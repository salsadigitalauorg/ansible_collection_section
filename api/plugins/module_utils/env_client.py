from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.section.api.plugins.module_utils.client import Client


class EnvClient(Client):

    def __init__(self, account, application, username, password, options={}):
        Client.__init__(self, username=username, password=password, options=options)
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

    def list_egress(self, name):
        """List egress configuration for an environment

        Parameters
        ----------
        name : str
          The environment name
        """

        return self.request(method="GET", path=f"/{name}/egress")

    def update_egress(self, name, egress, egress_name='default', remove_headers=list()):
        """ Updates an environments default egress.

        Parameters
        ----------
        name : str
            The environment name
        egress : str
            The egress hostname
        """
        return self.request(method='POST', path=f'/{name}/egress', payload={
            "remove_request_headers": remove_headers,
            "origins": {
                f"{egress_name}": {
                    "address": egress,
                }
            },
        })
