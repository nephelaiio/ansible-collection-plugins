# pylint: disable=line-too-long
"""
This module provides a collection of utility functions for various operations such as manipulating dictionaries,
string formatting, processing network records, and data transformation.

Functions:
- is_hash(d): Checks if the given object has a callable 'get' attribute.
- merge_dicts(x, y): Merges two dictionaries, with values from the second dictionary overwriting those from the first.
- merge_dicts_reverse(x, y): Merges two dictionaries in reverse order, giving priority to the first dictionary.
- filename(basename): Extracts the filename (without extension) from a full file name.
- map_format(value, pattern): Applies Python string formatting on an object, especially useful for dynamic string construction.
- map_values(d): Extracts values from a dictionary and returns them as a list.
- reverse_record(record): Reverses IP address and hostname in a record for reverse DNS lookup.
- with_ext(basename, ext): Appends an extension to a given basename.
- zone_fwd(zone, servers): Creates a DNS forward zone configuration.
- head(x): Returns the first element of a sequence.
- tail(x): Returns all but the first element of a sequence.
- split_with(x, d): Splits a string by the specified delimiter.
- join_with(x, d): Joins a list of strings using a specified delimiter.
- alias_keys(d, alias): Creates a new dictionary with keys renamed according to the provided alias mapping.
- map_attributes(d, atts): Maps selected attributes from a dictionary into a new list.
- select_attributes(d, atts): Selects specific attributes from a dictionary to create a new one.
- drop_attributes(d, x): Removes specified attributes from a dictionary.
- to_dict(x, key): Converts a sequence or a value into a dictionary.
- merge_item(item, key_attr): Merges an item's attributes into a dictionary.
- key_item(item, key_attr, remove_key): Converts an item into a key-value pair, optionally removing the key attribute.
- dict_to_list(d, key_attr): Converts a dictionary into a list of merged items.
- list_to_dict(l, key_attr, remove_key): Converts a list into a dictionary, keying items by specified attributes.
- to_kv(d, sep, prefix): Converts a nested dictionary or list into a flat key-value pair representation.
- to_safe_yaml(ds, indent): Converts a data structure into a YAML string representation.
- sorted_get(d, ks): Retrieves the value for the first key found in a list of keys from a dictionary.
- ip_range(spec): Generates a list of IP addresses within a specified range.
- map_flatten(o, env): Flattens a nested dictionary or list into a single-level dictionary with compound keys.
- map_join(d, atts, sep): Joins selected attributes from a dictionary into a single string.
- merge_join(d, attr, atts, sep): Merges selected attributes into a single string and adds it to the dictionary.
- map_group(l, key_atts, group_att): Groups a list of dictionaries by specified key attributes.
- is_any_true(xs): Returns True if any element in the provided iterable is truthy.
- is_all_true(xs): Returns True if all elements in the provided iterable are truthy.
- search_regex(r, s): Checks if a string matches a given regex pattern.

These functions are designed to assist in data manipulation and processing tasks, particularly useful in contexts
where data structures need to be dynamically created, modified, or converted between different formats.
"""
# pylint: enable=line-too-long

import copy
import itertools
import sys
import functools
import re
import netaddr
import yaml

from markupsafe import soft_str

if sys.version_info[0] < 3:
    from collections import Sequence, defaultdict  # pylint: disable=deprecated-class
else:
    from collections.abc import Sequence
    from collections import defaultdict


def is_hash(d):
    """
    Check if a given object is isomorphic to a dictionary.

    Args:
    d (Any): The object to check.

    Returns:
    bool: True if 'd' has a callable 'get' attribute, False otherwise.
    """

    return callable(getattr(d, "get", None))


def merge_dicts(x, y):
    """
    Merge two dictionaries.
    If there are overlapping keys, the values from the second dictionary will be used.

    Args:
    x (dict): The first dictionary.
    y (dict): The second dictionary.

    Returns:
    dict: A new dictionary containing the merged key-value pairs.
    """

    z = x.copy()
    z.update(y)
    return z


