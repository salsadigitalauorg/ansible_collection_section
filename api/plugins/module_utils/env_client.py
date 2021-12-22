from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.section.api.plugins.module_utils.client import Client


class EnvClient(Client):

    def __init__(self, account, application, endpoint, username, password, options={}):
        Client.__init__(self, endpoint, username, password, options)
        self.options['base_path'] = f'/account/{account}/application/{application}/environment'

    def all(self):
        return self.request()

    def get(self, name):
        return self.request(f'/{name}')

    def create(self, name, source_environment_name, domain_name):
        return self.request(method='POST', payload={
            'name': name,
            'source_environment_name': source_environment_name,
            'domain_name': domain_name
        })

    def add_domain(self, name, hostname):
        return self.request(f'/{name}/domain/{hostname}', 'POST')

    def delete_domain(self, name, hostname):
        return self.request(f'/{name}/domain/{hostname}', 'DELETE')
