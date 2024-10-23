import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "plugins", "filter"))

print(sys.path)

from custom_filter import dict_to_list  # noqa: E402
from custom_filter import (
    alias_keys,
    drop_attributes,
    filename,
    ip_range,
    is_all_true,
    is_any_true,
    is_hash,
    key_item,
    list_to_dict,
    map_attributes,
    map_flatten,
    map_format,
    map_group,
    map_join,
    map_values,
    merge_dicts,
    merge_dicts_reverse,
    merge_item,
    merge_join,
    reverse_record,
    search_regex,
    select_attributes,
    set_difference,
    sorted_get,
    to_dict,
    to_kv,
    to_safe_yaml,
    with_ext,
)


def test_is_hash():
    assert is_hash({}) is True
    assert is_hash({}) is True
    assert is_hash("") is False
    assert is_hash([]) is False


def test_reverse_record():
    host = "test.com"
    address = "10.0.0.1"
    r = {"host": host, "ip-address": address}
    rr = reverse_record(r)
    assert rr["ip-address"] == host
    assert rr["host"] == "1.0.0.10.in-addr.arpa"
    assert rr["type"] == "PTR"


def test_filename():
    assert filename("basename.ext") == "basename"
    assert filename("basename.ext1.ext2") == "basename"
    assert filename("basename") == "basename"


def test_with_ext():
    assert with_ext("basename.ext", "newext") == "basename.newext"
    assert with_ext("basename.ext1.ext2", "newext") == "basename.newext"
    assert with_ext("basename", "newext") == "basename.newext"


def test_alias_keys():
    assert alias_keys({}, {}) == {}
    assert alias_keys({"a": 1}, {"a": "b"}) == {"a": 1, "b": 1}
    assert alias_keys({"a": 1, "b": 2}, {"a": "c", "b": "d"}) == {
        "a": 1,
        "b": 2,
        "c": 1,
        "d": 2,
    }
    assert alias_keys({"a": 1}, {"a": "b", "b": "c"}) == {"a": 1, "b": 1, "c": 1}


def test_merge_dicts():
    assert merge_dicts({}, {}) == {}
    assert merge_dicts({"a": "0"}, {"a": "1"}) == {"a": "1"}
    assert merge_dicts({"a": "0", "b": "1"}, {"a": "2", "b": "3"}) == {
        "a": "2",
        "b": "3",
    }
    assert merge_dicts({"a": "0"}, {"a": "1", "b": "2"}) == {"a": "1", "b": "2"}
    assert merge_dicts({"a": "0", "b": "1"}, {"a": "2"}) == {"a": "2", "b": "1"}


def test_merge_dicts_reverse():
    assert merge_dicts_reverse({}, {}) == {}
    assert merge_dicts_reverse({"a": "0"}, {"a": "1"}) == {"a": "0"}
    assert merge_dicts_reverse({"a": "0", "b": "1"}, {"a": "2", "b": "3"}) == {
        "a": "0",
        "b": "1",
    }
    assert merge_dicts_reverse({"a": "0"}, {"a": "1", "b": "2"}) == {"a": "0", "b": "2"}
    assert merge_dicts_reverse({"a": "0", "b": "1"}, {"a": "2"}) == {"a": "0", "b": "1"}


def test_map_attributes():
    assert map_attributes({"a": "0", "b": "1"}, ["a"]) == ["0"]
    assert map_attributes({"a": "0", "b": "1"}, []) == []
    assert map_attributes({"a": "0", "b": "1"}, ["c"]) == []
    assert map_attributes({"a": "0", "b": "1"}, ["a", "b"]) == ["0", "1"]
    assert map_attributes({"a": "0", "b": "1"}, ["b", "a"]) == ["1", "0"]
    assert map_attributes({"a": "0"}, ["a", "b"]) == ["0"]


def test_select_attributes():
    assert select_attributes({"a": "0", "b": "1"}, ["a"]) == {"a": "0"}
    assert select_attributes({"a": "0", "b": "1"}, []) == {}
    assert select_attributes({"a": "0", "b": "1"}, ["a", "b"]) == {"a": "0", "b": "1"}
    assert select_attributes({"a": "0"}, ["a", "b"]) == {"a": "0"}


def test_drop_attributes():
    assert drop_attributes({"a": "0", "b": "1"}, ["a"]) == {"b": "1"}
    assert drop_attributes({"a": "0", "b": "1"}, []) == {"a": "0", "b": "1"}
    assert drop_attributes({"a": "0", "b": "1"}, ["a", "b"]) == {}
    assert drop_attributes({"a": "0"}, ["c"]) == {"a": "0"}


