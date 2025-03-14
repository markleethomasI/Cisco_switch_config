# Cisco_switch_config

Automated Cisco switch configuration script using Python & JSON.  
This script automatically configures VLANs, trunks, access ports, security settings, and management IPs on Cisco switches via the console port.

---

## Features
- Automated VLAN & Trunk Configuration  
- 802.1Q Trunking (Dot1Q) Support  
- Port Security (MAC Address Limits & Aging)  
- Voice VLAN Tagging on Access Ports  
- Dynamic Configuration Based on JSON File  
- SSH Security with Encrypted Passwords

---

## Installation
1. Clone the Repository
```sh
git clone https://github.com/yourusername/Cisco_switch_config.git
cd Cisco_switch_config
python3 -m venv venv
source venv/bin/activate
pip install
pip install -m pyserial
python3 switch_config.py
# Cisco_switch_config
