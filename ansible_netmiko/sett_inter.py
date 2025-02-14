import yaml
import os
from netmiko import ConnectHandler

with open("sett_int.yaml") as f:
    data = yaml.safe_load(f)

os.makedirs("../show_ip_interface_brief", exist_ok=True)

for device in data["devices"]:
    try:
        net_connect = ConnectHandler(
            host=device["host"],
            username=device["username"],
            password=device["password"],
            device_type=device["device_type"]
        )

        for interface in device["interfaces"]:
            config_commands = [
                f"interface {interface['name']}",
                f"ip address {interface['ip_address']} {interface['sub']}",
                "no shutdown",
                "exit"
            ]
            output = net_connect.send_config_set(config_commands)
            print(
                f"Configured {interface['name']} on {device['host']} with IP {interface['ip_address']} {interface['sub']}")
            print(output)

        for command in device.get("post_commands", []):
            output = net_connect.send_command(command)
            with open(f"show_ip_interface_brief/{device['host']}_{command.replace(' ', '_')}.txt", "w") as file:
                file.write(output)
            print(f"Output for '{command}' on {device['host']}:\n{output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"Error with {device['host']}: {e}")
