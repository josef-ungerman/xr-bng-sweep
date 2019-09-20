#!/usr/bin/python3
#
# Contact: josef.ungerman@cisco.com
#
# PURPOSE: Remove XR BNG config from 'show running-config'
# - parse IOS-XR BNG config file (first argument)
# - identify BNG-related configs
# - render the config that removes any BNG configs and package
# - print it to stdout and to a list for Netmiko
#
# USAGE: bng_sweep.py bng-config.txt bng-install.txt

import re
import sys
from netmiko import ConnectHandler

DEBUG = 0

cfg = []
ins = []
deconfigure_bng = []
uninstall_bng = []

box = {
    'device_type': 'cisco_xr',
    'ip':   'sbx-iosxr-mgmt.cisco.com',
    'username': 'admin',
#    'password': '',
    'port' : 8181,
    'global_delay_factor': 4,
    'timeout': 600
}

#########################
def grab_cfg():
    bng = ConnectHandler(**box)

    ins = bng.send_command('show install active')
    print(ins)

    cfg = bng.send_command('show running-config')
    c = cfg.splitlines()

    bng.disconnect()
    return(c)

def send_cfg(deconfig, uninstall):
    print ("-----Opening ssh...")
    bng = ConnectHandler(**box)

    rt=""
    c=0
    for set in deconfig:
      c=c+1
      print ("-----Sending the deconfig SECTION",c,"-",len(set),"lines...")
      #print(s)
      rt = bng.send_config_set(set)
      print(rt)

    print ("-----Verifying before commit...")
    rt = bng.send_command('root')
    rt = bng.send_command('show config')
    print(rt)

    print ("-----Trying to commit...")
    #rt = bng.send_command('commit')
    #print(rt)

    print ("-----Trying to uninstall the bng rpm...")
    rt = bng.send_command(uninstall)
    print(rt)

    print ("-----Closing ssh...")
    #bng.disconnect()


############################
def read_cfg(f1,f2):
    f = open(f1,'r')
    for l in f: cfg.append(l)
    f = open(f2,'r')
    for l in f: ins.append(l)

#####################
def findline(cli, expr, dict, sect):
    found=re.findall(expr, cli)
    if found:
        if DEBUG: print("Found under",sect,":",found)
        if not sect in dict: dict[sect]=[]
        dict[sect].append(cli)
        return(1)

#####################
read_cfg(sys.argv[1], sys.argv[2])

bngcfg = {}
section = "start"

for line in cfg:
    line=line.strip()
    intf=re.findall("^interface (.+)", line)
    if intf: section=line

    if findline(line, "service-policy type control subscriber (.+)", bngcfg, section): continue
    if findline(line, "pppoe enable", bngcfg, section): continue
    if findline(line, "ipsubscriber ip(.+)", bngcfg, section): continue

    if findline(line, "^pppoe bba-group (.+)", bngcfg, "BBA"): continue
    if findline(line, "^policy-map type control subscriber (.+)", bngcfg, "PM"): continue
    if findline(line, "^class-map type control subscriber match-any (.+)", bngcfg, "CM"): continue

s=0
for i in bngcfg:
    if not re.findall("^interface (.+)", i): continue
    deconfigure_bng.append([])
    print(i)
    deconfigure_bng[s].append(i)
    for j in bngcfg[i]:
        j=" no "+j
        print(j)
        deconfigure_bng[s].append(j)
    print(" shutdown")
    deconfigure_bng[s].append(" shutdown")
    s=s+1
    print("!")

sections_order=["BBA","PM","CM"]
for i in sections_order:
    deconfigure_bng.append([])
    print("!")
    for j in bngcfg[i]:
        j="no "+j
        print(j)
        deconfigure_bng[s].append(j)
    s=s+1

for line in ins:
    line=line.strip()
    pkg=re.findall("(asr9k-bng-.+)", line)
    if pkg:
        print()
        print("install deactivate",pkg[0])
        print()
        uninstall_bng.append(pkg[0])
        uninstall_bng.append("Y")
        break

#send_cfg(deconfigure_bng, uninstall_bng)
