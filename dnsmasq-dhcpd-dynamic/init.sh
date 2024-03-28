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
dhcp-option=tag:PXEBOOT,tag:!IPXEBOOT,option:bootfile-name,ipxe-x86_64.efi
EOF

smd.py
update_loop.sh &
dnsmasq -k -d --log-dhcp
