from __future__ import (absolute_import, division, print_function)
from ansible_collections.section.api.plugins.module_utils.env_client import EnvClient as ApiClient
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
__metaclass__ = type

DOCUMENTATION = """
  name: environment
  author: Steve Worley <steven.worley@salsadigital.com.au>
  short_description: get a section environment
  description:
      - This lookup returns the information for a Section environment.
  options:
    _terms:
      description: The environment to query for
      required: True
    username:
      description: The API user
      type: string
      required: True
      vars:
        - name: section_username
    password:
      description: The API users password
      type: string
      required: true
      vars:
        - name: section_password
    account:
        description: The account id
        type: long
        required: true
    application:
        description: The application id
        type: long
        required: true
    headers:
      description: HTTP request headers
      type: dictionary
      default: {}
    timeout:
      description: How long to wait for the server to send data before giving up
      type: float
      default: 10
      vars:
          - name: ansible_lookup_url_timeout
      env:
          - name: ANSIBLE_LOOKUP_URL_TIMEOUT
      ini:
          - section: url_lookup
            key: timeout
"""

EXAMPLES = """
- name: retrieve a environment's information
  debug: msg="{{ lookup('section.api.environment', 'Develop', section_account=1, section_application=1) }}"
"""

display = Display()

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        ret = []

        self.set_options(var_options=variables, direct=kwargs)

        client = ApiClient(
            self.get_option('section_account'),
            self.get_option('section_application'),
            self.get_option('section_username'),
            self.get_option('section_password'),
            {'headers': self.get_option('headers', {})}
        )

        for term in terms:
            ret.append(client.get(term))

        return ret