def test_to_dict():
    assert to_dict([["a", "b"]]) == {"a": "b"}
    assert to_dict({"a": "b"}, "c") == {"c": {"a": "b"}}
    assert to_dict(["a", "b"], "c") == {"c": ["a", "b"]}
    assert to_dict("a", {"a": "first", "b": "second"}) == {"a": "first", "b": "second"}
    assert to_dict("a", {"a": "first", "b": "%s"}) == {"a": "first", "b": "a"}
    assert to_dict("a", {"%s_1": "first", "%s_2": "%s"}) == {"a_1": "first", "a_2": "a"}
    assert to_dict("a", {"%s_1": "first", "%s_2": "%s"}) == {"a_1": "first", "a_2": "a"}


def test_map_format():
    assert map_format("", "%sx") == "x"
    assert map_format("a", "%sx") == "ax"
    assert map_format("a", "x%s") == "xa"
    assert map_format("a", "%s") == "a"
    assert map_format("a", "") == ""
    assert map_format({"a": "first"}, {"b": "x%s"}) == {"a": "first"}
    assert map_format({"a": "first"}, {"a": "x%s"}) == {"a": "xfirst"}
    assert map_format({"a": "first"}, {"a": "%sx"}) == {"a": "firstx"}
    assert map_format({"a": "first"}, {"a": "second"}) == {"a": "second"}


def test_map_values():
    assert map_values({"a": "first"}) == ["first"]
    assert map_values({"a": "first", "b": "second"}) == ["first", "second"]


def test_merge_item():
    d = {"a": "first"}
    assert merge_item(["second", d], "b") == {"a": "first", "b": "second"}
    assert merge_item(["second", {}], "b") == {"b": "second"}
    assert merge_item(["second", d], "a") == {"a": "second"}


def test_key_item():
    d = {"a": "first", "b": "second"}
    assert key_item(d, "a") == ["first", {"b": "second"}]
    assert key_item(d, "b") == ["second", {"a": "first"}]
    e = {"b": "second"}
    f = {"a": e}
    assert key_item(f, ["a", "b"], False) == ["second", f]
    assert key_item(f, ["a"], False) == [e, f]
    with pytest.raises(KeyError):
        key_item(d, ["na"], False)
    with pytest.raises(ValueError):
        key_item(d, ["na"])


def test_dict_to_list():
    d = {"a": {"content": "first"}, "b": {"content": "second"}}
    assert dict_to_list(d, "key") == [
        {"key": "a", "content": "first"},
        {"key": "b", "content": "second"},
    ]


def test_list_to_dict():
    d = {"a": {"content": "first"}, "b": {"content": "second"}}
    lx = dict_to_list(d, "key")
    assert list_to_dict(lx, "key") == d
    assert list_to_dict(lx, "key", False) == {
        "a": {"content": "first", "key": "a"},
        "b": {"content": "second", "key": "b"},
    }
    e = [
        {"a": {"b": "first"}},
        {"a": {"b": "second"}},
    ]
    assert list_to_dict(e, ["a", "b"], False) == {
        "first": {"a": {"b": "first"}},
        "second": {"a": {"b": "second"}},
    }
    with pytest.raises(KeyError):
        list_to_dict(e, ["a", "c"], False)
    with pytest.raises(ValueError):
        list_to_dict(e, ["a", "c"])


