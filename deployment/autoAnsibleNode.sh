apt install python-minimal # This should be installed already when creating the machine using the cloud-init script

# Install Ansible in the Ansible Master node
./ansible_install.sh
ansible-playbook -s spark_deployment.yml

# Add the IP-address and hostname of the Ansible Master, Spark Master and Spark Worker to /etc/hosts file in Ansible Master node.
read -p "Ansible Master Floating IP: " floatingAM
read -p "Spark Master Floating IP: " floatingSM
read -p "Spark Worker Floating IP: " floatingSW # This works for one Spark Worker for now

# Not sure if this is the correct syntax for the IP thing
echo "ansible-node ansible_ssh_host=$floatingAM
	  	sparkmaster  ansible_ssh_host=$floatingSM
	  	sparkworker ansible_ssh_host=$floatingSW" >> /etc/hosts

# Generate a SSH-key pair in Ansible Master node
echo 'ansibleNodeKey' | ssh-keygen -t rsa
cp ansibleNodeKey* ~/.ssh/

# Copy its public part to ~/.ssh/authorized_keys in all the Spark nodes.
cat ~/.ssh/ansibleNodeKey.pub >> ~/.ssh/authorized_keys

# TODO: Not sure yet if these remote ones work, have to test it
cat ~/.ssh/ansibleNodeKey.pub | ssh ubuntu@$floatingSM 'dd of=.ssh/authorized_keys oflag=append conv=notrunc'
cat ~/.ssh/ansibleNodeKey.pub | ssh ubuntu@$floatingSW 'dd of=.ssh/authorized_keys oflag=append conv=notrunc'

# Edit /etc/ansible/hosts using example-hosts-file available in the reprository. (Add
# [sparkmaster] followed by the name of sparkmaster node in the next line. Add [sparkworker]
# followed by the names of sparkworkers in the next lines, one per line).
echo "ansible-node ansible_ssh_host=$floatingAM
	  	sparkmaster  ansible_ssh_host=$floatingSM
	  	sparkworker ansible_ssh_host=$floatingSW

			[configNode]
			ansible-node ansible_connection=local ansible_user=ubuntu

			[sparkmaster]
			sparkmaster ansible_connection=ssh ansible_user=ubuntu

			[sparkworker]
			sparkworker1 ansible_connection=ssh ansible_user=ubuntu" >> /etc/ansible/hosts

ansible-playbook -s spark_deployment.yml
