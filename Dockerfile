# syntax=docker/dockerfile:1.4
FROM cgr.dev/chainguard/wolfi-base

RUN apk add dnsmasq

# Create the directory to store leases
RUN mkdir -p /var/lib/misc

# Create the directory to store the tftp files
RUN mkdir -p /var/lib/tftpboot

# Add the uefi ipxe binary to the tftp directory
# TODO: Find a palce to download the latest version for inclusion

VOLUME /etc/dnsmasq

EXPOSE 53 53/udp
EXPOSE 67 67/udp


ENTRYPOINT ["dnsmasq", "-k", "--log-dhcp", "--log-facility=-", "-R", "-h", "-C", "/etc/dnsmasq/dnsmasq.conf" ]
