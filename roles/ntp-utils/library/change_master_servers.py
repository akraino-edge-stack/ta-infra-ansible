#!/bin/env python
# pylint: skip-file
from ansible.module_utils.basic import AnsibleModule
import os
import re

if __name__ == '__main__':
    fields = {
            "new_ntp_servers": {"required":True, "type": list},
    }

    module = AnsibleModule(argument_spec=fields)

    new_ntp_servers = module.params['new_ntp_servers']

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
                if filter.match(line):
                    continue
                else:
                    updated.append(line)

            with open(tmp_file, 'w') as f:
                for line in updated:
                    f.write(line)

                #append the new server configuration
                for server in new_ntp_servers:
                    f.write("server " + server + "\n");

            os.rename(tmp_file, ntp_file)

            module.exit_json(changed=True)
                    
    except Exception as exp:
        module.fail_json(msg=str(ex))
