from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.section.api.plugins.module_utils.client import Client


class ProxyClient(Client):

    def __init__(self, account, application, endpoint, username, password, options={}):
        Client.__init__(self, endpoint, username, password, options)
        self.options['base_path'] = f'/account/{account}/application/{application}/environment/{environment}/proxy'

    def get(self, name):
        return self.request(f'/{name}/configuration')

    def ban(self, name, expression, wait=False):
        path = f'/{name}/state?banExpression={expression}&async={wait}'
        return self.request(path=path, method='POST')
