#!/bin/bash

nameA='ACC20-A-important'
nameSM='acc20-sparkmaster'
nameSW='acc20-sparkworker1'
# nameSM='ACC20-SM-important'
# nameSW='ACC20-S-important'

source openrc.sh

# Store the list of openstack IPs in a file
echo "Obtaining openstack server list..."
openstack server list > serverlist

# Filter our VMs and get their IPs
full=$(grep $nameA -r serverlist)
ips=$(cut -d "=" -f 2 <<< $full)
privA=${ips:0:12}
floatingA=${ips:14:12}


full=$(grep $nameSM -r serverlist)
ips=$(cut -d "=" -f 2 <<< $full)
privSM=${ips:0:12}
floatingSM=${ips:14:12}


full=$(grep $nameSW -r serverlist)
ips=$(cut -d "=" -f 2 <<< $full)
privSW1=${ips:0:12}
floatingSW1=${ips:14:12}

# Remove unnecessary files
rm serverlist

echo "Filtered IPs from list"

# /etc/hosts For all nodes
echo "127.0.0.1 localhost
$privA ansible-node
$privSW1 sparkworker1
$privSM sparkmaster

# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts" > exampleHostFile

sudo cp exampleHostFile /etc/hosts
echo "Written to local /etc/hosts file"

scp exampleHostFile ubuntu@$floatingSM:/etc/hosts
scp exampleHostFile ubuntu@$floatingSW1:/etc/hosts
echo "Written to remote /etc/hosts files (SM and SW)"

# /etc/ansible/hosts only for ansible node
echo "ansible-node ansible_ssh_host=$privA
sparkmaster  ansible_ssh_host=$privSM
sparkworker1 ansible_ssh_host=$privSW1

[configNode]
ansible-node ansible_connection=local ansible_user=ubuntu

[sparkmaster]
sparkmaster ansible_connection=ssh ansible_user=ubuntu

[sparkworker]
sparkworker1 ansible_connection=ssh ansible_user=ubuntu" > exampleAnsibleHostsFile

sudo cp exampleAnsibleHostsFile /etc/ansible/hosts
echo "Written to local /etc/ansible/hosts file"





############ Manually get the floating IPs ###############

# read -p "Ansible Master Floating IP: " floatingAM
# read -p "Spark Master Floating IP: " floatingSM
# read -p "Spark Worker Floating IP: " floatingSW
