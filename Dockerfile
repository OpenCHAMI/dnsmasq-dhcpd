# syntax=docker/dockerfile:1.4
FROM cgr.dev/chainguard/wolfi-base

RUN apk add dnsmasq

# Add the uefi ipxe binary to the tftp directory
# TODO: Find a palce to download the latest version for inclusion

VOLUME /etc/dnsmasq

EXPOSE 53 53/udp
EXPOSE 67 67/udp


ENTRYPOINT ["dnsmasq", "-k", "--log-dhcp", "--log-facility=-"]
