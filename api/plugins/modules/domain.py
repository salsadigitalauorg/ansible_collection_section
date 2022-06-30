#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
from ansible_collections.section.api.plugins.module_utils.env_client import EnvClient as ApiClient
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
    hostname:
        description: The hostname to add.
        required: true
        type: str
    public_key:
        description: Optional public key for SSL.
        required: false
        type: str
    private_key:
        description: Optional private key for SSL.
        required: false
        type: str
    state:
        description:
        - Determines if the domain should be created, updated, or deleted. When set to C(present), the domain will be
        created, if it does not already exist. If set to C(absent), an existing domain will be deleted.
        type: str
        default: present
        choices: [ absent, present ]
extends_documentation_fragment:
  - section.api.auth_options
author:
    - Steve Worley (@steveworley)
'''

EXAMPLES = r'''
- name: Delete Section domain.
  section.api.domain:
    account: 1
    application: 1
    environment: 'Production'
    hostname: www.test.com
    state: absent
'''


def main():
    module_args = dict(
        section_username=dict(type='str', required=True),
        section_password=dict(type='str', required=True, no_log=True),
        headers=dict(type='dict', required=False, default={}),
        section_account=dict(type='int', required=True),
        section_application=dict(type='int', required=True),
        environment=dict(type='str', required=True),
        hostname=dict(type='str', required=True),
        state=dict(type='str', required=False, default='present'),
    )

    result = dict(changed=False, result={})

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    client = ApiClient(
        account=module.params['section_account'],
        application=module.params['section_application'],
        username=module.params['section_username'],
        password=module.params['section_password'],
        options={'headers': module.params['headers']}
    )

    environment = client.get(module.params['environment'])

    if module.check_mode:
        found = False
        for domain in environment['domains']:
            if domain['name'] == module.params['hostname']:
                found = True

        if module.params['state'] == 'present':
            result['result'] = "Create" if not found else "No change"

        if module.params['state'] == 'absent':
            result['result'] = "Remove" if found else "No change"

        module.log('Check result for section.api.domain: %s' % result['result'])
        module.exit_json(**result)

    if module.params['state'] == 'present':
        for domain in environment['domains']:
            if domain['name'] == module.params['hostname']:
                module.exit_json(**result)

        result['result'] = client.add_domain(module.params['environment'], module.params['hostname'])
        result['changed'] = True

    elif module.params['state'] == 'absent':
        for domain in environment['domains']:
            if domain['name'] == module.params['hostname']:
                client.delete_domain(module.params['environment'], module.params['hostname'])
                result['result'] = module.params['hostname']
                result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
