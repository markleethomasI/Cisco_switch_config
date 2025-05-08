# Cisco_switch_config

Automated Cisco switch configuration script using Python & JSON.  
This script automatically configures VLANs, trunks, access ports, security settings, and management IPs on Cisco switches via the console port.

---

## Use with Linux only right now. Will work on a Windows version.

## Features
- Automated VLAN & Trunk Configuration  
- 802.1Q Trunking (Dot1Q) Support  
- Port Security (MAC Address Limits & Aging)  
- Voice VLAN Tagging on Access Ports  
- Dynamic Configuration Based on JSON File  
- SSH Security with Encrypted Passwords

---

## Installation
Clone the Repository
```sh
git clone https://github.com/yourusername/Cisco_switch_config.git
cd Cisco_switch_config

## Create virtual env
python3 -m venv venv

## Activate virtual env
source venv/bin/activate

## Install modules
pip install

## Install pyserial
pip install -m pyserial

```

---
## Configuration
Edit config.json as needed. The options are fairly limited at this point. I have no hardware available, but I have tested the command outputs in packet tracer and it is fully functional. I would love to add more features. Configuration is fairly straight forward.

### Example Configuration
```json
{
    "global": {
      "enable_password": "cisco",
      "console_password": "cisco",
      "vty_password": "cisco",
      "subnet_mask": "255.255.255.0",
      "ssh_modulus": 1024,
      "serial_port": "/dev/ttyUSB0",
      "baud_rate": 9600,
      "total_ports": 48
    },
    "switches": [
      {
        "hostname": "Alpha",
        "management_ip": "192.168.1.2",
        "vlans": {
          "10": "DATA",
          "20": "VOICE",
          "30": "MANAGEMENT"
        },
        "trunk_ports": ["GigabitEthernet0/24", "GigabitEthernet0/1"],
        "access_ports": {
          "GigabitEthernet0/2": {"data_vlan": "10", "voice_vlan": "20"},
          "GigabitEthernet0/3": {"data_vlan": "10", "voice_vlan": "20"},
          "GigabitEthernet0/4": {"data_vlan": "10", "voice_vlan": "20"}
        }
      },
      {
        "hostname": "Bravo",
        "management_ip": "192.168.1.3",
        "vlans": {
          "10": "DATA",
          "20": "VOICE",
          "30": "MANAGEMENT"
        },
        "trunk_ports": ["GigabitEthernet0/5", "GigabitEthernet0/6"],
        "access_ports": {
          "GigabitEthernet0/7": {"data_vlan": "10", "voice_vlan": "20"},
          "GigabitEthernet0/8": {"data_vlan": "10", "voice_vlan": "20"}
        }
      }
    ]
}
  
```  

```sh
## Run script
python3 switch_config.py

## Testing
I implemented basic testing using mocks.

PYTHONPATH=. pytest tests/test_switch_config.py -v -s

### Debugging
To view your command output run this. It is in a log block a few lines up.

DEBUG    switch_config:switch_config.py:21 Reading output
DEBUG    switch_config:switch_config.py:23 Received output: Mocked output
DEBUG    switch_config:switch_config.py:109 Configuration completed for Switch1
DEBUG    test_switch_config:test_switch_config.py:121 Verifying key commands
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: enable
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: configure terminal
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: hostname Switch1
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: vlan 10
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: name DATA
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: interface GigabitEthernet0/1
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: switchport mode trunk
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: interface vlan 99
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: ip address 192.168.99.2 255.255.255.0
DEBUG    test_switch_config:test_switch_config.py:135 Checking for command: wr mem
DEBUG    test_switch_config:test_switch_config.py:138 test_configure_switch completed
PASSED
```