def merge_dicts_reverse(x, y):
    """
    Merge two dictionaries in reverse order.
    The values from the first dictionary will overwrite those from the second.

    Args:
    x (dict): The first dictionary.
    y (dict): The second dictionary.

    Returns:
    dict: A new dictionary with merged key-value pairs, prioritizing 'x' over 'y'.
    """

    return merge_dicts(y, x)  # pylint: disable=arguments-out-of-order


def filename(basename):
    """
    Extracts the filename (excluding extension) from a given basename.

    Args:
    basename (str): The basename, typically including the file extension.

    Returns:
    str: The filename without the extension.
    """

    return basename.split(".")[0]


def map_format(value, pattern):
    """
    Apply python string formatting on an object:
    .. sourcecode:: jinja
        {{ "%s - %s"|format("Hello?", "Foo!") }}
            -> Hello? - Foo!
    """
    if is_hash(value) and is_hash(pattern):

        def constant_factory(value):
            return lambda: value

        p = defaultdict(constant_factory("%s"))
        p.update(pattern)
        result = {k: map_format(v, p[k]) for k, v in value.items()}
    else:
        try:
            result = soft_str(pattern) % value
        except TypeError:
            result = pattern
    return result


def map_values(d):
    """
    Extract the values from a dictionary and return them as a list.

    Args:
    d (dict): The dictionary from which to extract values.

    Returns:
    list: A list containing all the values from the dictionary.
    """

    return list(d.values())


def reverse_record(record):
    """
    Reverses the IP address and hostname in a record, formatting the IP address for reverse DNS lookup.

    Args:
    record (dict): A dictionary containing 'ip-address' and 'host' keys.

    Returns:
    dict: A new dictionary with reversed 'ip-address' and 'host', and a 'type' key set to "PTR".
    """

    def reverse_address(addr):
        rev = ".".join(addr.split(".")[::-1])
        return f"{rev}.in-addr.arpa"

    return {
        "host": reverse_address(record["ip-address"]),
        "ip-address": record["host"],
        "type": "PTR",
    }


def with_ext(basename, ext):
    """
    Appends an extension to a given basename.

    Args:
    basename (str): The initial basename.
    ext (str): The extension to append.

    Returns:
    str: The basename with the appended extension.
    """

    return f"{filename(basename)}.{ext}"


def zone_fwd(zone, servers):
    """
    Creates a DNS forward zone configuration.

    Args:
    zone (str): The DNS zone name.
    servers (list): A list of server addresses for forwarding.

    Returns:
    dict: A dictionary representing the forward zone configuration.
    """

    return {
        f'zone "{zone}" IN': {
            "type": "forward",
            "forward": "only",
            "forwarders": servers,
        }
    }


def head(x):
    """
    Returns the first element of a sequence.

    Args:
    x (list/tuple/str): The sequence from which to extract the first element.

    Returns:
    Any: The first element of the sequence.
    """

    return x[0]


def tail(x):
    """
    Returns all but the first element of a sequence.

    Args:
    x (list/tuple/str): The sequence from which to extract elements.

    Returns:
    list/tuple/str: A sequence of all but the first element.
    """
    return x[1::]


def split_with(x, d):
    """
    Splits a string by the specified delimiter.

    Args:
    x (str): The string to split.
    d (str): The delimiter to use for splitting.

    Returns:
    list: A list of substrings.
    """

    return x.split(d)


def join_with(x, d):
    """
    Joins a list of strings using a specified delimiter.

    Args:
    x (list): The list of strings to join.
    d (str): The delimiter to use for joining.

    Returns:
    str: The joined string.
    """

    return d.join(x)


def alias_keys(d, alias=None):
    """
    Creates a new dictionary with keys renamed as per the alias mapping.

    Args:
    d (dict): The original dictionary
    """

    new_dict = copy.deepcopy(d)
    _alias = alias or {}
    for k, v in list(_alias.items()):
        new_dict[v] = new_dict[k]
    return new_dict


