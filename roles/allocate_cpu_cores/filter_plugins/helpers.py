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

import itertools
import re

from ansible.errors import AnsibleError


def cpulist_to_set(cl):
    r = set()
    for e in cl.split(','):
        if '-' in e:
            p = e.split('-')
        else:
            p = [e, e]
        r.update(map(str, range(int(p[0]), int(p[1]) + 1)))
    return list(r)


def set_to_cpulist(cs):
    r = []
    for k, g in itertools.groupby(enumerate(sorted(cs, key=int)), lambda (i, v): int(v) - i):
        t = list(g)
        if len(t) == 1:
            r.append(str(t[0][1]))
        else:
            r.append('-'.join([str(t[0][1]), str(t[-1][1])]))
    return ','.join(r)


def _validate_node(topo, node, count):
    if node not in topo:
        raise AnsibleError("Unknown NUMA node '%s' (known nodes: %s)"
                           % (node, ', '.join(topo.keys())))
    if len(topo[node]) < count:
        raise AnsibleError("Cannot allocate %d CPUs in NUMA node '%s' (%d CPUs available)"
                           % (count, node, len(topo[node])))


def cpu_topology_alloc(topo, req, where='head'):
    r = set()
    for node, count in req.iteritems():
        _validate_node(topo, node, count)
        if count == 0:
            continue
        if where == 'tail':
            for i in topo[node][-count:]:
                r.update(i)
        else:
            for i in topo[node][:count]:
                r.update(i)
    return sorted(r)


def cpu_topology_trim(topo, req, where='head'):
    for node, count in req.iteritems():
        _validate_node(topo, node, count)
        if count == 0:
            continue
        if where == 'tail':
            topo[node] = topo[node][:-count]
        else:
            topo[node] = topo[node][count:]
    return topo


def _natural_sort(k):
    return [int(x) if x.isdigit() else x for x in re.split(r'([0-9]+)', k)]


def cpu_topology_defaults(topo, srv, req, is_virtual=False, is_single=False):
    own = 0
    shared = 0

    if is_virtual:
        req = req['virtual']
    elif is_single:
        req = req['single']
    else:
        req = req['default']

    for s in srv:
        if s not in req:
            continue
        if 'own' in req[s]:
            own += req[s]['own']
        if 'shared' in req[s]:
            shared = max(shared, req[s]['shared'])

    platform = own + shared
    if platform == 0:
        platform = 1

    nodes = [{'node': n, 'count': len(topo[n])} for n in sorted(topo, key=_natural_sort)]

    r = {}

    while platform > 0:
        prev = platform
        for i in nodes:
            if i['count'] <= 0:
                continue
            if i['node'] not in r:
                r[i['node']] = 0
            r[i['node']] += 1
            i['count'] -= 1
            platform -= 1
            if platform <= 0:
                break
        if platform == prev:
            break

    return r


def get_cpu_count_by_percent(topo, percent):
    return {
        n: int(_amount_with_minimum(len(topo[n]), float(percent)))
        for n in sorted(topo, key=_natural_sort)}


def _amount_with_minimum(whole, percent):
    amount = (whole * percent) / 100.0
    return amount if 0 < int(amount) else 1


class FilterModule(object):
    def filters(self):
        return {
            'cpulist_to_set': cpulist_to_set,
            'set_to_cpulist': set_to_cpulist,
            'cpu_topology_alloc': cpu_topology_alloc,
            'cpu_topology_trim': cpu_topology_trim,
            'cpu_topology_defaults': cpu_topology_defaults,
            'get_cpu_count_by_percent': get_cpu_count_by_percent,
        }
