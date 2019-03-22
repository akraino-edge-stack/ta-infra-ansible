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

import xml.etree.ElementTree as ET

DOCUMENTATION = '''
---
'''

def main():
    module = AnsibleModule(
        argument_spec=dict(
            xml_file=dict(required=True),
        ),
    )

    defaults = module.params.copy()
    xml_file = defaults.pop('xml_file', None)

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except IOError as e:
        module.fail_json(msg=str(e))

    for child in root:
        if child.tag == 'devices':
            devices=child
            break;

    mac_list = []
    for child in devices:
        if child.tag == 'interface':
            for detail in child:
                if detail.tag == 'mac':
                    mac_list.append(detail.attrib['address'])

    module.exit_json(
        changed=True,
        mac_list=mac_list,
    )

from ansible.module_utils.basic import *


if __name__ == '__main__':
    main()
