read -p "Use last IP? " -r
if [[ $REPLY =~ ^[Nn]$ ]]; then

	rm ~/.ssh/known_hosts

	# New floating IP
	read -p "Floating IP: " floating
	if [ -f ~/.ssh/lastFloatingIP ]
	then
	    rm ~/.ssh/lastFloatingIP
	fi
	echo "$floating" >> ~/.ssh/lastFloatingIP
	if [ -f ~/.ssh/config ]
	then
	    rm ~/.ssh/config
	fi
fi

echo "Host $floating
    IdentityFile ~/.ssh/acc20.pem" >> ~/.ssh/config
chmod 600 ~/.ssh/acc20.pem

#Connect using ssh
floatingip=$(<~/.ssh/lastFloatingIP)
ssh ubuntu@$floatingip
