import serial
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

logger.debug("Defining constants and functions")
def load_config(file):
    logger.debug(f"Loading config from {file}")
    with open(file, "r") as f:
        return json.load(f)

def send_command(ser, command, wait=2):
    logger.debug(f"Sending command: {command}")
    ser.write(command.encode() + b"\n")
    logger.debug(f"Sleeping for {wait} seconds")
    time.sleep(wait)
    logger.debug("Reading output")
    output = ser.read(ser.inWaiting()).decode("utf-8")
    logger.debug(f"Received output: {output}")
    print(output)
    return output

def configure_switch(switch, global_config):
    try:
        logger.debug(f"Configuring {switch['hostname']} via console...")
        logger.debug("Initializing serial port")
        ser = serial.Serial(global_config["serial_port"], global_config["baud_rate"], timeout=5)
        logger.debug("Serial port initialized")

        # Initial commands
        logger.debug("Sending initial commands")
        send_command(ser, "\r", 3)
        send_command(ser, "\r", 3)
        send_command(ser, "enable", 3)
        send_command(ser, "configure terminal", 3)

        commands = [
            f"hostname {switch['hostname']}",
            "no ip domain-lookup"
        ]

        for vlan_id, vlan_info in switch["vlans"].items():
            logger.debug(f"Adding VLAN {vlan_id} commands")
            commands.append(f"vlan {vlan_id}")
            commands.append(f"name {vlan_info['name']}")

        for trunk_port in switch["trunk_ports"]:
            logger.debug(f"Adding trunk port {trunk_port} commands")
            commands.extend([
                f"interface {trunk_port}",
                "switchport mode trunk",
                "switchport trunk encapsulation dot1q",
                f"switchport trunk allowed vlan {','.join(switch['vlans'].keys())}",
                "exit"
            ])

        for port_num in range(1, global_config["total_ports"] + 1):
            port_name = f"GigabitEthernet0/{port_num}"
            if port_name not in switch["trunk_ports"]:
                logger.debug(f"Adding access port {port_name} commands")
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
            logger.debug(f"Adding management VLAN {global_config['management_vlan']} commands")
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
            logger.debug(f"Preparing to send command: {cmd}")
            send_command(ser, cmd)

        logger.debug(f"Configuration completed for {switch['hostname']}")
        ser.close()

    except Exception as e:
        logger.error(f"Error configuring {switch['hostname']}: {e}")
        raise

if __name__ == "__main__":
    logger.debug("Running main block")
    config_data = load_config("config.json")
    global_config = config_data["global"]
    for switch in config_data["switches"]:
        configure_switch(switch, global_config)
        input("Press Enter to configure the next switch...")