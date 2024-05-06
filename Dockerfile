# syntax=docker/dockerfile:1.4

## Build iPXE binaries from source
FROM cgr.dev/chainguard/wolfi-base AS builder
RUN apk add git gcc binutils make perl xz xz-dev build-base
RUN mkdir -p /tmp
WORKDIR /tmp
RUN git clone https://github.com/ipxe/ipxe.git
WORKDIR /tmp/ipxe/src/
RUN make bin/undionly.kpxe && \
       make bin-x86_64-efi/ipxe.efi && \
       cp -a bin/undionly.kpxe /tmp/ && \
       cp -a bin-x86_64-efi/ipxe.efi /tmp/

## Build dnsmasq-dhcp container image
FROM cgr.dev/chainguard/wolfi-base

RUN apk add dnsmasq

# Create the directory to store leases
RUN mkdir -p /var/lib/misc

# Create the directory to store the tftp files
RUN mkdir -p /var/lib/tftpboot
#Copy PXE files from builder stage
COPY --from=builder /tmp/undionly.kpxe /var/lib/tftpboot/
COPY --from=builder /tmp/ipxe.efi /var/lib/tftpboot/ipxe-x86_64.efi

VOLUME /etc/dnsmasq

EXPOSE 53 53/udp
EXPOSE 67 67/udp


ENTRYPOINT ["dnsmasq", "-k", "--log-dhcp", "--log-facility=-", "-R", "-h", "-C", "/etc/dnsmasq/dnsmasq.conf" ]