def test_to_kv():
    assert to_kv(1) == [{"key": "", "value": 1}]
    assert to_kv(["a"]) == [{"key": "0", "value": "a"}]
    assert to_kv(["a", "b"]) == [{"key": "0", "value": "a"}, {"key": "1", "value": "b"}]
    assert to_kv(1, prefix="base") == [{"key": "base", "value": 1}]
    assert to_kv("1", prefix="base") == [{"key": "base", "value": "1"}]
    assert to_kv(["a", "b"], prefix="base") == [
        {"key": "base.0", "value": "a"},
        {"key": "base.1", "value": "b"},
    ]
    assert to_kv({"a": 1}, prefix="") == [{"key": "a", "value": 1}]
    assert to_kv({"a": ["b", "c"]}) == [
        {"key": "a.0", "value": "b"},
        {"key": "a.1", "value": "c"},
    ]
    assert to_kv({"a": ["b", "c"]}, sep="") == [
        {"key": "a0", "value": "b"},
        {"key": "a1", "value": "c"},
    ]
    assert to_kv({"a": {"b": "c"}, "d": "e"}, prefix="") == [
        {"key": "a.b", "value": "c"},
        {"key": "d", "value": "e"},
    ]
    assert to_kv({"a": {"b": "c"}, "d": "e"}, sep="/", prefix="") == [
        {"key": "a/b", "value": "c"},
        {"key": "d", "value": "e"},
    ]
    assert to_kv({"a": {"b": {"c": "d"}, "e": "f"}, "g": "h"}, sep="/") == [
        {"key": "a/b/c", "value": "d"},
        {"key": "a/e", "value": "f"},
        {"key": "g", "value": "h"},
    ]
    assert to_kv({"a": {"b": "c"}, "d": ["e", "f"]}, prefix="") == [
        {"key": "a.b", "value": "c"},
        {"key": "d.0", "value": "e"},
        {"key": "d.1", "value": "f"},
    ]
    assert to_kv({"a": [{"b": "c", "d": "e"}, "h"]}, sep="/", prefix="") == [
        {"key": "a/0/b", "value": "c"},
        {"key": "a/0/d", "value": "e"},
        {"key": "a/1", "value": "h"},
    ]


def test_to_safe_yaml():
    assert to_safe_yaml([{"a": 0}, {"b": 1}]) == "- a: 0\n- b: 1\n"
    assert to_safe_yaml({"a": 0}) == "a: 0\n"
    assert to_safe_yaml({"a": [0, 1]}) == "a:\n- 0\n- 1\n"
    assert to_safe_yaml({"a": 0, "b": 1}) == "a: 0\nb: 1\n"


def test_sorted_get():
    d = {
        "ubuntu": "ubuntu",
        "ubuntu-focal": "ubuntu-focal",
        "centos": "centos",
        "default": "default",
    }
    assert sorted_get(d, ["default"]) == "default"
    assert sorted_get(d, ["centos"]) == "centos"
    assert sorted_get(d, ["centos", "default"]) == "centos"
    assert sorted_get(d, ["ubuntu-focal", "ubuntu"]) == "ubuntu-focal"
    assert sorted_get(d, ["ubuntu", "ubuntu-focal"]) == "ubuntu"
    assert sorted_get(d, ["centos", "ubuntu", "default"]) == "centos"
    assert sorted_get(d, ["ubuntu", "centos", "default"]) == "ubuntu"

    assert sorted_get(d, ["na", "default"]) == "default"
    assert sorted_get(d, ["na", "centos"]) == "centos"
    assert sorted_get(d, ["na", "centos", "default"]) == "centos"
    assert sorted_get(d, ["na", "ubuntu-focal", "ubuntu"]) == "ubuntu-focal"
    assert sorted_get(d, ["na", "ubuntu", "ubuntu-focal"]) == "ubuntu"
    assert sorted_get(d, ["na", "centos", "ubuntu", "default"]) == "centos"
    assert sorted_get(d, ["na", "ubuntu", "centos", "default"]) == "ubuntu"

    with pytest.raises(KeyError):
        sorted_get(d, ["na"])
    with pytest.raises(KeyError):
        sorted_get(d, ["na", "an"])


def test_iprange():
    assert ip_range("8.8.8.8") == ["8.8.8.8"]
    assert ip_range("8.8.8.8-8.8.8.10") == ["8.8.8.8", "8.8.8.9", "8.8.8.10"]


def test_map_flatten():
    assert map_flatten({"a": 1}) == {
        "a": 1,
    }
    assert map_flatten({"a": {"b": 1, "c": 2}}) == {
        "a.b": 1,
        "a.c": 2,
    }
    assert map_flatten({"a": ["b", "c"]}) == {
        "a.0": "b",
        "a.1": "c",
    }
    assert map_flatten({"a": [{"b": 1, "c": 2}, {"d": 3}], "e": ["f", "g"]}) == {
        "a.0.b": 1,
        "a.0.c": 2,
        "a.1.d": 3,
        "e.0": "f",
        "e.1": "g",
    }

    with pytest.raises(ValueError):
        map_flatten("a")

    with pytest.raises(ValueError):
        map_flatten(1)

    with pytest.raises(ValueError):
        map_flatten(["a", "b"])


