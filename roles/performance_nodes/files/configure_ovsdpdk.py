#!/usr/bin/env python

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

import argparse
import subprocess
import sys


class CoreHandler(object):
    def __init__(self):
        pass

    @staticmethod
    def hex_to_set(hexstr):
        hexn = int(hexstr, 16)
        b = 1
        cpuset = set()
        for i in range(0, 64):
            if hexn & b != 0:
                cpuset.add(i)
            b = b << 1
        return cpuset

    @staticmethod
    def set_to_hex(cpuset):
        cpumask = 0
        for i in cpuset:
            b = 1 << i
            cpumask += b
        return '0x{:x}'.format(cpumask)

    @staticmethod
    def string_to_set(cpustr):
        if cpustr == '' or cpustr is None:
            raise Exception("Empty string")
        cpuset_ids = set()
        cpuset_reject_ids = set()
        for rule in cpustr.split(','):
            rule = rule.strip()
            # Handle multi ','
            if len(rule) < 1:
                continue
            # Note the count limit in the .split() call
            range_parts = rule.split('-', 1)
            if len(range_parts) > 1:
                # So, this was a range; start by converting the parts to ints
                try:
                    start, end = [int(p.strip()) for p in range_parts]
                except ValueError:
                    raise Exception("Invalid range expression {}".format(rule))
                # Make sure it's a valid range
                if start > end:
                    raise Exception("Invalid range expression (start > end): {}".format(rule))
                # Add available CPU ids to set
                cpuset_ids |= set(range(start, end + 1))
            elif rule[0] == '^':
                # Not a range, the rule is an exclusion rule; convert to int
                try:
                    cpuset_reject_ids.add(int(rule[1:].strip()))
                except ValueError:
                    raise Exception("Invalid exclusion expression {}".format(rule))
            else:
                # OK, a single CPU to include; convert to int
                try:
                    cpuset_ids.add(int(rule))
                except ValueError:
                    raise Exception("Invalid inclusion expression {}".format(rule))

        # Use sets to handle the exclusion rules for us
        cpuset_ids -= cpuset_reject_ids
        return cpuset_ids

    @staticmethod
    def set_to_string(cpuset):
        ranges = []
        previndex = None
        for cpuindex in sorted(cpuset):
            if previndex is None or previndex != (cpuindex - 1):
                ranges.append([])
            ranges[-1].append(cpuindex)
            previndex = cpuindex

        parts = []
        for entry in ranges:
            if len(entry) == 1:
                parts.append(str(entry[0]))
            else:
                parts.append("{}-{}".format(entry[0], entry[len(entry) - 1]))
        return ",".join(parts)

    def hex_to_string(self, hexstr):
        """
        :param hexstr: CPU mask as hex string
        :returns: a formatted CPU range string
        """
        cpuset = self.hex_to_set(hexstr)
        return self.set_to_string(cpuset)

    def string_to_hex(self, cpustr):
        cpuset = self.string_to_set(cpustr)
        return self.set_to_hex(cpuset)


