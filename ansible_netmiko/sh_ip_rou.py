import yaml
import os
from netmiko import ConnectHandler

with open("sh_ip_rou.yaml") as f:
    data = yaml.safe_load(f)

os.makedirs("../show_ip_route", exist_ok=True)

for device in data["devices"]:
    try:
        net_connect = ConnectHandler(
            host=device["host"],
            username=device["username"],
            password=device["password"],
            device_type=device["device_type"]
        )

        for command in device["commands"]:
            output = net_connect.send_command(command)
            with open(f"show_ip_route/{device['host']}_{command.replace(' ', '_')}.txt", "w") as file:
                file.write(output)
            print(output)
        print(f"Output for '{command}' on {device['host']} saved successfully.")
        net_connect.disconnect()

    except Exception as e:
        print(f"Error with {device['host']}: {e}")
