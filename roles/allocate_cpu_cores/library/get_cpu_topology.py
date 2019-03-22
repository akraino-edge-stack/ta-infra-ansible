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

import glob

from ansible.module_utils.basic import *

def mask2list(path):
    r = set()

    with open(path, 'r') as f:
        masks = [int(x, 16) for x in f.read().split(',')]

    masks.reverse()

    i = 0
    for m in masks:
        for j in range(32):
            if m & (1 << j):
                r.add(i)
            i += 1

    return sorted(r)

def get_node_cores(nodepath):
    r = []
    s = set()

    for cpu in mask2list(nodepath + '/cpumap'):
        if cpu not in s:
            v = mask2list(nodepath + '/cpu%d/topology/thread_siblings' % cpu)
            r.append(v)
            s.update(v)

    return r

def main():
    module = AnsibleModule(argument_spec = { 'var': { 'required': True, 'type': 'str' } })

    pattern = '/sys/devices/system/node/node*'
    r = {}

    for nodepath in glob.glob(pattern):
        nodeid = nodepath[len(pattern) - 1:]
        r['numa' + nodeid] = get_node_cores(nodepath)

    module.exit_json(changed = False, ansible_facts = { module.params['var']: r })

if __name__ == '__main__':
    main()