def map_attributes(d, atts):
    """
    Extracts values from the input dictionary (d) for the keys listed in atts.

    Args:
    d (dict): The dictionary from which to extract values.
    atts (list): A list of keys for which to extract values from the dictionary.

    Returns:
    list: A list of values corresponding to the keys in atts found in d.
    """

    new_array = []
    for k in atts:
        if k in d:
            new_array = new_array + [d[k]]
    return new_array


def select_attributes(d, atts):
    """
    Creates a new dictionary containing only the key-value pairs from the input dictionary (d)
    where the keys are specified in atts.

    Args:
    d (dict): The original dictionary to select key-value pairs from.
    atts (list): A list of keys to include in the new dictionary.

    Returns:
    dict: A new dictionary containing only the selected key-value pairs.
    """

    new_dict = {}
    for k, _ in list(d.items()):
        if k in atts:
            new_dict[k] = d[k]
    return new_dict


def drop_attributes(d, x):
    """
    Returns a new dictionary with specified keys removed from the input dictionary (d).

    Args:
    d (dict): The original dictionary to remove key-value pairs from.
    x (list): A list of keys to be removed from the dictionary.

    Returns:
    dict: A new dictionary with the specified keys removed.
    """

    new_dict = copy.deepcopy(d)
    for y in list(itertools.chain.from_iterable([x])):
        if y in d:
            del new_dict[y]
    return new_dict


def to_dict(x, key=None):
    """
    Converts the input into a dictionary. If a key function or mapping is provided,
    it applies the transformation as specified by the key.

    Args:
    x (Any): The input to be converted into a dictionary.
    key (function or dict, optional): A function or a dictionary defining how to transform
        the input into key-value pairs. If None, the input is converted directly into a dictionary.

    Returns:
    dict: The resulting dictionary after applying the key transformation, if provided.
    """

    if key is None:
        result = dict(x)
    else:
        if is_hash(key):
            result = {map_format(x, k): map_format(x, v) for k, v in key.items()}
        else:
            result = {key: x}
    return result


def merge_item(item, key_attr):
    """
    Merges a tuple of two items (a key-value pair) into a single dictionary,
    using a specified attribute for key transformation.

    Args:
        item (tuple): A tuple containing two elements, where the first element is transformed based on `key
    """

    return dict(merge_dicts(item[1], to_dict(item[0], key_attr)))


def key_item(item, key_attr, remove_key=True):
    """
    Extracts a value from the given item using a specified key or nested keys, and returns
    this value along with a modified copy of the original item.

    Parameters:
    - item (dict or similar): The item from which to extract the value. It should be a
      dictionary or a dictionary-like object.
    - key_attr (int, float, str, bool, list, tuple): The key or nested keys used to extract
      the value from the item. If it's a list or tuple, it is treated as nested keys.
    - remove_key (bool, optional): If True, the key is removed from the copied item.
      Default is True. Note: This option is not applicable for nested keys.

    Returns:
    - list: A list containing two elements:
        1. The value extracted from the item using the key(s).
        2. A deep copy of the item, potentially with the key removed.

    Raises:
    - ValueError: If 'remove_key' is True for nested attributes or if 'key_attr' is
      neither a scalar nor a list/tuple.

    Example:
    >>> item = {'a': {'b': 2}}
    >>> key_item(item, ['a', 'b'], False)
    [2, {'a': {'b': 2}}]

    >>> key_item(item, 'a')
    [{'b': 2}, {}]

    Note:
    - The function assumes that the nested keys correctly point to a value in the item.
    """

    new_item = copy.deepcopy(item)
    if isinstance(key_attr, (list, tuple)):
        if remove_key:
            raise ValueError("remove_key must be False for nested attributes")
        _nested_attr = functools.reduce(lambda x, k: x[k], key_attr, item)
        return [_nested_attr, new_item]
    if isinstance(key_attr, (int, float, str, bool)):
        if remove_key:
            del new_item[key_attr]
        return [item[key_attr], new_item]
    raise ValueError("key_attr must be scalar or list")


