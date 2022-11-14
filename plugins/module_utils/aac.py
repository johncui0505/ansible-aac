#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

import os
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap


def merge_dict_list(source, destination):
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge_dict_list(value, node)
        elif isinstance(value, list):
            if key not in destination:
                destination[key] = []
            if isinstance(destination[key], list):
                destination[key].extend(value)
        else:
            destination[key] = value
    return destination


def load_yaml_dir(path):
    class VaultTag:
        yaml_tag = "!vault"

        def __init__(self, vault_var):
            self.vault_var = vault_var

        def __repr__(self):
            return self.vault_var

        @staticmethod
        def yaml_constructor(loader, node):
            return VaultTag(loader.construct_scalar(node))

    data = CommentedMap()
    if path != "":
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path) and (
                ".yaml" in filename or ".yml" in filename
            ):
                with open(file_path, "r") as yaml_file:
                    data_yaml = yaml_file.read()
                    yaml = ruamel.yaml.YAML(typ="safe")
                    ruamel.yaml.add_constructor(
                        VaultTag.yaml_tag,
                        VaultTag.yaml_constructor,
                        constructor=ruamel.yaml.SafeConstructor,
                    )
                    data_dict = yaml.load(data_yaml)
                    merge_dict_list(data_dict, data)
    return data


def compare(previous, current, state={}, result=[]):
    if isinstance(previous, dict) and isinstance(current, dict):
        compare_dict(previous, current, state, result)
    elif isinstance(previous, list) and isinstance(current, list):
        compare_list(previous, current, state, result)
    else:
        if str(previous) != str(current):
            result.append(dict(state))
    return result


def compare_dict(previous, current, state, result):
    old_path = state.get("path", "")
    for k in previous.keys():
        if old_path:
            state["path"] = ".".join([old_path, k])
        else:
            state["path"] = k
        if k not in current:
            result.append(dict(state))
        else:
            compare(previous[k], current[k], state, result)
    for k in current.keys():
        if old_path:
            state["path"] = ".".join([old_path, k])
        else:
            state["path"] = k
        if k not in previous:
            result.append(dict(state))


def find_in_list(element, search_list):
    compare_types = (str, int, float, bool)
    for item in search_list:
        if isinstance(element, dict):
            diff = False
            for k, v in element.items():
                if isinstance(v, dict):
                    continue
                if type(v) in compare_types and item.get(k) != element.get(k):
                    diff = True
                    break
            if not diff:
                return item
        elif type(item) in compare_types and element == item:
            return item
    return None


def compare_list(previous, current, state, result):
    old_path = state.get("path", "")
    old_state = dict(state)
    if len(previous) != len(current):
        result.append(dict(state))
    for index, _ in enumerate(previous):
        new_state = dict(old_state)
        if old_path == "apic.tenants":
            new_state["tenant"] = previous[index]["name"]
        elif "apic.tenants" not in old_path and "apic." in old_path:
            new_state["tenant"] = ""
        if old_path == "apic.interface_policies.nodes":
            new_state["node"] = str(previous[index]["id"])
        elif "apic.interface_policies.nodes" not in old_path:
            new_state["node"] = ""
        if old_path == "mso.tenants":
            new_state["tenant"] = previous[index]["name"]
        elif "mso.tenants" not in old_path and "mso." in old_path:
            new_state["tenant"] = ""
        if old_path == "mso.schemas":
            new_state["schema"] = previous[index]["name"]
        elif "mso.schemas" not in old_path:
            new_state["schema"] = ""
        element = find_in_list(previous[index], current)
        if element is None:
            # result.append(dict(state))
            if isinstance(previous[index], dict):
                compare(previous[index], {}, new_state, result)
            elif isinstance(previous[index], list):
                compare(previous[index], [], new_state, result)
            else:
                compare(previous[index], "", new_state, result)
        else:
            compare(previous[index], element, new_state, result)
    for index, _ in enumerate(current):
        new_state = dict(old_state)
        if old_path == "apic.tenants":
            new_state["tenant"] = current[index]["name"]
        elif "apic.tenants" not in old_path and "apic." in old_path:
            new_state["tenant"] = ""
        if old_path == "apic.interface_policies.nodes":
            new_state["node"] = str(current[index]["id"])
        elif "apic.interface_policies.nodes" not in old_path:
            new_state["node"] = ""
        if old_path == "mso.tenants":
            new_state["tenant"] = current[index]["name"]
        elif "mso.tenants" not in old_path and "mso." in old_path:
            new_state["tenant"] = ""
        if old_path == "mso.schemas":
            new_state["schema"] = current[index]["name"]
        elif "mso.schemas" not in old_path:
            new_state["schema"] = ""
        element = find_in_list(current[index], previous)
        if element is None:
            # result.append(dict(state))
            if isinstance(current[index], dict):
                compare(current[index], {}, new_state, result)
            elif isinstance(current[index], list):
                compare(current[index], [], new_state, result)
            else:
                compare(current[index], "", new_state, result)
        else:
            compare(current[index], element, new_state, result)


def get_paths(inventory, state={}, result=[]):
    old_path = state.get("path", "")
    old_state = dict(state)
    if isinstance(inventory, dict):
        for k in inventory.keys():
            if old_path:
                state["path"] = ".".join([old_path, k])
            else:
                state["path"] = k
            get_paths(inventory[k], state, result)
    elif isinstance(inventory, list):
        for item in inventory:
            new_state = dict(old_state)
            if old_path == "apic.tenants":
                new_state["tenant"] = item["name"]
            elif "apic.tenants" not in old_path and "apic." in old_path:
                new_state["tenant"] = ""
            if old_path == "apic.interface_policies.nodes":
                new_state["node"] = str(item["id"])
            elif "apic.interface_policies.nodes" not in old_path:
                new_state["node"] = ""
            if old_path == "mso.tenants":
                new_state["tenant"] = item["name"]
            elif "mso.tenants" not in old_path and "mso." in old_path:
                new_state["tenant"] = ""
            if old_path == "mso.schemas":
                new_state["schema"] = item["name"]
            elif "mso.schemas" not in old_path:
                new_state["schema"] = ""
            get_paths(item, new_state, result)
    else:
        result.append(dict(state))
    return result
