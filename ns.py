#
# Copyright (C) 2023 Tobe Deprez
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

from sh import ip, iptables, sysctl, mkdir
import shutil
import sys
import textwrap

def create_namespace(name, host_interfaces, interface_in, ip_in, interface_out, ip_out):
    # create the network namespace
    ip('netns', 'add', name)
    ns_exec = ip.bake('netns', 'exec', name)

    # start the loopback interface in the namespace
    ns_exec('ip', 'addr', 'add', '127.0.0.1/8', 'dev', 'lo')
    ns_exec('ip', 'link', 'set', 'lo', 'up')

    # create virtual network interfaces that will let OpenFortiVPN (in the
    # namespace) access the real network, and configure the interface in the
    # namespace (interface_in) to use the interface out of the namespace (interface_out)
    # as its default gateway
    ip('link', 'add', interface_out, 'type', 'veth', 'peer', 'name', interface_in)
    ip('link', 'set', interface_out, 'up')
    ip('link', 'set', interface_in, 'netns', name, 'up')

    ip('addr', 'add', f'{ip_out}/24', 'dev', interface_out)
    ns_exec('ip', 'addr', 'add', f'{ip_in}/24', 'dev', interface_in)
    ns_exec('ip', 'link', 'set', 'dev', interface_in, 'mtu', 1492)
    ns_exec('ip', 'route', 'add', 'default', 'via', ip_out, 'dev', interface_in)

    # make sure ipv4 forwarding is enabled
    sysctl('-w', 'net.ipv4.ip_forward=1')

    mkdir('-p', f'/etc/netns/{name}')
    with open(f'/etc/netns/{name}/resolv.conf', 'w') as f:
        f.write('nameserver 8.8.8.8\n'
                'nameserver 8.8.4.4\n')
        
    for interface in host_interfaces:
        iptables('-t', 'nat', '-A', 'POSTROUTING', '-o', interface, '-m', 'mark', '--mark', '0x29a', '-j', 'MASQUERADE')
    iptables('-t', 'mangle', '-A', 'PREROUTING', '-i', interface_out, '-j', 'MARK', '--set-xmark', '0x29a/0xffffffff')

    return ns_exec

def remove_namespace(name, host_interfaces, interface_in, interface_out):
    #Clear NAT
    for interface in host_interfaces:
        iptables('-t', 'nat', '-D', 'POSTROUTING', '-o', interface, '-m', 'mark', '--mark', '0x29a', '-j', 'MASQUERADE')
    iptables('-t', 'mangle', '-D', 'PREROUTING', '-i', interface_out, '-j', 'MARK', '--set-xmark', '0x29a/0xffffffff')

    #Deleting network interface
    shutil.rmtree(f'/etc/netns/{name}')

    ip('link', 'delete', interface_out)
    ip('netns', 'delete', name)

def set_up(ns_name, host_interfaces, interface_in, ip_in, interface_out, ip_out, command=None):
    try:
        print(f'Adding network interface {interface_in} in namespace {ns_name}')
        ns_exec = create_namespace(ns_name, host_interfaces, interface_in, ip_in, interface_out, ip_out)
        if command is not None:
            command(ns_exec=ns_exec)
        else:
            print(f'Network interface {interface_in} is up and running in namespace {ns_name}. Run commands in the namespace using\n'
                  f'  sudo ip netns exec {ns_name} <command>')
            input('Press enter to stop the network namespace and remove the network interface...')
    except KeyboardInterrupt:
        print('Keyboard interrupt detected. Attempting graceful shutdown of network namespace. '
              'Press ctrl+c again to stop the process immediately.')
    except Exception as e:
        print(f'Error occured: {e}', file=sys.stderr)
    finally:
        remove_namespace(ns_name, host_interfaces, interface_in, interface_out)
        print(f'Network interface {ns_name} and all its related interfaces have been removed.')

def print_firewall_help(host_interfaces, interface_out):
    ufw_commands = []
    iptables_commands = []
    for host_interface in host_interfaces:
        ufw_commands += [f'sudo ufw route allow in on {interface_out} out on {host_interface}',
                         f'sudo ufw route allow in on {host_interface} out on {interface_out}']
        iptables_commands += [f'sudo iptables -A FORWARD -i {interface_out} -o {host_interface} -j ACCEPT',
                              f'sudo iptables -A FORWARD -i {host_interface} -o {interface_out} -j ACCEPT']

    text = textwrap.wrap('In order to allow internet connection from inside the network namespace, one should allow forwarding between '
          f'your host interfaces {", ".join(host_interfaces)} and the interface associated to the network namespace '
          f'{interface_out}.', width=80)
    for line in text:
        print(line)
    print()

    print('To do this using ufw, run the following commands:')
    for command in ufw_commands:
        print(f'  {command}')
    print('To do this using iptables, run the following commands:')
    for command in iptables_commands:
        print(f'  {command}')