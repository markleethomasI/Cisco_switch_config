import pytest
import json
from unittest.mock import MagicMock
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

logger.debug("Importing modules")
import pytest
import json
from unittest.mock import MagicMock
import sys
import os

logger.debug("Setting up project root and sys.path")
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger.debug(f"Project root: {project_root}")
logger.debug(f"sys.path: {sys.path}")
switch_config_path = os.path.join(project_root, 'switch_config.py')
logger.debug(f"Checking for switch_config.py at {switch_config_path}")
if not os.path.exists(switch_config_path):
    raise FileNotFoundError(f"switch_config.py not found at {switch_config_path}. Ensure the file exists and is named correctly.")

logger.debug("Attempting to import from switch_config")
try:
    from switch_config import load_config, send_command, configure_switch
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(f"Failed to import from switch_config. Ensure switch_config.py is in {project_root} and contains the required definitions. Error: {e}")

# Sample config for testing
logger.debug("Defining SAMPLE_CONFIG")
SAMPLE_CONFIG = {
    "global": {
        "data_vlan": "10",
        "voice_vlan": "20",
        "management_vlan": "99",
        "console_password": "cisco123",
        "vty_password": "cisco123",
        "enable_password": "cisco456",
        "ssh_modulus": 2048,
        "baud_rate": 9600,
        "total_ports": 2,
        "serial_port": "/dev/ttyUSB0"
    },
    "switches": [
        {
            "hostname": "Switch1",
            "vlans": {
                "10": {"name": "DATA", "ip": None, "subnet": None},
                "20": {"name": "VOICE", "ip": None, "subnet": None},
                "99": {"name": "MGMT", "ip": "192.168.99.2", "subnet": "255.255.255.0"}
            },
            "trunk_ports": ["GigabitEthernet0/1"]
        }
    ]
}

@pytest.fixture
def mock_serial(mocker):
    logger.debug("Setting up mock_serial fixture")
    mock = mocker.patch("serial.Serial")
    mock_instance = MagicMock()
    mock.return_value = mock_instance
    mock_instance.read.return_value = b"Mocked output"
    mock_instance.inWaiting.return_value = 100
    logger.debug("mock_serial fixture setup complete")
    return mock_instance

@pytest.fixture
def temp_config_file(tmp_path):
    logger.debug("Creating temp config file")
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        json.dump(SAMPLE_CONFIG, f)
    logger.debug(f"Temp config file created at {config_file}")
    return str(config_file)

def test_load_config(temp_config_file):
    logger.debug("Running test_load_config")
    config = load_config(temp_config_file)
    logger.debug("Verifying config")
    assert config == SAMPLE_CONFIG
    assert config["global"]["data_vlan"] == "10"
    assert config["switches"][0]["hostname"] == "Switch1"
    logger.debug("test_load_config completed")

def test_send_command(mock_serial, mocker):
    logger.debug("Running test_send_command")
    mocker.patch("time.sleep")
    logger.debug("Calling send_command with 'enable'")
    result = send_command(mock_serial, "enable", wait=1)
    logger.debug("Verifying mock_serial.write")
    mock_serial.write.assert_called_with(b"enable\n")
    logger.debug("Verifying result")
    assert result == "Mocked output"
    logger.debug("Verifying mock_serial.read and inWaiting")
    mock_serial.read.assert_called_once()
    mock_serial.inWaiting.assert_called_once()
    logger.debug("test_send_command completed")

def test_configure_switch(mock_serial, mocker, capsys):
    logger.debug("Running test_configure_switch")
    switch = SAMPLE_CONFIG["switches"][0]
    global_config = SAMPLE_CONFIG["global"]
    
    logger.debug("Mocking print, input, and time.sleep")
    mocker.patch("builtins.print")
    mocker.patch("builtins.input")
    mocker.patch("time.sleep")
    
    logger.debug("Calling configure_switch")
    configure_switch(switch, global_config)
    
    logger.debug("Verifying key commands")
    expected_commands = [
        "enable",
        "configure terminal",
        "hostname Switch1",
        "vlan 10",
        "name DATA",
        "interface GigabitEthernet0/1",
        "switchport mode trunk",
        "interface vlan 99",
        "ip address 192.168.99.2 255.255.255.0",
        "wr mem"
    ]
    for cmd in expected_commands:
        logger.debug(f"Checking for command: {cmd}")
        assert any(cmd in call.args[0].decode() for call in mock_serial.write.call_args_list), f"Command '{cmd}' not sent"
    
    logger.debug("test_configure_switch completed")

def test_configure_switch_error_handling(mocker):
    logger.debug("Running test_configure_switch_error_handling")
    switch = SAMPLE_CONFIG["switches"][0]
    global_config = SAMPLE_CONFIG["global"]
    
    logger.debug("Mocking serial to raise exception")
    mocker.patch("serial.Serial", side_effect=Exception("Serial port error"))
    mocker.patch("builtins.print")
    mocker.patch("time.sleep")
    
    logger.debug("Running configure_switch and expecting exception")
    with pytest.raises(Exception, match="Serial port error"):
        configure_switch(switch, global_config)
    logger.debug("test_configure_switch_error_handling completed")