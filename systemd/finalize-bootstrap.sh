#!/usr/bin/env bash

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

set -o nounset
set -o errexit
set -o pipefail

source /opt/cmframework/scripts/common.sh

rm -rf /etc/ansible-change_kernel_cmdline/enabled

if [ ! -f /etc/performance-nodes/dpdk.enabled ]
then
    if has_kernel_parameters_changed;
    then
       systemctl set-environment _INSTALLATION_SUCCESS='failed'
       log_installation_failure
    else
       systemctl set-environment _INSTALLATION_SUCCESS='success'
       log_installation_success
    fi
    systemctl start report-installation-success.service --no-block
fi
