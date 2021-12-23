#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from ansible_collections.section.api.plugins.module_utils.proxy_client import ProxyClient as ApiClient
from ansible.module_utils.basic import AnsibleModule
__metaclass__ = type

DOCUMENTATION = r'''
---
module: domain
short_description: Manage application>environment domains.
version_added: "1.0.0"
description:
    - Allows creating, updating, replacing and deleting domains for an environment.
options:
    account:
        description: The account id.
        required: true
        type: int
    application:
        description: The application id.
        required: true
        type: int
    environment:
        description: The environment name.
        required: true
        type: str
    proxy:
        description: The proxy to send the ban to.
        required: true
        type: str
        default: varnish
    wait:
        description: Wait for edge nodes to be cleared.
        required: false
        type: bool
        default: false
author:
    - Steve Worley (@steveworley)
'''

EXAMPLES = r'''
- name: Clean varnish caches
  section.api.ban:
    account: 1
    application: 1
    environment: 'Production'
    expression: req.url~/
    wait: true
'''


def main():
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        headers=dict(type='dict', required=False, default={}),
        account=dict(type='int', required=True),
        application=dict(type='int', required=True),
        environment=dict(type='str', required=True),
        hostname=dict(type='str', required=True),
        state=dict(type='str', required=False, default='present'),
    )

    result = dict(changed=False, result={})

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    client = ApiClient(
        module.params['username'],
        module.params['password'],
        {'headers': module.params['headers']}
    )

    client.ban('varnish', module.params['expression'])

if __name__ == '__main__':
    main()
