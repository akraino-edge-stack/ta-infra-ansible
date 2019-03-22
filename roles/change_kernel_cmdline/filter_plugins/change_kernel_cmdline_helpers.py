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

def cpulist_combine(conf, name, lst):
    r = set()
    for s in lst:
        if s in conf:
            r.update(conf[s]['set'])
    if len(r) > 0:
        conf[name] = { 'set': sorted(r), 'list': set_to_cpulist(r) }
    return conf

def cmdline_to_list(cmdl):
    return re.findall('(?:[^" ]|"[^"]*")+', cmdl)

def list_to_cmdline(lst):
    return ' '.join(lst)

class FilterModule(object):
    def filters(self):
        return {
            'cpulist_to_set': cpulist_to_set,
            'set_to_cpulist': set_to_cpulist,
            'cpulist_combine': cpulist_combine,
            'cmdline_to_list': cmdline_to_list,
            'list_to_cmdline': list_to_cmdline
        }

