#!/bin/env python
# pylint: skip-file
from ansible.module_utils.basic import *
import os, json
import re, sys
import syslog
import re

if __name__ == '__main__':
    fields = {
            "server_extra_params": {"required":True, "type": str},
    }

    module = AnsibleModule(argument_spec=fields)

    server_extra_params = module.params['server_extra_params']

    ntp_file = "/etc/ntp.conf"
    tmp_file = "/etc/ntp.conf.mod"

    try:
        filter = re.compile('^server.*')
        lines = []
        with open(ntp_file, 'r') as f:
            lines = f.readlines()

        updated = []
        if lines:
            for line in lines:
                if filter.match(line) and line.find(server_extra_params) == -1:
                    tmp = line.split('\n')[0]
                    tmp = tmp + " " + server_extra_params + '\n'
                    updated.append(tmp)
                else:
                    updated.append(line)

            with open(tmp_file, 'w') as f:
                for line in updated:
                    f.write(line)

            os.rename(tmp_file, ntp_file)

            module.exit_json(changed=True)
                    
    except Exception as exp:
        module.fail_json(msg=str(ex))
