dhcp-o82
========

Makes humans working with DHCP Option 82/RelayAgentInfo possible.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/supermanny81/dhcp-o82)
![tests](https://github.com/supermanny81/dhcp-o82/actions/workflows/test.yaml/badge.svg)
[![codecov](https://codecov.io/gh/supermanny81/dhcp-o82/branch/main/graph/badge.svg?token=81PI6KOHUA)](https://codecov.io/gh/supermanny81/dhcp-o82)
[![PyPI version](https://badge.fury.io/py/dhcp-o82.svg)](https://badge.fury.io/py/dhcp-o82)
-----

DHCP Option 82 is used to pass relay agent information from a client to a DHCP server for address assignment.  Use cases like cable modems, factory floors, and IoT often require assigning addresses based on the information passed in this header over the traditional client MAC based reservations.

This utility will parse the contents of the packet for network admins for troubleshooting and will also generate new lookup keys for their DHCP servers, like Cisco Prime Network Registrar, dhcpd, or on box XE based DHCP.

Usage
-----

See `dhcp-o82 --help` or `dhcp-o82 [COMMAND] --help` for more usage information.

Creating a lookup key for vlan-module-port and switch mac address...

```bash
$ dhcp-o82 create -c 401-1-16  -r 4c71.0c45.6300
01:06:00:04:01:91:01:10:02:08:00:06:4C:71:0C:45:63:00

sub-option: 1 (0x1), name: CIRCUIT_ID, length: 6 (0x6)
  type: 0 (0x0), length: 4 (0x4)
  val: 01:91:01:10
  vlan-module-port: 401-1-16

sub-option: 2 (0x2), name: REMOTE_ID, length: 8 (0x8)
  type: 0 (0x0), length: 6 (0x6)
  val: 4c:71:0c:45:63:00
```

Inspecting the contents of a lookup key...

```bash
$ dhcp-o82 inspect 01:09:01:07:54:77:30:2F:30:2F:31:02:0E:01:0C:6F:74:2D:73:77:69:74:63:68:2D:39:39
01:09:01:07:54:77:30:2F:30:2F:31:02:0E:01:0C:6F:74:2D:73:77:69:74:63:68:2D:39:39

sub-option: 1 (0x1), name: CIRCUIT_ID, length: 9 (0x9)
  type: 1 (0x1), length: 7 (0x7)
  val: 54:77:30:2f:30:2f:31
  string: Tw0/0/1

sub-option: 2 (0x2), name: REMOTE_ID, length: 14 (0xe)
  type: 1 (0x1), length: 12 (0xc)
  val: 6f:74:2d:73:77:69:74:63:68:2d:39:39
  string: ot-switch-99
```

Working with a csv file...

```bash
$ cat sample.csv 
vlan,module,port,remote_id
400,1,1,access-sw1
400,1,4,access-sw1
500,1,7,access-sw3
$ dhcp-o82 create-from sample.csv                                          
$ cat sample-modified.csv 
vlan,module,port,remote_id,hex
400,1,1,access-sw1,01:06:00:04:01:90:01:01:02:0C:01:0A:61:63:63:65:73:73:2D:73:77:31
400,1,4,access-sw1,01:06:00:04:01:90:01:04:02:0C:01:0A:61:63:63:65:73:73:2D:73:77:31
500,1,7,access-sw3,01:06:00:04:01:F4:01:07:02:0C:01:0A:61:63:63:65:73:73:2D:73:77:33
```

Install
-------

Use `pip` for install:

```bash
pip install dhcp-o82
```

If you want to setup a development environment, use `poetry` instead:

```bash
# install poetry using pipx
python -m pip install pipx
python -m pipx ensurepath
pipx install poetry

# clone repository
git clone https://github.com/supermanny81/dhcp-o82.git

cd dhcp/

# install dependencies
poetry install
```
