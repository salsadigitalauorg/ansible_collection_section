from __future__ import absolute_import, division, print_function

import json
import os
import re

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible_collections.section.api.plugins.module_utils.client import Client as ApiClient

__metaclass__ = type

DOCUMENTATION = """
    name: applications
    plugin_type: inventory
    author:
      - Steve Worley <@steveworley>
    short_description: Section.io inventory source
    description:
      - Fetch applications for one or more accounts
      - Groups by account id
    options:
      connections:
          description:
          - List of Section.io API connection configuration.
          suboptions:
              name:
                  description:
                  - Optional name to assign to the cluster.
              username:
                  description:
                  - Provide a username for authenticating with the API.
              password:
                  description:
                  - Provide a password for authenticating with the API.
              limit_accounts:
                description:
                - List of account ids to limit the inventory to.
    requirements:
    - "python >= 3.6"
    - "PyYAML >= 3.11"
"""

EXAMPLES = """
# File must be named section.yaml or section.yml
# Authenticate with token, and return all pods and services for all namespaces
plugin: section.api.account
connections:
  - username: testuser
    password: password
    limit_accounts:
    - 1
"""


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):

    NAME = "section.api.applications"

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        cache_key = self._get_cache_prefix(path)
        config_data = self._read_config_data(path)
        self.setup(config_data, cache, cache_key)

    def slugify(self, text):
        return re.sub(r'[\W-]+', '_', text).lower()

    def setup(self, config_data, cache, cache_key):

        connections = config_data.get('connections')

        source_data = None

        if cache and cache_key in self._cache:
            try:
                source_data = self._cache[cache_key]
            except KeyError:
                pass

        config_spec = dict(
            username=os.getenv('SECTION_IO_USERNAME'),
            password=os.getenv('SECTION_IO_PASSWORD'),
            limit_accounts=[]
        )

        if not source_data:
            if len(connections) == 0:
                if os.getenv('SECTION_IO_ACCOUNT_ID'):
                    config_spec['limit_accounts'] = [os.getenv('SECTION_IO_ACCOUNT_ID')]
                connections.append(config_spec)

            for connection in connections:
                connection = dict(config_spec, **connection)
                try:
                    self.fetch(**connection)
                except KeyError:
                    raise AnsibleError('Invalid connection dict')

    def fetch(self, username, password, limit_accounts=[]):
        accounts = []

        client = ApiClient(username, password)
        response = client.request('/account')

        for account in response:
            try:
                if len(limit_accounts) > 0 and account['id'] not in limit_accounts:
                    continue
                accounts.append({
                    'id': account['id'],
                    'name': self.slugify(account['account_name']),
                })
            except KeyError as key:
                raise AnsibleError(f'Invalid account definition, missing ({key}) from response.')

        # Fetch applications for the accounts.
        for account in accounts:
            sid = account['id']

            self.inventory.add_group(account['name'])

            applications = client.request(f'/account/{sid}/application')

            for application in applications:
                try:
                    app_id = application['id']
                    app_name = application['application_name']
                except KeyError as key:
                    raise AnsibleError(f'Invalid application definition, missing ({key}) from response.')

                # Add inventory group for the application.
                self.inventory.add_group(app_name)

                environments = client.request(f'/account/{sid}/application/{app_id}/environment')

                for environment in environments:
                    env_name = environment['environment_name']
                    host_name = f'{sid}-{app_name}-{env_name}'

                    self.inventory.add_group(env_name)

                    # Add the host to the groups.
                    self.inventory.add_host(host_name)
                    self.inventory.add_child(env_name, host_name)
                    self.inventory.add_child(app_name, host_name)
                    self.inventory.add_child(account['name'], host_name)

                    # Add hostvars.
                    self.inventory.set_variable(host_name, 'branch', env_name)
                    self.inventory.set_variable(host_name, 'id', app_id)
                    self.inventory.set_variable(host_name, 'name', app_name)
                    self.inventory.set_variable(host_name, 'section_id', sid)

                    try:
                        self.inventory.set_variable(host_name, 'domains', list(
                            map(lambda x: x["name"], environment['domains'])))
                    except KeyError:
                        pass


