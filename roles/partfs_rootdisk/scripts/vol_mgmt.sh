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

# This tool is meant to stop processes running in a given directory.
# Evacuate its contents to a temp location.
# Mount a given LVM to the Directory
# Start those services again

#arg1: Directory to evacuate
#arg2: Volume dev path to mount

exec >> /tmp/vol_mgmt_logfile
exec 2>&1


if [[ $# != 2 ]];then
  echo "Improper number of arguments passed!!"
  exit 1
fi

evac_dir=$1
mount_vol_dev=$2

echo "Trying to mount $mount_vol_dev on $evac_dir"

# Run partprobe to load new volumes
/usr/sbin/partprobe

if [ ! -d $evac_dir ];then
  echo "Provided directory $evac_dir does not exist, so lets create it."
  mkdir -p "$evac_dir"
fi

if [ ! -b $mount_vol_dev ];then
  echo "Provided volume $mount_vol_dev is not a block device!!"
  exit 1
fi

# check if given directory is already mounted from needed volume
df -k $evac_dir | grep $mount_vol_dev > /dev/null 2>&1
if [[ $? == 0 ]];then
  echo "$evac_dir is already mounted from $mount_vol_dev"
  exit 0
fi

running_process_list=`lsof | grep ${evac_dir} | awk -F " " {'print $2'}| uniq`
systemd_service_list=`systemctl --state=active --type=socket,service | grep "loaded active" | awk -F " " {'print $1'}`

declare -a matching_systemd_services
for process in ${running_process_list}; do
  for systemd_service in ${systemd_service_list}; do
    systemd_MainPID=`systemctl show -p MainPID ${systemd_service} | awk -F "MainPID=" {'print $2'}`
    if [[ $process == $systemd_MainPID ]];then
      matching_systemd_services+=(${systemd_service})
      break
    fi
  done
done

# Stop running services which were using old dir
echo "Stopping services ${matching_systemd_services[@]}"
for service_name in ${matching_systemd_services[@]}; do
  systemctl stop $service_name > /dev/null 2>&1
  if [[ $? != 0 ]];then
    service_base_name=`echo $service_name | awk -F ".service" {'print $1'}`
    service $service_base_name stop > /dev/null 2>&1
  fi

  service_wait_count=10
  systemd_status=0
  while [[ $service_wait_count != 0 && $systemd_status == 0 ]]; do
    echo "waiting for $service_name to stop"
    sleep 1
    ((service_wait_count--))
    systemctl status $service_name > /dev/null 2>&1
    systemd_status=$?
  done

  if [[ $service_wait_count == 0 ]];then
    echo "$service_name did not stop gracefully. Stopping it forcefully."
    systemctl -f stop $service_name > /dev/null 2>&1
  fi
done

# Move old dir contents to tmp location
tmp_dir="/tmp/`basename ${evac_dir}`"
mkdir -p $tmp_dir
cp -rpf ${evac_dir}/* $tmp_dir
rm -rf ${evac_dir}/*

# Mount the volume on dir
mount $evac_dir

cp -rpf $tmp_dir/* ${evac_dir}/
rm -rf $tmp_dir

# Start the services again
echo "Starting services ${matching_systemd_services[@]}"
for service_name in ${matching_systemd_services[@]}; do
  systemctl start $service_name > /dev/null 2>&1
done
