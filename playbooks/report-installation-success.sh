#!/bin/bash

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

MAX_TRIES=5
COUNT=0
while [ $COUNT -lt $MAX_TRIES ]; do
    if [ "$_INSTALLATION_SUCCESS" == "success" ]; then
        /opt/openstack-ansible/playbooks/report-installation-progress --status completed --description "Installation complete" --percentage 100
    else
        /opt/openstack-ansible/playbooks/report-installation-progress --status failed --description "Installation failed"
    fi

    if [ "$?" -eq 0 ]; then
        exit 0
    fi
    sleep 10
    let COUNT=COUNT+1
done

exit 1
