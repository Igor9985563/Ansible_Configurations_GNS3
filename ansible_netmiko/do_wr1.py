import yaml
import os
from netmiko import ConnectHandler

with open("do_wr1.yaml") as f:
    data = yaml.safe_load(f)

os.makedirs("../wr1", exist_ok=True)

for device in data["devices"]:
    try:
        net_connect = ConnectHandler(
            host=device["host"],
            username=device["username"],
            password=device["password"],
            device_type=device["device_type"]
        )

        for command in device["do_wr"]:
            output = net_connect.send_config_set(command)
            with open(f"wr1/{device['host']}_{command.replace(' ', '_')}.txt", "w") as file:
                file.write(output)
            print(output)
        print(f"Output for '{command}' on {device['host']} saved successfully.")
        net_connect.disconnect()

    except Exception as e:
        print(f"Error with {device['host']}: {e}")
