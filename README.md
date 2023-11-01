# Tools for setting up a split-tunnel FortiVPN on GNU/linux

Easily set up a split-tunnel FortiVPN client on GNU/Linux using network namespaces and openfortivpn, allowing you to
connect to the internet with and without the VPN simultaneously. Optionally start an RDP connection inside the VPN.

## How to run

The repository contains three ready to use scripts `set-up-ns.py`, `vpn-in-ns.py` and `rdp-over-vpn.sh`. Configuration,
such as the VPN username and endpoint to use, is set in `Configuration.py`.

- `set-up-ns.py`: sets up a network namespace,
- `vpn-in-ns.py`: sets up a VPN inside a network namespace,
- `rdp-over-vpn.py`: sets up an RDP connection over a VPN inside a network namespace.

All commands tear down the network namespace and VPN, if applicable, when they exit. How to run commands inside the
namespace or VPN is documented while running. Depending on what you want to run inside the VPN, it might be worth
making a separate script like `rdp-over-vpn.py` that automatically the commands you need inside the VPN.

The host interfaces to use for the connection to the internet are configured in `HOST_INTERFACES` inside
`Configuration.py`. On Ubuntu 22.04, these are `eno1` (wired interface) and `wlp2s0` (wireless interface) by default.
On some systems, you might want to change this to `['eth0', 'wlan0']`. Run `ifconfig` to check the names of the interfaces
on your system.

### Firewall configuration

In order to allow internet connection inside the network namespace, one has to allow forwarding between your host
interfaces, and the interface associated to the network namespace (`nsname1` by default). The exact configuration
can either be done directly using `iptables`, or through `ufw` (or possibly using any other
firewall you have on your system). Running any of the three scripts above with the option `--help-firewall` will
detail what commands you have to run. Note that these commands work with many standard firewall configuration, but might
not work if you have more exotic configurations.

### Dependencies

The scripts in this repository use the following programs

- iptables (tested with 1.8.7)
- openfortivpn (tested with 1.17.1)
- python 3 (tested with 3.10.6)
- xfreerdp (tested with 2.6.1)

Moreover, the scripts in this repository depend on the following python packages

- pwinput (tested with 1.0.3)
- sh (tested with 2.0.6)

If these packages are not provided by your distribution, it is recommended to install them inside a virtual environment
(see below).

### Creating a python environment

The scripts in this repository rely on a number of python packages.
If (one of) these packages are available in your distributions packages, it is recommended to install them in
a virtual environment. One can do this as follows.

First, create a new virtual environment in the same directory as this script

```bash
python -m venv --system-site-packages venv
```

The `--system-site-packages` option is optional. It allows you to use the packages that are install system-wide
inside this environment. Without this option, the virtual environment will not have access to any of those packages,
and you will have to install all dependencies manually. Then, activate the environment

```bash
source venv/bin/activate
```

and install the packages using

```bash
pip install sh pwinput
```

To exit the virtual environment, run

```bash
deactivate
```

You will need to be root to execute the scripts, meaning that you need to load the virtual environment as root as well.
Therefore, run

```bash
sudo su
source venv/bin/activate
./vpn-in-ns.py
```

to start `vpn-in-ns.py` (and similarly for any of the other scripts). When finished run

```bash
deactivate
exit
```

to exit virtual environment and exit the `su` session.

## History

This repository came about as I needed an easy, quick and reliable way to set up a split-tunnel VPN on my Ubuntu machine.
A number of solutions existed already, in varying states of readiness, but since none exactly did what I needed
(in particular no mention of possibly needed firewall configuration was made),
I decided to make my own solution. Below are some notable alternatives and resources I came across.

- [vpnshift](https://github.com/crasm/vpnshift.sh): a similar script as mine, using openvpn instead of openforticlient,
- [vpnns.sh](https://gist.github.com/Schnouki/fd171bcb2d8c556e8fdf#file-vpnns-sh): another, slightly less polished,
alternative using openvpn,
- <https://www.redhat.com/sysadmin/use-net-namespace-vpn>: a nice article explaining the main idea of network namespaces
and their relation to VPNs.

## License

All code in this repository is licensed under GPL-3+, see [here](https://www.gnu.org/licenses/gpl-3.0.html) for more 
information.
