"""
Custom composite inventory plugin
"""

import os
from collections.abc import MutableMapping

from ansible.errors import AnsibleParserError
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.text.converters import to_text
from ansible.plugins.inventory import BaseFileInventoryPlugin
from ansible.utils.path import basedir
from ansible.vars.plugins import get_vars_from_path

DOCUMENTATION = """
    name: composite_inventory
    plugin_type: inventory
    short_description: A composition plugin for multiple yaml invetories
    description: Build a composite inventory from the union of multiple yaml inventories
    options:
        plugin:
            description: Name of the plugin
            required: true
            choices: ['nephelaiio.plugins.composite']
"""

NoneType = type(None)

GROUP_VARS = "group_vars"
HOST_VARS = "host_vars"
DICT_TYPES = (MutableMapping, NoneType)
CANONICAL_PATHS: dict[str, str] = {}
FOUND: dict[str, list[str]] = {}
NAK: set[str] = set()
PATH_CACHE: dict[tuple[str, str], str] = {}


class InventoryModule(BaseFileInventoryPlugin):
    """Build a composite inventory from the union of multiple yaml inventories"""

    NAME = "composite"

    def _prefixed_group_name(self, group_name, prefix):
        if not prefix:
            return group_name
        return f"{prefix}_{group_name}"

    def verify_file(self, path):
        valid = False
        if super().verify_file(path):
            _, file_ext = os.path.splitext(path)
            if file_ext in ["", ".yml", ".yaml"]:
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache)
        self._read_config_data(path)

        try:
            data = self.loader.load_from_file(path)
        except Exception as e:
            raise AnsibleParserError(e) from e

        path_dir = basedir(path)
        group_vars_dir = os.path.join(path_dir, GROUP_VARS)
        host_vars_dir = os.path.join(path_dir, HOST_VARS)

        if not data:
            msg = f'Parsed empty YAML file "{to_text(path)}"'
            raise AnsibleParserError(msg)
        if not data.get("inventories"):
            msg = f'Parsed file "{to_text(path)}" does not contain "inventories" key'
            raise AnsibleParserError(msg)
        if os.path.exists(group_vars_dir):
            msg = f"Directory {group_vars_dir} exists, group_vars should be defined in child inventories"
            raise AnsibleParserError(msg)
        if os.path.exists(host_vars_dir):
            msg = f"Directory {host_vars_dir} exists, host_vars should be defined in child inventories"
            raise AnsibleParserError(msg)

        inventories = data.get("inventories")
        if not inventories or len(inventories) == 0:
            msg = f'Parsed file "{to_text(path)}" does not contain any inventories'
            raise AnsibleParserError(msg)
        for subinventory in inventories:
            _subinventory = to_text(subinventory)
            if not isinstance(data, MutableMapping):
                msg = f"YAML inventory has invalid structure, it should be a dictionary, got: {type(subinventory)}"
                raise AnsibleParserError(msg)
            if not subinventory.get("file"):
                msg = f'Inventory "{_subinventory}" does not contain "file" key'
                raise AnsibleParserError(msg)
            if not subinventory.get("prefix"):
                msg = f'Inventory "{_subinventory}" does not contain "prefix" key'
                raise AnsibleParserError(msg)
            source = os.path.realpath(subinventory.get("file"))
            if not os.path.exists(source):
                msg = f'File "{source}" does not exist'
                raise AnsibleParserError(msg)
            prefix = subinventory.get("prefix")
            manager = InventoryManager(loader=loader, sources=[source])
            manager.parse_sources()
            groups = manager.get_groups_dict()
            for group_name in groups:
                if group_name == "ungrouped":
                    continue
                if group_name == prefix:
                    msg = f"Group name {group_name} conflicts with prefix {prefix}"
                    raise AnsibleParserError(msg)
                if group_name == "all":
                    prefix_group = prefix
                else:
                    prefix_group = self._prefixed_group_name(group_name, prefix)
                self.inventory.add_group(group_name)
                self.inventory.add_group(prefix_group)
                self.inventory.add_child(group_name, prefix_group)
                # load group_vars from inventory sources
                group = manager.groups[group_name]
                group_vars = group.vars
                for var_name in group_vars:
                    var_value = group_vars[var_name]
                    msg = f"Registered var {var_name} for group {prefix_group}"
                    self.display.warning(msg)
                    self.inventory.set_variable(prefix_group, var_name, var_value)
                # load group_vars from group_vars directory
                group_vars = get_vars_from_path(loader, source, group, "task")
                for var_name in group_vars:
                    var_value = group_vars[var_name]
                    msg = f"Registered var {var_name} for group {prefix_group}"
                    self.display.warning(msg)
                    self.inventory.set_variable(prefix_group, var_name, var_value)
                # register host
                for host_name in groups[group_name]:
                    host = manager.get_host(host_name)
                    self.inventory.add_host(host_name, prefix_group)
                    msg = f"Registered host {host_name} for group {group_name}"
                    self.display.warning(msg)
                    # load host_vars from inventory sources
                    host_vars = host.vars
                    for var_name in host_vars:
                        msg = f"Registered var {var_name} for host {host_name}"
                        var_value = host.vars[var_name]
                        self.inventory.set_variable(host_name, var_name, var_value)
                    # load host_vars from host_vars directory
                    group_vars = get_vars_from_path(loader, source, host, "task")
                    for var_name in host_vars:
                        msg = f"Registered var {var_name} for host {host_name}"
                        var_value = host.vars[var_name]
                        self.inventory.set_variable(host_name, var_name, var_value)
