FROM rockylinux:8.9
RUN dnf install -y dnsmasq procps-ng ipxe-bootimgs-x86 python3 python3-pip; dnf clean all;
COPY --chmod=644 --chown=dnsmasq:dnsmasq dnsmasq.conf /etc/dnsmasq.conf
COPY --chmod=555 --chown=dnsmasq:dnsmasq smd.py /bin/smd.py
COPY --chmod=555 --chown=dnsmasq:dnsmasq init.sh /bin/init.sh
COPY --chmod=555 --chown=dnsmasq:dnsmasq update_loop.sh /bin/update_loop.sh  
RUN pip3 install requests 

EXPOSE 67/udp
ENTRYPOINT init.sh