def dict_to_list(d, key_attr):
    """
    Converts a dictionary into a list of merged items based on a specified key attribute.

    Args:
        d (dict): The dictionary to convert.
        key_attr: The key attribute to use for merging each item in the dictionary.

    Returns:
        list: A list where each element is a merged version of the key-value pairs from `d`, transformed by `key_attr`.
    """

    return [merge_item(item, key_attr) for item in d.items()]


def list_to_dict(l, key_attr, remove_key=True):
    """
    Converts a list of dictionaries into a dictionary by using a specified key attribute from each item.

    Args:
        l (list): A list of dictionaries to convert.
        key_attr: The attribute to use as the key for each dictionary in the resulting dictionary.
        remove_key (bool, optional): If True, removes `key_attr` from each dictionary in the list. Default is True.

    Returns:
        dict: A dictionary with keys derived from `key_attr` of each item in the list.
    """

    return dict([key_item(x, key_attr, remove_key) for x in l])


def to_kv(d, sep=".", prefix=""):
    """
    Recursively converts a nested dictionary or list into a flat list of key-value pairs with compound keys.

    Args:
        d (dict or list): The nested dictionary or list to flatten.
        sep (str, optional): The separator to use in compound keys. Default is '.'.
        prefix (str, optional): The prefix to prepend to each key. Default is an empty string.

    Returns:
        list: A flat list of dictionaries,
              each containing a 'key' and 'value' pair representing the flattened structure.
    """

    if is_hash(d):
        lvl = [
            to_kv(v, sep, (prefix != "" and (prefix + sep) or "") + k)
            for k, v in d.items()
        ]
        return list(itertools.chain.from_iterable(lvl))
    if isinstance(d, Sequence) and not isinstance(d, str):
        lvl = [
            to_kv(v, sep, (prefix != "" and (prefix + sep) or "") + str(i))
            for i, v in list(enumerate(d))
        ]
        return list(itertools.chain.from_iterable(lvl))
    return [{"key": prefix, "value": d}]


def to_safe_yaml(ds):
    """
    Converts a data structure into a YAML formatted string using safe dumping.

    Args:
        ds (dict or list): The data structure to convert into YAML.

    Returns:
        str: A YAML formatted string representing the input data structure.
    """

    return yaml.safe_dump(ds)


def sorted_get(d, ks):
    """
    Retrieves the value from a dictionary for the first key in a list of keys that exists in the dictionary.

    Args:
        d (dict): The dictionary to search in.
        ks (list): A list of keys to search for in the dictionary.

    Returns:
        The value corresponding to the first key found in `ks` that exists in `d`.

    Raises:
        KeyError: If none of the keys in `ks` are found in `d`.
    """

    for k in ks:
        if k in d:
            return d[k]
    raise KeyError(f"None of {ks} keys found")


def ip_range(spec):
    """
    Generates a list of IP addresses in the specified range.

    Args:
        spec (str): A string specifying the IP range in the format 'start-end' or just a single IP.

    Returns:
        list: A list of IP addresses within the specified range.
    """

    addrs = spec.split("-")
    start = addrs[0]
    end = start if len(addrs) == 1 else addrs[1]
    return [str(ip) for ip in netaddr.iter_iprange(start, end)]


