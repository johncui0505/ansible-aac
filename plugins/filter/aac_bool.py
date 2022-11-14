#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Daniel Schmidt <danischm@cisco.com>

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def aac_bool(value, format):
    v = False
    if value in [True, "enabled", "yes", "on"]:
        v = True

    if format is True:
        return v
    elif format == "enabled":
        return "enabled" if v else "disabled"
    elif format == "yes":
        return "yes" if v else "no"
    elif format == "on":
        return "on" if v else "off"


class FilterModule(object):
    """Ansible jinja2 filters"""

    def filters(self):
        return {
            "aac_bool": aac_bool,
        }
