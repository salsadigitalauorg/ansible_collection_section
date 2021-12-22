# -*- coding: utf-8 -*-

# Options for authenticating with the API.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    DOCUMENTATION = r'''
options:
    section_endpoint:
        description:
            - Provide a URL for accessing the API.
        type: str
    section_username:
        description:
            - Username used to authenticate with the API.
        type: str
    section_password:
        description:
            - Password used to authenticate with the API.
        type: str
'''
