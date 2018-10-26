# read -p "Connect to (A/SM/SW)? " id
#
# if [ $id = "A" ]; then
# 	echo "salu2"
# elif [ $id = "SM" ]; then
# 	echo "salu3"
# elif [ $id = "SW" ]; then
# 	echo "salu3"
# fi

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
    IdentityFile ~/.ssh/acc.pem" >> ~/.ssh/config
chmod 600 ~/.ssh/acc.pem

#Connect using ssh
floatingip=$(<~/.ssh/lastFloatingIP)
ssh ubuntu@$floatingip
