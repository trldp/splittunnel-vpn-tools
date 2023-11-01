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

import re
import subprocess
import sys

def set_up(ns_name, endpoint, user, password, command=None):
    print('Setting up VPN...')
    vpn_command = subprocess.Popen(['ip', 'netns', 'exec', ns_name, 'openfortivpn', endpoint, '-u', user, '-p', password],
                                    stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

    try:
        vpn_up_regexp = re.compile(r'INFO:\s*Tunnel is up and running.')
        while True:
            line = vpn_command.stdout.readline()
            if not line:
                raise Exception('VPN has exited without establishing a connection')
            
            line = line.decode('utf-8')
            if re.match(vpn_up_regexp, line):
                print(f'VPN is up and running in namespace {ns_name}.')
                break

        if command is not None:
            command()
        else:
            print('To run commands inside the VPN, use\n'
                  f'  sudo ip netns exec {ns_name} <command>')
            input('Press enter to stop the VPN and remove the network namespace...')
    except KeyboardInterrupt:
        print('Keyboard interrupt detected. Attempting graceful shutdown of VPN. Press ctrl+c again to stop the process '
              'immediately.')
    except Exception as e:
        print(f'Error occured: {e}. Stopping VPN and removing the network namespace again...', file=sys.stderr)
    finally:
        try:
            if vpn_command is not None:
                vpn_command.terminate()
                print('Waiting for VPN to stop...')
                vpn_command.wait(timeout=5)
                print('VPN stopped sucessfully')
        except KeyboardInterrupt:
            raise
        except subprocess.TimeoutExpired:
            print('Timeout expired. Killing VPN process...')
            vpn_command.kill()
        except Exception as e:
            print(f'Error occured while stopping VPN: {e}', file=sys.stderr)