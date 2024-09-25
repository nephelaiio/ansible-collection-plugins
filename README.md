# Ansible Collection - nephelaiio.plugins

[![Build Status](https://github.com/nephelaiio/ansible-collection-plugins/actions/workflows/pytest.yml/badge.svg)](https://github.com/nephelaiio/ansible-collection-plugins/actions/wofklows/molecule.yml)
[![Ansible Galaxy](http://img.shields.io/badge/ansible--galaxy-nephelaiio.plugins-blue.svg)](https://galaxy.ansible.com/ui/repo/published/nephelaiio/plugins/)

An [ansible collection](https://galaxy.ansible.com/ui/repo/published/nephelaiio/plugins/) for utility filters and tests

## Collection plugins

### Filters:

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

### Tests:
- test_network(record=None, net="0.0.0.0/0", prop="ansible_host"): Tests if an IP address in a given record falls within a specified network range.
- test_property(record=None, regex=".*", prop=""): Tests if the value of a specified property in a given record matches a regular expression.

## Testing

Role is tested using molecule through Github Actions on Ubuntu latest. You can test the collection directly from sources using command `make test`

## License

This project is licensed under the terms of the [MIT License](/LICENSE)
