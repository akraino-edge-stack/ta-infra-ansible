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

exec >> /tmp/old_vol_rm_logfile
exec 2>&1

lvm_paths=`lvs --noheadings -o vg_name,lvname,lv_dmpath`

if [[ $lvm_paths ]];then

  echo "Already available lvm_paths:"
  echo "$lvm_paths"

  while read -r -a lvm_path; do
    grep ${lvm_path[2]} /etc/fstab > /dev/null 2>&1
    if [[ $? != 0 ]];then
      lvm_rm_path=`echo ${lvm_path[0]}/${lvm_path[1]}`
      echo "Removing LVM $lvm_rm_path"
      sudo lvremove -f $lvm_rm_path
    fi
  done

else
    echo "No logical volumes to remove (lvm_paths: \"${lvm_paths}\")."
    exit 0
fi <<< "$lvm_paths"
