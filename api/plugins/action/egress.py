from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible.errors import AnsibleError
from ansible.plugins.action import ActionBase
from ansible.utils.display import Display
from ansible_collections.section.api.plugins.module_utils.env_client import EnvClient as ApiClient

display = Display()

EXAMPLES = r'''
- name: Set the Develop environment egress to a new backend
  section.api.egress:
    environment: Develop
    egress: my-origin.com
- name: Remove request headers for
  section.api.egress:
    environment: Develop
    egress: my-origin.com
    remove_headers:
      - section-io-id
      - x-my-request-location
'''

class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        """Update the egress of an environment.

        This will return skipped if the egress does not need to be updated.

        Parameters
        ----------
        environment : str
            The environment name
        egress : str
            The egress host name to set
        egress_name : str, optional
            The name of the egress object in Section
        remover_headers : list, optional
            A list of optional request headers to remove when handling requests, if omitted section-io-id
            will be added for compatibility

        Raises
        ----------
        AnsibleError
            Raised when parameters are missing or API request fails

        Environment
        ----------
        section_username : str
            The account name to authenticate with the API
        section_password : str
            The password (or token) to authenticate with the API
        section_account : str
            The section account id
        section_application : str
            The section application id
        """

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        environment_name = self._task.args.get('environment')
        egress = self._task.args.get('egress')
        remove_headers = self._task.args.get('remove_headers')
        egress_name = self._task.args.get('egress_name')

        if not environment_name:
            raise AnsibleError("Required parameter 'environment' is missing")

        if not egress:
            raise AnsibleError("Required parameter 'egress' is missing")

        if not remove_headers:
            remove_headers = ['section-io-id']

        if not isinstance(remove_headers, list):
            remove_headers = [remove_headers]

        if not egress_name:
            egress_name = 'default'

        client = ApiClient(
            task_vars.get('section_account'),
            task_vars.get('section_application'),
            task_vars.get('section_username'),
            task_vars.get('section_password'),
            {'headers': {}}
        )

        egress_config = client.list_egress(environment_name)

        if set(remove_headers) == set(egress_config['remove_request_headers']) and egress_config['origins'][egress_name]['address'] == egress:
            result['skipped'] = True
            return result

        client.update_egress(environment_name, egress, egress_name=egress_name, remove_headers=remove_headers)
        result['changed'] = True

        return result