class OvsVsctl(object):
    def __init__(self, cores, pcore, tcore, sockets):
        self.cores = cores
        self.pcore = pcore
        self.threads_per_core = tcore
        self.sockets = sockets

    def is_hyperthreading_enabled(self):
        if int(self.threads_per_core) >= 2:
            return True
        return False

    def is_single_socket(self):
        if int(self.sockets) == 1:
            return True
        return False

    @staticmethod
    def get_value(field):
        """Get value for specified field in Open_vSwitch other_config.
        Returns:
            Value without quotes or newlines
            None if field is not set
        """
        try:
            current_value = subprocess.check_output(["ovs-vsctl", "get", "Open_vSwitch", ".", "other_config:{}".format(field)])
        except Exception:
            return None
        return current_value.lstrip('\"').strip('\n').rstrip('\"')

    def set_pmd_cpu_mask(self, value):
        """Set DPDK core mask."""
        current_value = self.get_value('pmd-cpu-mask')
        print "INFO: New core mask {}, current_value {}".format(value, current_value)
        if current_value == value:
            return False
        try:
            subprocess.check_output(["ovs-vsctl", "set", "Open_vSwitch", ".", "other_config:pmd-cpu-mask=\"{}\"".format(value)])
        except Exception:
            sys.exit(2)
        return True

    def set_lcore_mask(self):
        """Set DPDK library mask."""
        #if self.is_single_socket():
        mask = '0x0'
        # TODO: measure if it would be beneficial to reserve more cores and from second socket
        current_value = self.get_value('dpdk-lcore-mask')
        print "INFO: Mask {},  current_value {}".format(mask, current_value)

        if current_value == mask:
            return False
        try:
            subprocess.check_output(["ovs-vsctl", "set", "Open_vSwitch", ".", "other_config:dpdk-lcore-mask=\"{}\"".format(mask)])
        except Exception:
            sys.exit(2)
        return True

    def set_socket_mem(self, value):
        """Set DPDK memory."""
        if self.is_single_socket():
            mem = '{0},0'.format(value)
        else:
            mem = '{0},{0}'.format(value)
        current_value = self.get_value('dpdk-socket-mem')
        print "INFO: New mem {},  current_value {}".format(mem, current_value)

        if current_value == mem:
            return False
        try:
            subprocess.check_output(["ovs-vsctl", "set", "Open_vSwitch", ".", "other_config:dpdk-socket-mem=\"{}\"".format(mem)])
        except Exception:
            sys.exit(2)
        return True

    def enable_dpdk(self):
        """Enable DPDK."""
        current_value = self.get_value('dpdk-init')
        print "INFO: Enable DPDK, current_value {}".format(current_value)
        if current_value == 'true':
            return False

        try:
            with open('/etc/performance-nodes/dpdk.enabled', 'a'):
                pass
        except IOError:
            sys.exit(2)

        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dpdkcores', dest='dpdkcores', help='DPDK cores', required=False, type=str)
    parser.add_argument('--cores', dest='cores', help='Logical cores', required=False, type=str)
    parser.add_argument('--pcore', dest='pcore', help='Cores per processor', required=False, type=str)
    parser.add_argument('--tcore', dest='tcore', help='Threads per core', required=False, type=str)
    parser.add_argument('--sockets', dest='sockets', help='Number of sockets', required=False, type=str)
    parser.add_argument('--mem', dest='mem', help='Socket mem', required=False, type=str, default='4096')
    args = parser.parse_args()

    ovsvsctl = OvsVsctl(args.cores, args.pcore, args.tcore, args.sockets)
    coreh = CoreHandler()

    dpdkcoreset = None
    try:
        print "INFO: dpdk cores: {}, cpu count: {}".format(args.dpdkcores, args.cores)
        if args.dpdkcores:
            dpdkcoreset = coreh.string_to_set(args.dpdkcores)
    except Exception as exp:
        print "ERROR: Calculating of cpu/core set failed: {}".format(exp)
        sys.exit(2)

    if max(dpdkcoreset) > int(args.cores):
        print "ERROR: invalid DPDK cores (too big)"
        sys.exit(2)

    # Check if hyperthreading is off and we can calculate new core set so that
    # DPDK has a chance to start.
    if not ovsvsctl.is_hyperthreading_enabled() and max(dpdkcoreset) > int(args.cores):
        print "INFO: Hyperthreading off, DPDK cores contain too big core"
        dpdkcoreset = set([x for x in dpdkcoreset if x < int(args.cores)])
        print "INFO: new dpdkcoreset {}".format(dpdkcoreset)
    else:
        dpdkcoreset = dpdkcoreset
    dpdkcoremask = coreh.set_to_hex(dpdkcoreset)

    changed = False

    changed |= ovsvsctl.set_pmd_cpu_mask(dpdkcoremask)
    #changed |= ovsvsctl.set_lcore_mask()
    changed |= ovsvsctl.set_socket_mem(args.mem)
    changed |= ovsvsctl.enable_dpdk()
    if changed:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
