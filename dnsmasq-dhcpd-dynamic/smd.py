#!/usr/bin/env python3
import requests
import os
import filecmp
import shutil
import sys
import tempfile
def getSMD(url):
    r = requests.get(url)
    data = r.json()
    return data

def getNID(c_data, xname):
    if 'node_prefix' in os.environ:
        node_prefix = os.environ['node_prefix']
    else:
        node_prefix="nid"
    for c in c_data:
        if xname == c['ID']:
            return node_prefix+'%0*d' % (3, c['NID'])
    else:
        return None

def main():
    sighup = False
    smd_endpoint=os.environ['smd_endpoint']
    smd_port=os.environ['smd_port']
    bss_endpoint=os.environ['bss_endpoint']
    bss_port=os.environ['bss_port']
    ei_data = getSMD(f'http://{smd_endpoint}:{smd_port}/hsm/v2/Inventory/EthernetInterfaces')
    component_data = getSMD(f"http://{smd_endpoint}:{smd_port}/hsm/v2/State/Components")['Components']
    #hostsfile = tempfile.TemporaryFile(mode = "r+")
    hostsfile = open("/etc/dhcp-hostsfile-new", "w")
    #this for loop writes host entries
    for i in ei_data:
        if i['Type'] != 'NodeBMC':
            nidname=getNID(component_data, i['ComponentID'])
            if nidname:
                print(f"{i['MACAddress']},set:{nidname},{i['IPAddresses'][0]['IPAddress']},{nidname}", file=hostsfile)
            else:
                print(f"{i['MACAddress']},set:{i['ComponentID']},{i['IPAddresses'][0]['IPAddress']},{i['ComponentID']}", file=hostsfile)
        else:
           print(f"{i['MACAddress']},{i['IPAddresses'][0]['IPAddress']},{i['ComponentID']}", file=hostsfile)
    hostsfile.close()
    if os.path.isfile("/etc/dhcp-hostsfile") == False or filecmp.cmp("/etc/dhcp-hostsfile-new", "/etc/dhcp-hostsfile") == False:
        sighup = True
        shutil.copyfile("/etc/dhcp-hostsfile-new", "/etc/dhcp-hostsfile")
    #TODO actually map all the BMCs straight from redfish, instead of creating dummy endpoints for them.
    #rf_data = getSMD(f'http://{smd_endpoint}:27779/hsm/v2/Inventory/RedfishEndpoints')
    #for r in rf_data['RedfishEndpoints']:
    #    print(r['ID'] + ' ' + r['IPAddress'])
    #optsfile = tempfile.TemporaryFile(mode = "r+")
    optsfile = open("/etc/dhcp-optsfile-new", "w")
    #this for loop writes option entries, we wouldn't need it if the BSS wasn't MAC specific
    for i in ei_data:
      if 'bmc' not in i['Description']:
          nidname=getNID(component_data, i['ComponentID'])
          if nidname:
              print(f"tag:{nidname},tag:IPXEBOOT,option:bootfile-name,\"http://{bss_endpoint}:{bss_port}/boot/v1/bootscript?mac={i['MACAddress']}\"", file=optsfile)
          else:
              print(f"tag:{i['ComponentID']},tag:IPXEBOOT,option:bootfile-name,\"http://{bss_endpoint}:{bss_port}/boot/v1/bootscript?mac={i['MACAddress']}\"", file=optsfile)
    optsfile.close()
    if os.path.isfile("/etc/dhcp-optsfile") == False or filecmp.cmp("/etc/dhcp-optsfile-new","/etc/dhcp-optsfile") == False:
        sighup = True
        shutil.copyfile(optsfile.name, "/etc/dhcp-optsfile")

    if sighup:
       print("newfile!")
       sys.exit(1)
    else:
       sys.exit(0)

if __name__ == "__main__":
    main()
