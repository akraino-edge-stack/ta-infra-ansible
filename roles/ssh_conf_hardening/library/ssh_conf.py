#!/bin/python

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

import os
import re
from ansible.module_utils.basic import AnsibleModule

class SshdConf(object):

    def __init__(self):
        self.module = AnsibleModule(argument_spec=dict(regexp=dict(required=True),
                                                       values=dict(required=True)))
        self.used_regexp = self.module.params["regexp"]
        self.set_values = self.module.params["values"]
        self.sshd_contents = None
        self.changed = False
        self.target = "/etc/ssh/sshd_config"

    def _read_sshd_conf(self):
        os.system("sync")
        with open(self.target, "r") as sshd_file:
            self.sshd_contents = sshd_file.readlines()

    def _write_sshd_conf(self):
        os.system("sync")
        os.remove(self.target)
        os.system("sync")
        for line in self.sshd_contents:
            with open(self.target, "a") as out:
                out.write(line)
                os.system("sync")
        os.system("sync")
        os.system("chmod 600 "+ self.target)
        os.system("sync")
        os.system("chown root:root "+ self.target)
        os.system("sync")

    def _start_finder(self):
        end = start = None
        index = 0

        for line in self.sshd_contents:
            if start is None and re.compile("^[A-Za-z].*").search(line):
                start = index + 1
            if re.compile("^[#\s]*Match ").search(line):
                end = index
                break
            index += 1

        if end is None:
            end = index - 1

        if start is None:
            start = 0

        return start, end

    def ssh_checker_and_setter(self, line):
        if self.changed:
            self.sshd_contents[line] = ''
        else:
            self.sshd_contents[line] = self.module.params["values"]
            self.changed = True

    def _configuration(self, start, end):
        for line in range(0, end):
            if re.compile("^"+self.module.params["regexp"]).search(self.sshd_contents[line]):
                self.ssh_checker_and_setter(line)
        if not self.changed:
            for line in range(0, end):
                if re.compile("^#"+self.module.params["regexp"]).search(self.sshd_contents[line]) and not self.changed:
                    self.sshd_contents[line] = self.sshd_contents[line]+self.module.params["values"]
                    self.changed = True
            if not self.changed:
                self.sshd_contents.insert(start, self.module.params["values"])
                self.changed = True

    def run(self):
        self._read_sshd_conf()

        indexes = self._start_finder()
        start_index = indexes[0]
        end_index = indexes[1]

        self._configuration(start_index, end_index)

        self._write_sshd_conf()

        self.module.exit_json(changed=self.changed, msg=self.module.params["values"]+" configured")

    @staticmethod
    def main():
        SshdConf().run()

if __name__ == '__main__':
    SshdConf.main()
