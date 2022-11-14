#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# This is a virtual module that is entirely implemented as an action plugin and runs on the controller

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: template_local
version_added: historical
short_description: Template a file on the controller
options:
  follow:
    description:
    - Determine whether symbolic links should be followed.
    - When set to C(yes) symbolic links will be followed, if they exist.
    - When set to C(no) symbolic links will not be followed.
    type: bool
    default: no
    version_added: '2.10'
author:
- Ansible Core Team
- Michael DeHaan
- Daniel Schmidt
extends_documentation_fragment:
- backup
- files
- template_common
- validate
"""

EXAMPLES = r"""
- name: Template a file to /tmp/file.conf
  template_local:
    src: /mytemplates/foo.j2
    dest: /tmp/file.conf
    owner: bin
    group: wheel
    mode: '0644'

- name: Template a file, using symbolic modes (equivalent to 0644)
  template_local:
    src: /mytemplates/foo.j2
    dest: /tmp/file.conf
    owner: bin
    group: wheel
    mode: u=rw,g=r,o=r

- name: Create a DOS-style text file from a template
  template_local:
    src: config.ini.j2
    dest: /share/windows/config.ini
    newline_sequence: '\r\n'

- name: Copy a new sudoers file into place, after passing validation with visudo
  template_local:
    src: /mine/sudoers
    dest: /tmp/sudoers
    validate: /usr/sbin/visudo -cf %s
"""
