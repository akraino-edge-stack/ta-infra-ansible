#!/bin/bash
# Copyright 2019 Nokia
#
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
#

start()
{
    local iface vf_count
    local res=0

    for iface in $SRIOV_INTERFACES
    do
        vf_count=$SRIOV_VF_COUNT
        if [[ -z "$vf_count" ]]
        then
            if ! vf_count=$(</sys/class/net/$iface/device/sriov_totalvfs)
            then
                echo "Failed to get supported VF count for the interface $iface" >&2
                res=1
                continue
            fi
        fi

        echo "Creating $vf_count SR-IOV VFs for the interface $iface"
        if ! echo $vf_count > /sys/class/net/$iface/device/sriov_numvfs
        then
            echo "Failed to create SR-IOV VFs for the interface $iface" >&2
            res=1
        fi
    done

    return $res
}

stop()
{
    local iface
    local res=0

    for iface in $SRIOV_INTERFACES
    do
        echo "Removing SR-IOV VFs from the interface $iface"
        if ! echo 0 > /sys/class/net/$iface/device/sriov_numvfs
        then
            echo "Failed to remove SR-IOV VFs from the interface $iface" >&2
            res=1
        fi
    done

    return $res
}

main()
{
    local -r CONF_FILE="/etc/sriov/sriov.conf"
    local -r ACTION=$1

    if [[ $# -ne 1 || ! $ACTION =~ ^(start|stop)$ ]]
    then
        echo "usage: $0 [start|stop]" >&2
        return 1
    fi

    [[ -r $CONF_FILE ]] && source $CONF_FILE

    if [[ -n "$SRIOV_INTERFACES" ]]
    then
        $ACTION
    else
        echo "No SR-IOV interfaces to configure" >&2
        return 1
    fi
}

main "$@"
