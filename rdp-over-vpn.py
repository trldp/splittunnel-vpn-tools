#!/usr/bin/env python3

#
# Copyright (C) 2021 Tobe Deprez
# 
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>. 

import argparse
import Configuration
import ns
import openfortivpn
import os
import pwinput
import rdplib
import sys

parser = argparse.ArgumentParser(description=f'Set up RDP connection to {Configuration.RDP_HOST} over a VPN, set up '
                                 'inside a network namespace. '
                                 'This script requires root privileges to set up the network namespace and the VPN '
                                 'connection. In order to allow internet connection from inside the network namespace, '
                                 'one should allow forwarding between the host interfaces and the interface associated to '
                                 'the network namespace and vice versa. Run with --help-firewall for more details.')
parser.add_argument('screens', metavar='SCREENS', default=None, nargs='?',
                    help='The screens to use for the RDP connection. This should be a comma-separated list of screens.')
parser.add_argument('--help-firewall', action='store_true', help='Show help on how to set up the firewall rules.')
args = parser.parse_args()

if args.help_firewall:
    ns.print_firewall_help(Configuration.HOST_INTERFACES, Configuration.INTERFACE_OUT)
    sys.exit()

if os.geteuid() != 0:
    exit('You need to have root privileges to run this script.\n'
         'Please try again, this time using \'sudo\'. Exiting.')

password = pwinput.pwinput()

def set_up_rdp():
    rdplib.rdp(Configuration.RDP_HOST, Configuration.RDP_DOMAIN, Configuration.RDP_USER, password, 
               screens=sys.argv[1] if len(sys.argv) > 1 else None,
               fullscreen=True, multimonitor=True, network_namespace=Configuration.NS_NAME)

def set_up_openfortivpn(ns_exec):
    openfortivpn.set_up(Configuration.NS_NAME, Configuration.VPN_ENDPOINT, Configuration.VPN_USER, password, set_up_rdp)

ns.set_up(Configuration.NS_NAME, Configuration.HOST_INTERFACES, Configuration.INTERFACE_IN, Configuration.IP_IN, 
          Configuration.INTERFACE_OUT, Configuration.IP_OUT, command=set_up_openfortivpn)