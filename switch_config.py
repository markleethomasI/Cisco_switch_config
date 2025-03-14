import serial
import time
import json

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
TOTAL_PORTS = 48  # Adjust based on switch model

def load_config(file):
    with open(file, "r") as f:
        return json.load(f)

def send_command(ser, command, wait=2):
    ser.write(command.encode() + b"\n")
    time.sleep(wait)
    output = ser.read(ser.inWaiting()).decode("utf-8")
    print(output)
    return output

def configure_switch(switch, global_config):
    try:
        print(f"Configuring {switch['hostname']} via console...")
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=5)

        send_command(ser, "\r", 3)
        send_command(ser, "\r", 3)
        send_command(ser, "enable", 3)
        send_command(ser, "configure terminal", 3)

        commands = [
            f"hostname {switch['hostname']}",
            "no ip domain-lookup"
        ]

        for vlan_id, vlan_info in switch["vlans"].items():
            commands.append(f"vlan {vlan_id}")
            commands.append(f"name {vlan_info['name']}")

        for trunk_port in switch["trunk_ports"]:
            commands.extend([
                f"interface {trunk_port}",
                "switchport mode trunk",
                "switchport trunk encapsulation dot1q",
                f"switchport trunk allowed vlan {','.join(switch['vlans'].keys())}",
                "exit"
            ])

        for port_num in range(1, TOTAL_PORTS + 1):
            port_name = f"GigabitEthernet0/{port_num}"
            if port_name not in switch["trunk_ports"]:
                commands.extend([
                    f"interface {port_name}",
                    "switchport mode access",
                    f"switchport access vlan {global_config['data_vlan']}",
                    f"switchport voice vlan {global_config['voice_vlan']}",
                    "switchport port-security",
                    "switchport port-security maximum 2",
                    "switchport port-security violation restrict",
                    "switchport port-security aging time 5",
                    "switchport port-security aging type inactivity",
                    "exit"
                ])

        if "ip" in switch["vlans"][global_config["management_vlan"]]:
            mgmt_vlan = switch["vlans"][global_config["management_vlan"]]
            commands.extend([
                f"interface vlan {global_config['management_vlan']}",
                f"ip address {mgmt_vlan['ip']} {mgmt_vlan['subnet']}",
                "no shutdown",
                "exit"
            ])

        commands.extend([
            "line console 0",
            f"password {global_config['console_password']}",
            "login",
            "exit",
            "line vty 0 4",
            f"password {global_config['vty_password']}",
            "login",
            "transport input ssh",
            "exit",
            f"enable secret {global_config['enable_password']}",
            "service password-encryption",
            f"crypto key generate rsa modulus {global_config['ssh_modulus']}",
            "ip ssh version 2",
            "wr mem"
        ])

        for cmd in commands:
            send_command(ser, cmd)

        print(f"Configuration completed for {switch['hostname']}")
        ser.close()

    except Exception as e:
        print(f"Error configuring {switch['hostname']}: {e}")

config_data = load_config("config.json")
global_config = config_data["global"]

for switch in config_data["switches"]:
    configure_switch(switch, global_config)
    input("Press Enter to configure the next switch...")
