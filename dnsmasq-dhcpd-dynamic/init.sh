#!/bin/bash

# Check for needed ENV variables
env_check=0
if [[ -z ${NTP_SERVER+x} ]]
then
	echo "NTP_SERVER is not set!"
	env_check=1
fi
if [[ -z ${OPTION_ROUTER+x} ]]
then
        echo "OPTION_ROUTER is not set!"
        env_check=1
fi
if [[ -z ${DNS_SERVERS+x} ]]
then
        echo "DNS_SERVERS is not set!"
        env_check=1
fi
if [[ -z ${DHP_RANGE+x} ]]
then
        echo "DHCP_RANGE is not set!"
        env_check=1
fi
if [[ -z ${DHCP_NETMASK+x} ]]
then
        echo "DHCP_NETMASK is not set!"
        env_check=1
fi
if [[ -z ${BOOTFILE_NAME+x} ]]
then
        echo "BOOTFILE_NAME is not set!"
        env_check=1
fi

# Exit if any ENV variables are missing
if [[ env_check -eq 1 ]]
then
	echo "Missing requried ENV variables, Exiting"
	exit 1
fi

# ENV variables that if not set have some default value
if [[ -z ${NODE_PREFIX+X} ]]
then
        echo "NODE_PREFIX is not set!"
        echo "Using default prefix 'nid'"
	NODE_PREFIX="nid"
fi

if [[ -z ${SMD_ENDPOINT+X} ]]
then
        echo "SMD_ENDPOINT is not set!"
        echo "Using default value 'localhost'"
	SMD_ENDPOINT="localhost"
fi

if [[ -z ${SMD_PORT+X} ]]
then
        echo "SMD_PORT is not set!"
        echo "Using default value '27779'"
        SMD_PORT="27779"
fi

if [[ -z ${BSS_ENDPOINT+X} ]]
then
        echo "BSS_ENDPOINT is not set!"
        echo "Using default value 'localhost'"
        BSS_ENDPOINT="localhost"
fi

if [[ -z ${BSS_PORT+X} ]]
then
        echo "BSS_PORT is not set!"
        echo "Using default value '27778'"
        BSS_PORT="27778"
fi

# Write dnsmasq-dhcp config file
cat > /etc/dnsmasq.d/dhcp.conf << EOF
dhcp-option=option:domain-search,.local
dhcp-option=option:ntp-server,${NTP_SERVER}
dhcp-option=option:router,${OPTION_ROUTER}
dhcp-option=option:dns-server,${DNS_SERVERS}
dhcp-range=${DHCP_RANGE}
dhcp-option=option:mtu,1500
dhcp-hostsfile=/etc/dhcp-hostsfile
dhcp-optsfile=/etc/dhcp-optsfile
enable-tftp
tftp-root=/usr/share/ipxe/
dhcp-match=IPXEBOOT,175
dhcp-match=PXEBOOT,60
dhcp-option=tag:PXEBOOT,tag:!IPXEBOOT,option:bootfile-name,${BOOTFILE_NAME}
dhcp-option=option:netmask,${DHCP_NETMASK}
EOF

# Run the update script
update_loop.sh &

# Run dnsmasq
dnsmasq -k -d --log-dhcp
