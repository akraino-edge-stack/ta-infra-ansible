#!/usr/bin/python

# Copyright 2019 Nokia

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fnmatch

try:
    import shade
    from shade import meta
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

DOCUMENTATION = '''
---
module: os_node_provision_check
short_description: Retrieve facts about ironic nodes list provided,
                   Returns a list of nodes which are not in deploying and failed states
version_added: "2.0"
description:
    - Retrieve facts about ironic nodes list provided,
      Returns a list of nodes which are not in deploying and failed states
requirements:
    - "python >= 2.6"
    - "shade"
options:
   nodes_details:
     description:
       - List of dicts [{id: <ironic_node_id>, name: <ironic_node_name>},....], containing ironic node ids and names.
         This modules runs through all the ironic nodes and returns list of nodes in deploying and failed state.
     required: True
     default: None
returns:
     provision_pending_list
     provision_failed_list
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Gather facts about all nodes named C<web*>:
- os_node_provision_check:
    cloud: rax-dfw
    nodes_details:
      - id: <id-1>
        name: <name-1>
      - id: <id-2>
        name: <name-2>
'''


def main():

    argument_spec = openstack_full_argument_spec(
        nodes_details=dict(type='list', required=True), 
        ironic_url=dict(required=False),
    )
    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')
    if (module.params['auth_type'] in [None, 'None'] and
            module.params['ironic_url'] is None):
        module.fail_json(msg="Authentication appears to be disabled, "
                             "Please define an ironic_url parameter")

    if (module.params['ironic_url'] and
            module.params['auth_type'] in [None, 'None']):
        module.params['auth'] = dict(
            endpoint=module.params['ironic_url']
        )

    try:
        cloud = shade.operator_cloud(**module.params)

        nodes_details = module.params['nodes_details']
        provision_pending_list = []
        provision_failed_list = []

        for node in nodes_details:
            node_name = node['name']
            node_details = cloud.get_machine(node_name)

            if node_details['provision_state'] in ['deploying', 'wait call-back']:
                provision_pending_list.append(node_name)

            if node_details['provision_state'] in ['deploy failed']:
                node_provision_state = {}
                node_provision_state['name'] = node_name
                node_provision_state['provision_state'] = node_details['provision_state']
                provision_failed_list.append(node_provision_state)

        module.exit_json(changed=False, ansible_facts=dict(provision_pending_list=provision_pending_list, provision_failed_list=provision_failed_list))

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))

# this is magic, see lib/ansible/module_common.py
from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *
if __name__ == '__main__':
    main()
