read -p "Ansible Master Floating IP: " floatingAM
scp QTLaaSRequiredFiles/ ubuntu@$floatingAM:/home/ubuntu/