def test_map_join():
    target = {
        "a": 1,
        "b": "hola",
        "c": 2,
        "d": "mundo",
        "e": "chamo",
    }

    assert map_join(target, ["a"]) == "1"
    assert map_join(target, ["b", "d"]) == "hola mundo"
    assert map_join(target, ["d", "b"]) == "mundo hola"
    assert map_join(target, ["b", "e"]) == "hola chamo"
    assert map_join(target, ["e", "b"]) == "chamo hola"

    assert map_join(target, ["a"], "") == "1"
    assert map_join(target, ["b", "d"], "") == "holamundo"
    assert map_join(target, ["d", "b"], "") == "mundohola"
    assert map_join(target, ["b", "e"], "") == "holachamo"
    assert map_join(target, ["e", "b"], "") == "chamohola"

    assert map_join(target, ["a"], ",") == "1"
    assert map_join(target, ["b", "d"], ",") == "hola,mundo"
    assert map_join(target, ["d", "b"], ",") == "mundo,hola"
    assert map_join(target, ["b", "e"], ",") == "hola,chamo"
    assert map_join(target, ["e", "b"], ",") == "chamo,hola"

    assert map_join(target, ["x"]) == ""


def test_merge_join():
    target = {
        "a": 1,
        "b": "hola",
        "c": 2,
        "d": "mundo",
        "e": "chamo",
        "join": "fail",
    }

    assert merge_join(target, "join", ["b", "d"]) == {
        **target,
        **{"join": "hola mundo"},
    }
    assert merge_join(target, "join", ["d", "b"]) == {
        **target,
        **{"join": "mundo hola"},
    }
    assert merge_join(target, "join", ["b", "e"]) == {
        **target,
        **{"join": "hola chamo"},
    }
    assert merge_join(target, "join", ["e", "b"]) == {
        **target,
        **{"join": "chamo hola"},
    }


def test_map_group():
    target = [
        {
            "a": "uno",
            "b": "one",
            "c": "chamo",
        },
        {
            "a": "uno",
            "b": "one",
            "c": "mae",
        },
        {
            "a": "uno",
            "b": "one",
            "c": "pana",
        },
        {
            "a": "dos",
            "b": "two",
            "c": "chama",
        },
    ]

    assert map_group(target, ["a", "b"]) == [
        {
            "a": "uno",
            "b": "one",
            "data": [
                {"c": "chamo"},
                {"c": "mae"},
                {"c": "pana"},
            ],
        },
        {
            "a": "dos",
            "b": "two",
            "data": [
                {"c": "chama"},
            ],
        },
    ]

    assert map_group(target, ["a", "b"], "c") == [
        {
            "a": "uno",
            "b": "one",
            "c": ["chamo", "mae", "pana"],
        },
        {
            "a": "dos",
            "b": "two",
            "c": ["chama"],
        },
    ]


def test_is_any_true():
    assert is_any_true(["a"]) is True
    assert is_any_true([""]) is False
    assert is_any_true(["", "a"]) is True
    assert is_any_true(["a", ""]) is True
    assert is_any_true(["a", "b"]) is True
    assert is_any_true([1]) is True
    assert is_any_true([0]) is False
    assert is_any_true([0, 1]) is True
    assert is_any_true([1, 0]) is True
    assert is_any_true([1, 2]) is True


def test_is_all_true():
    assert is_all_true(["a"]) is True
    assert is_all_true([""]) is False
    assert is_all_true(["", "a"]) is False
    assert is_all_true(["a", ""]) is False
    assert is_all_true(["a", "b"]) is True
    assert is_all_true([1]) is True
    assert is_all_true([0]) is False
    assert is_all_true([0, 1]) is False
    assert is_all_true([1, 0]) is False
    assert is_all_true([1, 2]) is True


def test_search_regex():
    assert search_regex("^$", "") is True
    assert search_regex("^[a-z]$", "") is False
    assert search_regex("^[a-z]$", "a") is True
    assert search_regex("^m", "match") is True
    assert search_regex("^h", "match") is False
    assert search_regex("^a.*", "abcd") is True
    assert search_regex("^.*bc.*", "abcd") is True
    assert search_regex("^.*bc.*", "abCd") is False


def test_set_difference():
    assert set_difference([[], []]) == []
    assert set(set_difference([["a", "b"], ["c"]])).difference(set(["a", "b"])) == set()
    assert set(set_difference([["a", "b"], []])).difference(set(["a", "b"])) == set()
    assert set(set_difference([["a", "b"], ["a", "d"]])).difference(set(["b"])) == set()
    assert set(set_difference([["a", "b"], ["b", "c"]])).difference(set(["a"])) == set()
    assert set(set_difference([["a", "b"], ["a", "b"]])).difference(set([])) == set()
