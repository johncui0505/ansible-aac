#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {"metadata_version": "0.1", "status": ["preview"]}

DOCUMENTATION = r"""
---
module: aci_nae_prepare
short_description: Merge changed objects into a single (json) file.
description:
- Merge changed objects into a single (json) file.
version_added: '2.8'
options:
  changed_dir:
    description:
    - The path to the changed json files.
    type: str
    required: yes
  dest:
    description:
    - The path to the destination file.
    type: str
    required: yes
author:
- Daniel Schmidt
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

import os
import json

from ansible.module_utils.basic import AnsibleModule

PCA_OBJECTS = [
    "fvTenant",
    "physDomP",
    "fabricLePortP",
    "infraNodeP",
    "infraSpineP",
    "infraAccPortGrp",
    "infraSpAccPortGrp",
    "cdpIfPol",
    "lldpIfPol",
]


class ApicObject:
    def __init__(self, cl, attributes, children, parent):
        self.cl = cl
        self.attributes = attributes
        self.children = children
        self.parent = parent

    def update(self, attributes, children):
        self.attributes.update(attributes)
        for child in children:
            dn = child.attributes.get("dn")
            name = child.attributes.get("name")
            found = False
            # look for existing object with dn
            if dn is not None:
                for c in self.children:
                    if c.attributes.get("dn") == dn:
                        if child.cl != c.cl:
                            continue
                        c.update(child.attributes, child.children)
                        found = True
            if found:
                continue
            # look for existing object with name
            if name is not None:
                for c in self.children:
                    if c.attributes.get("name") == name and child.cl == c.cl:
                        c.update(child.attributes, child.children)
                        found = True
            if found:
                continue
            # add as a new child
            self.children.append(
                ApicObject(child.cl, child.attributes, child.children, self)
            )

    def find(self, dn=None, cl=None):
        result = []
        if dn is None and cl is None:
            return result
        elif cl is None:
            if self.attributes.get("dn") == dn:
                result.append(self)
        elif dn is None:
            if self.cl == cl:
                result.append(self)
        elif self.attributes.get("dn") == dn and self.cl == cl:
            result.append(self)
        for child in self.children:
            objs = child.find(dn=dn, cl=cl)
            result.extend(objs)
        return result

    def insert(self, obj):
        if obj is None:
            return
        dn = obj.attributes["dn"]
        o = self.find(dn=dn)
        if len(o) > 0:
            o[0].update(obj.attributes, obj.children)
        else:
            index = dn.rfind("/")
            if index == -1:
                self.children.append(obj)
                obj.parent = self
            else:
                parent_dn = dn[:index]
                o = self.find(dn=parent_dn)
                if len(o) > 0:
                    o[0].children.append(obj)
                    obj.parent = o[0]
                else:
                    new_obj = ApicObject(None, {"dn": parent_dn}, [obj], None)
                    obj.parent = new_obj
                    self.insert(new_obj)

    def add_child(self, cl, attributes, children):
        child = ApicObject(cl, attributes, children, self)
        self.children.append(child)
        return child

    def add_parent(self, cl, attributes):
        if self.parent is not None:
            raise Exception(
                "ApicObject {} already has a parent.".format(str(ApicObject))
            )
        self.parent = ApicObject(cl, attributes, [self], None)
        return self.parent

    def get_root(self):
        obj = self
        # max search depth 100
        for i in range(100):
            if obj.cl == "root":
                return obj
            elif obj.parent is not None:
                obj = obj.parent
            else:
                return None
        return None

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.attributes.get(key)
        else:
            return self.children[key]

    def __str__(self):
        """Return json string."""
        attr_string = ", ".join(
            ['"{}": "{}"'.format(k, v) for k, v in self.attributes.items()]
        )
        child_string = ", ".join([str(c) for c in self.children])
        return '{{"{}": {{"attributes": {{{}}}, "children": [{}]}}}}'.format(
            self.cl, attr_string, child_string
        )


def load_json_objects(json_dict, parent=None):
    new_obj = None
    for k, v in json_dict.items():
        new_obj = ApicObject(k, v.get("attributes"), [], parent)
        if parent:
            parent.children.append(new_obj)
        for child in v.get("children", []):
            load_json_objects(child, new_obj)
    return new_obj


def load_files(root, path):
    def _load_file(file_path):
        with open(file_path, "r") as fh:
            if ".json" in file_path:
                inv = json.loads(fh.read())
                obj = load_json_objects(inv)
                root.insert(obj)

    # load files into object tree
    if os.path.isfile(path):
        _load_file(path)
    for dir, subdir, files in os.walk(path):
        for filename in files:
            _load_file(dir + os.path.sep + filename)


def mark_pca_children(root):
    for child in root.children:
        child.pca = True
        mark_pca_children(child)


def mark_pca_objects(root):
    if root.cl in PCA_OBJECTS:
        obj = root
        # max search depth 100
        for i in range(100):
            obj.pca = True
            if obj.cl == "root":
                break
            elif obj.parent is not None:
                obj = obj.parent
            else:
                break
        mark_pca_children(root)
    for child in root.children:
        mark_pca_objects(child)


def delete_child(root, dn):
    for child in root.children:
        if child["dn"] == dn:
            root.children.remove(child)
            return


def remove_non_pca_objects(root):
    to_delete = []
    for child in root.children:
        if not hasattr(child, "pca"):
            to_delete.append(child["dn"])
        remove_non_pca_objects(child)
    for dn in to_delete:
        delete_child(root, dn)


def run_module():
    module_args = dict(
        changed_dir=dict(type="str", required=True),
        dest=dict(type="str", required=True),
    )

    result = dict(changed=False)

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    changed_dir = module.params["changed_dir"]
    dest = module.params["dest"]

    root = ApicObject("root", {}, [], None)

    if changed_dir and not os.path.exists(changed_dir):
        module.fail_json(
            msg="The provided directory (changed_dir) does not appear to exist. Is it a directory?"
        )
    try:
        load_files(root, changed_dir)
    except Exception:
        module.fail_json(msg="Failed to load files from '%s'." % changed_dir)

    if module.check_mode:
        module.exit_json(**result)

    mark_pca_objects(root)
    remove_non_pca_objects(root)

    uni = root.children[0]
    uni.cl = "polUni"

    if os.path.isfile(dest) and str(uni) == open(dest).read():
        result["changed"] = False
    else:
        result["changed"] = True

    with open(dest, "w") as fh:
        fh.write(str(uni))
        result

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
