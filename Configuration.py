#
# Configuration for the network namespace
#

# The name of the network namespace
NS_NAME = 'nsname'
# The host interfaces used for the connection, typically your main wired and/or a wireless interface
HOST_INTERFACES = ['eno1', 'wlp2s0']
# The name of the network interface in the network namespace
INTERFACE_IN = f'{NS_NAME}0'
# The IP address of the network interface in the network namespace
IP_IN = '10.202.200.1'
# The name of the network interface outside the network namespace that is connected to the interface in the network namespace
INTERFACE_OUT = f'{NS_NAME}1'
# The IP address of the network interface outside the network namespace
IP_OUT = '10.202.200.2'

#
# Configuration for the VPN
#

# The address of the VPN to connect to
VPN_ENDPOINT = 'vpn.something.com'
# The username to use for the VPN
VPN_USER = 'vpn_username'

#
# Configuration for the RDP connection
#

# The address of the RDP host to connect to
RDP_HOST = 'rdp.something.com'
# The domain of the RDP host
RDP_DOMAIN = 'some_domain'
# The username to use for the RDP connection
RDP_USER = 'rdp_username'