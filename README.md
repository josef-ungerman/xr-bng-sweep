# bng-sweep
Sweep XR BNG config & package out of Cisco ASR9000 temporarily (commit it for later rollback).

PURPOSE: Remove XR BNG config from 'show running-config' & uninstall bng rpm
 - parse IOS-XR BNG config file (first argument)
 - identify BNG-related configs
 - render the config that removes any BNG configs and package
 - print it to stdout and to a list for use with Netmiko

 USAGE: bng_sweep.py bng-config.txt bng-install.txt

