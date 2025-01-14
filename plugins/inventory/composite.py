import os
from collections.abc import MutableMapping

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils.common.text.converters import to_native, to_text
from ansible.module_utils.six import string_types
from ansible.plugins.inventory import BaseFileInventoryPlugin
from ansible.utils.path import basedir
from ansible.utils.vars import combine_vars

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

GROUP_VARS = "group_vars"
HOST_VARS = "host_vars"
NONE_TYPE = type(None)
DICT_TYPES = (MutableMapping, NONE_TYPE)
CANONICAL_PATHS: dict[str, str] = {}
FOUND: dict[str, list[str]] = {}
NAK: set[str] = set()
PATH_CACHE: dict[tuple[str, str], str] = {}


class InventoryModule(BaseFileInventoryPlugin):
    """Build a composite inventory from the union of multiple yaml inventories"""

    NAME = "composite"

    def __init__(self):
        super(InventoryModule, self).__init__()

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            _, file_ext = os.path.splitext(path)
            if file_ext in ["", ".yml", ".yaml"]:
                valid = True
        return valid

    def load_file(self, path):
        return self.loader.load_from_file(path)

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        self._read_config_data(path)

        try:
            data = self.load_file(path)
        except Exception as e:
            raise AnsibleParserError(e)

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
        for inventory in inventories:
            if not isinstance(data, MutableMapping):
                msg = f"YAML inventory has invalid structure, it should be a dictionary, got: {type(inventory)}"
                raise AnsibleParserError(msg)
            if not inventory.get("file"):
                msg = f'Inventory "{to_text(inventory)}" does not contain "file" key'
                raise AnsibleParserError(msg)
            if not inventory.get("prefix"):
                msg = f'Inventory "{to_text(inventory)}" does not contain "prefix" key'
                raise AnsibleParserError(msg)
            config_file = os.path.realpath(path)
            inventory_dir = basedir(config_file)
            inventory_file = os.path.join(inventory_dir, inventory.get("file"))
            _, inventory_ext = os.path.splitext(inventory_file)
            if inventory_ext not in [".yaml", ".yml"]:
                msg = f'File "{inventory_file}" is not a valid YAML file'
                raise AnsibleParserError(msg)
            if not os.path.exists(inventory_file):
                msg = f'File "{inventory_file}" does not exist'
                raise AnsibleParserError(msg)
            inventory_prefix = inventory.get("prefix")
            self._parse_inventory(inventory_file, inventory_prefix)

    def _prefixed_group_name(self, group_name, prefix):
        if not prefix:
            return group_name
        else:
            return f"{prefix}_{group_name}"

    def _parse_inventory(self, path, prefix):
        """parses the inventory file"""

        msg = f"Loading inventory file {path} with prefix {prefix}"
        self.display.warning(msg)
        try:
            data = self.load_file(path)
        except Exception as e:
            raise AnsibleParserError(f"Error loading inventory file {path}\n\n{e}")
        if not data:
            raise AnsibleParserError("Parsed empty YAML file")
        elif not isinstance(data, MutableMapping):
            msg = f"YAML inventory has invalid structure, it should be a dictionary, got: {type(data)}"
            raise AnsibleParserError(msg)
        elif data.get("plugin"):
            msg = "Plugin configuration YAML file, not YAML inventory"
            raise AnsibleParserError(msg)

        if isinstance(data, MutableMapping):
            self._parse_group(prefix, data["all"], "")
            for group_name in data:
                if not prefix:
                    raise AnsibleParserError("Inventory prefix is required")
                if group_name == prefix:
                    msg = f"Group name {group_name} conflicts with prefix {prefix}"
                    raise AnsibleParserError(msg)
                if group_name == "all":
                    continue
                else:
                    prefixed_group = self._prefixed_group_name(group_name, prefix)
                    group_children = {"children": {prefixed_group: None}}
                    self._parse_group(group_name, group_children, "")
                    self._parse_group(prefixed_group, data[group_name], prefix)
        else:
            msg = f"Invalid data from file, expected dictionary and got:\n\n{to_native(data)}"
            raise AnsibleParserError(msg)

        group_var_data = self.load_group_vars(self.loader, basedir(path))
        for group in group_var_data:
            group_name = group
            group_vars = group_var_data[group]
            if group_name == "all":
                group_name = prefix
            else:
                group_name = f"{prefix}_{group_name}"
            for var in group_vars:
                self.display.vvv(f"Loading variable {var}")
                var_data = group_vars[var]
                self.inventory.set_variable(group_name, var, var_data)
        self.display.warning(f"Loaded vars {group_var_data} for group {group_name}")

    def _parse_group(self, group_name, vars_data, prefix):
        """parses a group from the inventory file"""
        group = group_name
        if isinstance(vars_data, DICT_TYPES):  # type: ignore[misc]
            try:
                group = self.inventory.add_group(group)
            except AnsibleError as e:
                msg = f"Unable to add group {group}: {to_text(e)}"
                raise AnsibleParserError(msg)

            if vars_data is not None:
                # make sure they are dicts
                for section in ["vars", "children", "hosts"]:
                    if section in vars_data:
                        # convert strings to dicts as these are allowed
                        if isinstance(vars_data[section], string_types):
                            vars_data[section] = {to_text(vars_data[section]): None}

                        if not isinstance(vars_data[section], DICT_TYPES):
                            msg = f"Invalid {section} entry for {group} group, requires a dictionary, found {type(vars_data[section])} instead."
                            raise AnsibleParserError(msg)

                for section in vars_data:
                    if not isinstance(vars_data[section], DICT_TYPES):  # type: ignore[misc]
                        msg = f"Skipping key {section} in group {group} as it is not a mapping, it is a {type(vars_data[section])}"
                        self.display.warning(msg)
                        continue

                    if isinstance(vars_data[section], NONE_TYPE):  # type: ignore[misc]
                        msg = f"Skipping empty key {section} in group {group}"
                        self.display.vvv(msg)
                    elif section == "vars":
                        for var in vars_data[section]:
                            vars_value = vars_data[section][var]
                            self.inventory.set_variable(group, var, vars_value)
                    elif section == "children":
                        for subgroup in vars_data[section]:
                            self.display.vvv(f"Loading subgroup {subgroup}")
                            child_data = vars_data[section][subgroup]
                            prefixed = self._prefixed_group_name(subgroup, prefix)
                            subgroup = self._parse_group(prefixed, child_data, prefix)
                            self.inventory.add_child(group, subgroup)
                    elif section == "hosts":
                        for host_pattern in vars_data[section]:
                            hosts_data = vars_data[section][host_pattern] or {}
                            hosts, port = self._parse_host(host_pattern)
                            self._populate_host_vars(hosts, hosts_data, group, port)
                    else:
                        msg = f"Skipping unexpected key {section} in group {group}, only 'vars', 'children' and 'hosts' are valid"
                        self.display.warning(msg)

        else:
            msg = f"Skipping {group} as this is not a valid group definition"
            self.display.warning(msg)

        return group

    def _parse_host(self, host_pattern):
        """
        Each host key can be a pattern, try to process it and add variables as needed
        """
        try:
            (hostnames, port) = self._expand_hostpattern(host_pattern)
        except TypeError:
            raise AnsibleParserError(
                f"Host pattern {host_pattern} must be a string. Enclose integers/floats in quotation marks."
            )
        return hostnames, port

    def load_found_files(self, data, found_files):
        data = {}
        self.display.vvv(f"Loading found files {found_files}")
        for found in found_files:
            new_data = self.load_file(found)

            if new_data:  # ignore empty files
                data = combine_vars(data, new_data)
        self.display.vvv(f"Read {data} from {found}")
        return data

    def load_group_vars(self, loader, path):
        """parses the inventory file"""
        group_vars = {}
        group_vars_basedir = os.path.join(path, GROUP_VARS)

        self.display.vvv(f"Loading vars files from {group_vars_basedir}")
        if not os.path.exists(group_vars_basedir):
            return {}
        try:
            for group in os.listdir(group_vars_basedir):
                group_path = os.path.join(group_vars_basedir, group)
                group_name, _ = os.path.splitext(group)
                if os.path.isdir(group_path):
                    self.display.vvv(f"Processing dir {group_path}")
                    found_files = loader.find_vars_files(group_path, "")
                elif os.path.isfile(group_path):
                    self.display.vvv(f"Processing file {group_path}")
                    found_files = [group_path]
                else:
                    raise AnsibleError(f"Invalid group_vars path {group_path}")
                data = self.load_found_files({}, found_files)
                self.display.vvv(f"Loaded data {data}")
                group_vars[group_name] = data
            return group_vars
        except Exception as e:
            raise AnsibleParserError(to_native(e))
