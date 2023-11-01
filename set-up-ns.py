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
import sys


parser = argparse.ArgumentParser(description=f'Set up a network namespace {Configuration.NS_NAME} with a single network '
                                 f'interface {Configuration.INTERFACE_IN} with IP address {Configuration.IP_IN}, connected '
                                 f'to the host interface {Configuration.INTERFACE_OUT} with IP address {Configuration.IP_OUT}. '
                                 'This script requires root privileges. '
                                 'In order to allow internet connection from inside the network namespace, '
                                 'one should allow forwarding between the host interfaces and the interface associated to '
                                 'the network namespace and vice versa. Run with --help-firewall for more details.')
parser.add_argument('--help-firewall', action='store_true', help='Show help on how to set up the firewall rules.')
args = parser.parse_args()

if args.help_firewall:
    ns.print_firewall_help(Configuration.HOST_INTERFACES, Configuration.INTERFACE_OUT)
    sys.exit()

if os.geteuid() != 0:
    exit('You need to have root privileges to run this script.\n'
         'Please try again, this time using \'sudo\'. Exiting.')

ns.set_up(Configuration.NS_NAME, Configuration.HOST_INTERFACES, Configuration.INTERFACE_IN, Configuration.IP_IN, 
          Configuration.INTERFACE_OUT, Configuration.IP_OUT)