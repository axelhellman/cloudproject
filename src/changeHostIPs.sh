#!/bin/bash

nameA='ACC20-A-important'
nameSM='acc20-sparkmaster'
nameSW='acc20-sparkworker'

declare -a floatingIPs=()
#nameSM='ACC20-SM-important'
#nameSW='ACC20-S-important'

source openrc.sh

# Store the list of openstack IPs in a file
echo "Obtaining openstack server list..."
openstack server list > serverlist

# Filter our VMs and get their IPs
full=$(grep $nameA -r serverlist)
ips=$(cut -d "=" -f 2 <<< $full)
privA=${ips:0:12}
floatingA=${ips:14:12}
if [ -z "$privA" ]
then
  privA='none'
fi

full=$(grep $nameSM -r serverlist)
ips=$(cut -d "=" -f 2 <<< $full)
privSM=${ips:0:12}
floatingSM=${ips:14:12}
if [ -z "$privSM" ]
then
  privSM='none'
fi

# Variable workers
hostContent=$"127.0.0.1 localhost
$privA ansible-node
$privSM sparkmaster"

hostAnsibleContent=$"ansible-node ansible_ssh_host=$privA
sparkmaster  ansible_ssh_host=$privSM"

hostAnsibleContentSecond=$"
[configNode]
ansible-node ansible_connection=local ansible_user=ubuntu

[sparkmaster]
sparkmaster ansible_connection=ssh ansible_user=ubuntu"

COUNTER=1
while [ $COUNTER -lt 10 ]; do
  newWorker="$nameSW$COUNTER"
  full=$(grep $newWorker -r serverlist)
  if [ -z "$full" ]
  then
    let COUNTER=15 # or break???
  else
    ips=$(cut -d "=" -f 2 <<< $full)
    privSW=${ips:0:12}
    floatingSW=${ips:14:12}

    floatingIPs=( "${floatingIPs[@]}" "$floatingSW" )

    # etc/hosts file
    singleLine="$privSW sparkworker$COUNTER"
    hostContent=${hostContent}'\n'${singleLine}

    # etc/ansible/hosts file
    singleLine="sparkworker$COUNTER ansible_ssh_host=$privSW"
    singleLineSecond="[sparkworker$COUNTER]
    sparkworker$COUNTER ansible_connection=ssh ansible_user=ubuntu"
    hostAnsibleContent=${hostAnsibleContent}'\n'${singleLine}
    hostAnsibleContentSecond=${hostAnsibleContentSecond}'\n'${singleLineSecond}
  fi
  	let COUNTER=COUNTER+1
done

######################/etc/hosts file########################

hostContentEnd="
# The following lines are desirable for IPv6 capable hosts
::1 ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts"

echo -e "$hostContent$hostContentEnd" > exampleHostFile

##############################################

# Remove unnecessary files
rm serverlist

echo "Filtered IPs from list"

sudo cp exampleHostFile /etc/hosts || true
echo "Written to local /etc/hosts file"

# for i in "${floatingIPs[@]}"
# do
#    echo "$i"
#    scp exampleHostFile ubuntu@"$i":/etc/hostsecho
# done
# scp exampleHostFile ubuntu@$floatingSM:/etc/hosts
# echo "Written to remote /etc/hosts files (SM and SW)"

scp exampleHostFile ubuntu@$floatingSM:/etc/hosts

######################/etc/ansible/hosts file########################

echo -e "$hostAnsibleContent$hostAnsibleContentSecond" > exampleAnsibleHostsFile

sudo cp exampleAnsibleHostsFile /etc/ansible/hosts || true
echo "Written to local /etc/ansible/hosts file"





############ Manually get the floating IPs ###############

# read -p "Ansible Master Floating IP: " floatingAM
# read -p "Spark Master Floating IP: " floatingSM
# read -p "Spark Worker Floating IP: " floatingSW
