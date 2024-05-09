#!/usr/bin/env python3
import requests
import os
import filecmp
import shutil
import sys
import tempfile 
import signal
import time
import sys
import argparse
import logging

# This script needs an auth token and must be able to renew that token on use.

def getSMD(url, AccessToken=None):
    if AccessToken:
        headers = {'Authorization' : f'Bearer {AccessToken}'}
        r = requests.get(url, headers=headers)
    else:
        r = requests.get(url)
    try:
        data = r.json()
        return data
    except:
        if r.status_code == 401:
            print(f"Error: {r.status_code} {r.reason} when querying {url}.  Please check your access token.")
            sys.exit(1)
        else:
            print(f"Error: {r.status_code} {r.reason} when querying {url}")
            sys.exit(1)

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

def template_file(base_url, access_token, hostsfilename, optsfilename):
    ei_data = getSMD(f'{base_url}/hsm/v2/Inventory/EthernetInterfaces',access_token)
    component_data = getSMD(f"{base_url}/hsm/v2/State/Components", access_token)['Components']
    logging.warning(f"Retrieved {len(ei_data)} EthernetInterfaces and {len(component_data)} Components from {base_url}")
    hostsfile = open(hostsfilename, "w")
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
    logging.warning(f"Generated {hostsfilename}")

    #TODO actually map all the BMCs straight from redfish, instead of creating dummy endpoints for them.
    #rf_data = getSMD(f'http://{smd_endpoint}:27779/hsm/v2/Inventory/RedfishEndpoints')
    #for r in rf_data['RedfishEndpoints']:
    #    print(r['ID'] + ' ' + r['IPAddress'])
    #optsfile = tempfile.TemporaryFile(mode = "r+")
    optsfile = open(optsfilename, "w")
    #this for loop writes option entries, we wouldn't need it if the BSS wasn't MAC specific
    for i in ei_data:
      if 'bmc' not in i['Description']:
          nidname=getNID(component_data, i['ComponentID'])
          if nidname:
              print(f"tag:{nidname},tag:IPXEBOOT,option:bootfile-name,\"{base_url}/boot/v1/bootscript?mac={i['MACAddress']}\"", file=optsfile)
          else:
              print(f"tag:{i['ComponentID']},tag:IPXEBOOT,option:bootfile-name,\"{base_url}/boot/v1/bootscript?mac={i['MACAddress']}\"", file=optsfile)
    optsfile.close()
    logging.warning(f"Generated {optsfilename}")



# Define the signal handler function
def signal_handler(signum, frame):
    print(f"Received signal {signum}, exiting...")
    sys.exit(0)

def main():
    # Register the signal handler for common Unix signals
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler) # Termination signal

    parser = argparse.ArgumentParser(description='Regenerate DHCP files')
    parser.add_argument('--base-url', help='Base URL for OpenCHAMI endpoint.  This flag will override the OCHAMI_BASEURL environment variable.')
    parser.add_argument('--access-token', help='Access token for OpenCHAMI endpoint This flag will override the OCHAMI_ACCESS_TOKEN environment variable.')
    parser.add_argument('--hosts-file', help='Path to the hosts file', default='/configs/site/hosts/hostsfile')
    parser.add_argument('--opts-file', help='Path to the options file', default='/configs/site/opts/optsfile')
    
    args = parser.parse_args()

    if args.base_url:
        if os.environ.get('OCHAMI_BASEURL') is not None:
            logging.warning(f'Configuring base_url based on flag value of "{args.base_url}" Ignoring OCHAMI_BASEURL which is "{os.environ["OCHAMI_BASEURL"]}"')
        else:
            logging.warning(f'Configuring base_url based on flag value of "{args.base_url}"')
        base_url = args.base_url
    else:
        if os.environ.get('OCHAMI_BASEURL') is not None:
            logging.warning(f'Configuring base_url based on OCHAMI_BASEURL which is "{os.environ["OCHAMI_BASEURL"]}"')
            base_url = os.environ['OCHAMI_BASEURL']
        else:
            logging.warning(f'Configuring base_url based on default value of "http://localhost"')  
            base_url = 'http://localhost'

    if args.access_token:
        if os.environ.get('OCHAMI_ACCESS_TOKEN') is not None:
            logging.warning(f'Configuring access_token based on flag value of "{args.access_token}" Ignoring OCHAMI_ACCESS_TOKEN which is "{os.environ["OCHAMI_ACCESS_TOKEN"]}"')
        else:
            logging.warning(f'Configuring access_token based on flag value of "{args.access_token}"')
        access_token = args.access_token
    else:
        if os.environ.get('OCHAMI_ACCESS_TOKEN') is not None:
            logging.warning(f'Configuring access_token based on OCHAMI_ACCESS_TOKEN which is "{os.environ["OCHAMI_ACCESS_TOKEN"]}"')
            access_token = os.environ['OCHAMI_ACCESS_TOKEN']
        else:
            logging.warning(f'Configuring access_token based on default value of None')  
            access_token = None


    # Main loop to run template_file() every minute
    while True:
        try:
            template_file(base_url, access_token, args.hosts_file, args.opts_file)  # Execute the subroutine
            time.sleep(60)  # Wait for 60 seconds (1 minute)
        except KeyboardInterrupt:
            print("KeyboardInterrupt received, exiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
