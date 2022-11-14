#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = r"""
---
module: mso_login
short_description: MSO login
description:
- MSO login.
author:
- Daniel Schmidt
version_added: '2.8'
options:
extends_documentation_fragment: mso
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.network.aci.mso import MSOModule, mso_argument_spec


def main():
    argument_spec = mso_argument_spec()

    module = AnsibleModule(argument_spec=argument_spec)

    mso = MSOModule(module)

    mso.result["token"] = mso.headers["Authorization"][7:]

    mso.result["changed"] = False

    mso.exit_json()


if __name__ == "__main__":
    main()