def map_flatten(o, env=""):
    """
    Flattens a nested dictionary or list into a single-level dictionary with compound keys.

    Args:
        o (dict or list): The dictionary or list to flatten.
        env (str, optional): A string prefix to prepend to each key in the flattened dictionary. Defaults to an empty string.

    Returns:
        dict: A flattened dictionary with compound keys representing the nested structure.

    Raises:
        ValueError: If 'o' is not a dictionary when 'env' is an empty string.

    Note:
        The compound keys are formed by concatenating the keys of nested dictionaries, separated by '.'.
    """
    if env == "" and not isinstance(o, dict):
        raise ValueError("Argument must be dictionary")
    if isinstance(o, dict):
        flattened = {}
        for k, v in o.items():
            if env == "":
                newenv = k
            else:
                newenv = f"{env}.{k}"
            if isinstance(v, (dict, list)):
                item = map_flatten(v, newenv)
            else:
                item = {newenv: v}
            flattened = {**flattened, **item}
        return flattened
    if isinstance(o, list):
        flattened = {}
        for i, j in enumerate(o):
            if env == "":
                newenv = f"{i}"
            else:
                newenv = f"{env}.{i}"
            if isinstance(j, (dict, list)):
                item = map_flatten(j, newenv)
            else:
                item = {newenv: j}
            flattened = {**flattened, **item}
        return flattened
    return o


def map_join(d, atts, sep=" "):
    """
    Joins selected attributes from a dictionary into a single string.

    Args:
        d (dict): The dictionary from which to extract values.
        atts (list): A list of keys whose corresponding values are to be joined.
        sep (str, optional): The separator to use between values. Defaults to a space.

    Returns:
        str: A single string made by joining the values of the specified keys in the dictionary.
    """

    return sep.join([str(x) for x in map_attributes(d, atts)])


def merge_join(d, attr, atts, sep=" "):
    """
    Merges selected attributes into a single string and adds it to the dictionary.

    Args:
        d (dict): The dictionary to work with.
        attr (str): The attribute under which the merged string will be added to the dictionary.
        atts (list): A list of keys whose corresponding values are to be merged.
        sep (str, optional): The separator to use between values in the merged string. Defaults to a space.

    Returns:
        dict: The original dictionary with the merged string added under the specified attribute.
    """

    item = {
        attr: map_join(d, atts, sep),
    }
    return {**d, **item}


def map_group(l, key_atts, group_att=None):
    """
    Groups a list of dictionaries by specified key attributes.

    Args:
        l (list): A list of dictionaries to group.
        key_atts (list): A list of keys to group by.
        group_att (str, optional): The attribute to group the data under. Defaults to None, which uses 'data' as default.

    Returns:
        list: A list of dictionaries, each representing a group of items from the original list.
    """

    data_field = group_att or "data"
    groups = {}
    for x in l:
        _key = tuple(map_attributes(x, key_atts))
        if _key in groups:
            cur_item = groups[_key]
            cur_data = cur_item[data_field]
        else:
            cur_item = {}
            cur_data = []
        group_atts = select_attributes(x, key_atts)
        if group_att is None:
            groups[_key] = {
                **cur_item,
                **group_atts,
                **{data_field: cur_data + [drop_attributes(x, key_atts)]},
            }
        else:
            if group_att in x:
                groups[_key] = {
                    **cur_item,
                    **group_atts,
                    **{data_field: cur_data + [x[group_att]]},
                }
    return list(groups.values())


def is_any_true(xs):
    """
    Checks if any element in the provided iterable is true.

    Args:
        xs (iterable): An iterable to check for truthiness.

    Returns:
        bool: True if any element in the iterable is true, False otherwise.
    """

    return functools.reduce(lambda x, y: x or y, map(lambda x: bool(x), xs), False)  # pylint: disable=unnecessary-lambda


def is_all_true(xs):
    """
    Checks if all elements in the provided iterable are true.

    Args:
        xs (iterable): An iterable to check for truthiness.

    Returns:
        bool: True if all elements in the iterable are true, False otherwise.

    Note:
        This function uses a lambda function in conjunction with functools.reduce for evaluation.
    """

    return functools.reduce(lambda x, y: x and y, map(lambda x: bool(x), xs), True)  # pylint: disable=unnecessary-lambda


