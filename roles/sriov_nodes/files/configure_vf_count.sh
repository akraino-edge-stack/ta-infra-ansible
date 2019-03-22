#!/bin/bash
set -e

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

set_max_vf_count()
{
    local iface vf_count device
    iface=$1
    vf_count=$2

    echo "Setting interface $iface max vf count to $vf_count"
    device=$(/bin/mst status -v | grep -E "net-${iface}[[:space:]]+" | awk '{print $2}')
    /bin/mlxconfig --yes --dev $device set NUM_OF_VFS=$vf_count
}

main()
{
    local -r CONF_FILE="/etc/sriov/sriov.conf"
    local res=0
    local mst_started=0
    local item iface vf_count

    [[ -r $CONF_FILE ]] && source $CONF_FILE

    if [[ -n "$SRIOV_VF_COUNTS" ]]
    then
        for item in $SRIOV_VF_COUNTS
        do
            iface=${item%:*}
            vf_count=${item##*:}
            if /sbin/ethtool -i $iface | grep -qE '^driver:[[:space:]]+mlx5_core$'
            then
                old_count=$(</sys/class/net/$iface/device/sriov_totalvfs)
                [[ $old_count -eq $vf_count ]] && continue
                [[ $mst_started -eq 0 ]] && /bin/mst start
                mst_started=1
                set_max_vf_count $iface $vf_count
                res=2
            fi
        done
    fi

    return $res
}

main "$@"
