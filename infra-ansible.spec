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

Name:           infra-ansible
Version:        %{_version}
Release:        9%{?dist}
Summary:        Contains ansible playbook and roles for Akraino rec blueprint
License:        %{_platform_licence}
Source0:        %{name}-%{version}.tar.gz
Vendor:         %{_platform_vendor}

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch

%description
This RPM contains Contains ansible playbook and roles for Akraino rec blueprint

%prep
%autosetup

%install
mkdir -p %{buildroot}/root/dev_tools
cp dev_tools/* %{buildroot}/root/dev_tools

mkdir -p %{buildroot}%{_playbooks_path}
cp playbooks/* %{buildroot}%{_playbooks_path}

# mkdir -p %{buildroot}%{_inventory_path}
# cp -rf inventory/* %{buildroot}%{_inventory_path}

mkdir -p %{buildroot}%{_roles_path}
cp -rf roles/* %{buildroot}%{_roles_path}

mkdir -p %{buildroot}/%{_finalize_path}
ln -sf %{_playbooks_path}/removevips.yml                              %{buildroot}/%{_finalize_path}
ln -sf %{_playbooks_path}/monitoring.yml                              %{buildroot}/%{_finalize_path}
ln -sf %{_playbooks_path}/redissync.yml                               %{buildroot}/%{_finalize_path}
ln -sf %{_playbooks_path}/ansiblesync.yml                             %{buildroot}/%{_finalize_path}
ln -sf %{_playbooks_path}/redisconfig.yml                             %{buildroot}/%{_finalize_path}
ln -sf %{_playbooks_path}/cmserverconfig.yml                          %{buildroot}/%{_finalize_path}

mkdir -p %{buildroot}/%{_secrets_path}
cp secrets/* %{buildroot}/%{_secrets_path}

# Create links for the bootstrapping phase
mkdir -p %{buildroot}/%{_bootstrapping_path}
ln -sf %{_playbooks_path}/initial_poweroff_hosts.yml         %{buildroot}/%{_bootstrapping_path}
ln -sf %{_playbooks_path}/partfs_rootdisk_inst_cont.yml      %{buildroot}/%{_bootstrapping_path}
ln -sf %{_playbooks_path}/ntp-config.yml                     %{buildroot}/%{_bootstrapping_path}

# Create links for the provisioning phase
mkdir -p %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/baremetal-install.yml              %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/partfs_rootdisk.yml                %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/allocate-cpu-cores.yml             %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/sriov_nodes.yaml                   %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/sriovdp_config.yaml                %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/performance-kernel-cmdline-set.yml %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/performance_nodes.yaml             %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/baremetal-interface-config.yml     %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/ntp-config.yml                     %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/rpm-database.yml                   %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/single_node_storage.yml            %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/ceph-deploy.yml                    %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/baremetal-interface-config.yml     %{buildroot}/%{_provisioning_path}
ln -sf %{_playbooks_path}/ntp-check.yml                      %{buildroot}/%{_provisioning_path}

# Create links for the postconfig phase
mkdir -p %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/synchonize_ssh_keys.yml                     %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/distributed-state-server-file-plugin.yml    %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/distributed-state-server-etcd-plugin.yml    %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/distributed-state-server.yml                %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/etcdansible.yml                             %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/core-handling.yml                           %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/dbwatchdog.yml                              %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/access-management.yml                       %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/accounts.yml                                %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/adminuserfile.yml                           %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/ansibleldconfig.yml                         %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/bare_lvm_backend.yml                        %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/baremetal-interface-config-post.yml         %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/certificate_update.yml                      %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/core-handling.yml                           %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/create-bash-command-auth-conf.yml           %{buildroot}/%{_postconfig_path}
# keepalive ln -sf %{_playbooks_path}/dbwatchdog.yml                              %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/disable-old-node-rsyslog.yml                %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/enablecmagent.yml                           %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/haproxy-install.yml                         %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/ipv6-config.yml                             %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/motd.yml                                    %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/hostcli.yml                                 %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/oom.yml                                     %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/openssh_server_conf_hardening.yml           %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/openstack-ansible-log-dir.yml               %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/operation_system_hardening.yml              %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/restful.yml                                 %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/root-openstack-admin-credentials.yml        %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/service-profiles.yml                        %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/setup_audit.yml                             %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/setup_in_host_traffic_filtering.yml         %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/synchonize_ssh_keys.yml                     %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/systemd_services.yml                        %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/userskeyssync.yml                           %{buildroot}/%{_postconfig_path}
ln -sf %{_playbooks_path}/baremetal-interface-config-post.yml         %{buildroot}/%{_postconfig_path}

ln -sf %{_roles_path}/baremetal_interface_config/templates/os_net_config.j2 %{buildroot}%{_roles_path}/bootstrap-host/templates/os_net_config.j2
ln -sf /opt/config-encoder-macros %{buildroot}%{_roles_path}/access-management/templates/encoder

mkdir -p %{buildroot}/usr/lib/systemd/system/
cp systemd/finalize-bootstrap.service %{buildroot}/usr/lib/systemd/system/
cp systemd/sriov.service %{buildroot}/usr/lib/systemd/system
cp systemd/report-installation-success.service %{buildroot}/usr/lib/systemd/system

mkdir -p %{buildroot}/opt/ansible-change_kernel_cmdline/
cp systemd/finalize-bootstrap.sh %{buildroot}/opt/ansible-change_kernel_cmdline/

mkdir -p %{buildroot}/opt/sriov
cp systemd/sriov.sh %{buildroot}/opt/sriov

%files
%attr(0755,root,root) %{_playbooks_path}/report-installation-progress
%attr(0755,root,root) %{_playbooks_path}/report-installation-success.sh
%defattr(0644,root,root,0755)
/root/dev_tools
%{_playbooks_path}/*
# %{_inventory_path}/*
%{_roles_path}/*
%{_bootstrapping_path}/*
%{_provisioning_path}/*
%{_postconfig_path}/*
%{_finalize_path}/*
%{_secrets_path}/*
%attr(0755,root,root) /usr/lib/systemd/system/*
%attr(0755,root,root) /opt/ansible-change_kernel_cmdline/finalize-bootstrap.sh
%attr(0755,root,root) /opt/sriov/sriov.sh

%post
for role in /usr/share/ceph-ansible/roles/*; do
  ln -sf $role /etc/ansible/roles/
done
mkdir -p /etc/ansible/roles/plugins/library
for module in /usr/share/ceph-ansible/library/*.py*; do
  ln -sf $module /etc/ansible/roles/plugins/library
done
systemctl enable sriov

%preun

%postun

%clean
rm -rf ${buildroot}
