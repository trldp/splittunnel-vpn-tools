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
from sh import xfreerdp, ip
import sys

def rdp(host, domain, user, password, screens=None, gateway=None, gateway_user=None, gateway_password=None,
        fullscreen=True, multimonitor=True, network_namespace=None):
    """Starts an RDP connection to the given host."""
    
    args = [f'/v:{host}', f'/u:{user}', f'/d:{domain}']
    if screens is not None:
        args.append(f'/monitors:{screens}')
    if password is not None:
        args.append(f'/p:{password}')
    if fullscreen:
        args.append('/f')
    if multimonitor:
        args.append('/multimon')
    if gateway is not None:
        args.append(f'/g:{gateway}')
        if gateway_user is not None:
            args.append(f'/gu:{gateway_user}')
            gateway_password = gateway_password or password
            if gateway_password is not None:
                args.append(f'/gp:{gateway_password}')

    if network_namespace is not None:
        ip('netns', 'exec', network_namespace, 'xfreerdp', *args)
    else:
        xfreerdp(*args)