def search_regex(r, s):
    """
    Checks if a string matches a given regular expression.

    Args:
        r (str): The regular expression pattern to match against.
        s (str): The string to search for a match.

    Returns:
        bool: True if the string matches the regular expression pattern, False otherwise.
    """

    return bool(re.match(r, s))


class FilterModule():
    """
    A class encapsulating a collection of jinja2 filters.

    This class serves as a container for various utility functions which can be used as filters in jinja2 templates.
    It provides a convenient way to access and apply these filters for transforming or manipulating data within templates.

    Methods:
        filters(): Returns a dictionary mapping filter names to their corresponding functions.
    """

    def filters(self):
        """
        Retrieves a dictionary of jinja2 filter functions.

        This method returns a dictionary where each key is the name of a filter (as used in jinja2 templates), and
        its corresponding value is a function that implements the filter's functionality.

        Returns:
            dict: A dictionary mapping filter names to their respective functions. Includes filters for string
                  manipulation, data structure transformation, and various other utilities.

        Filters:
            - split_with: Splits a string by a given delimiter.
            - join_with: Joins a list of strings using a specified delimiter.
            - head: Retrieves the first element of a sequence.
            - tail: Retrieves all but the first element of a sequence.
            - map_format: Applies Python string formatting on an object.
            - map_values: Extracts the values from a dictionary.
            - reverse_record: Reverses IP address and hostname in a record for reverse DNS lookup.
            - zone_fwd: Creates a DNS forward zone configuration.
            - alias_keys: Renames keys in a dictionary based on a mapping.
            - merge_dicts: Merges two dictionaries.
            - map_attributes: Extracts a list of values from a dictionary based on specified keys.
            - drop_attributes: Removes specified keys from a dictionary.
            - select_attributes: Creates a new dictionary with selected key-value pairs.
            - merge_dicts_reverse: Merges two dictionaries in reverse order.
            - to_dict: Converts a sequence or a value into a dictionary.
            - merge_item: Merges an item's attributes into a dictionary.
            - key_item: Converts an item into a key-value pair.
            - dict_to_list: Converts a dictionary into a list of merged items.
            - list_to_dict: Converts a list into a dictionary.
            - to_kv: Converts a nested dictionary or list into a flat key-value pair representation.
            - to_safe_yaml: Converts a data structure into a YAML string.
            - sorted_get: Retrieves the value for the first key found in a list of keys.
            - ip_range: Generates a list of IP addresses within a specified range.
            - map_flatten: Flattens a nested dictionary or list.
            - map_join: Joins selected attributes from a dictionary into a string.
            - merge_join: Merges selected attributes into a string and adds it to a dictionary.
            - map_group: Groups a list of dictionaries by specified key attributes.
            - is_any_true: Checks if any element in an iterable is true.
            - is_all_true: Checks if all elements in an iterable are true.
            - search_regex: Checks if a string matches a given regex pattern.
        """

        return {
            "split_with": split_with,
            "join_with": join_with,
            "head": head,
            "tail": tail,
            "map_format": map_format,
            "map_values": map_values,
            "reverse_record": reverse_record,
            "zone_fwd": zone_fwd,
            "alias_keys": alias_keys,
            "merge_dicts": merge_dicts,
            "map_attributes": map_attributes,
            "drop_attributes": drop_attributes,
            "select_attributes": select_attributes,
            "merge_dicts_reverse": merge_dicts_reverse,
            "to_dict": to_dict,
            "merge_item": merge_item,
            "key_item": key_item,
            "dict_to_list": dict_to_list,
            "list_to_dict": list_to_dict,
            "to_kv": to_kv,
            "to_safe_yaml": to_safe_yaml,
            "sorted_get": sorted_get,
            "ip_range": ip_range,
            "map_flatten": map_flatten,
            "map_join": map_join,
            "merge_join": merge_join,
            "map_group": map_group,
            "is_any_true": is_any_true,
            "is_all_true": is_all_true,
            "search_regex": search_regex,
        }
