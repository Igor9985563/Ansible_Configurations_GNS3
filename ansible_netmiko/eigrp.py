import re
import ipaddress
import yaml
import os
from netmiko import ConnectHandler

with open("eigrp.yaml") as f:
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

        # Выполним команду show ip route, если файл не существует
        show_ip_route_file = f"show_ip_route/{device['host']}_show_ip_route.txt"
        if not os.path.exists(show_ip_route_file):
            output = net_connect.send_command("show ip route")
            with open(show_ip_route_file, "w") as f:
                f.write(output)

        # Теперь можно читать из файла
        with open(show_ip_route_file) as f:
            data = f.read()

            r = re.findall(r"C\s+(\d+\.\d+\.\d+\.\d+)/(\d+)", data)

            for ip, mask in r:
                ipadd = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)

                for eigr in device["eigrp"]:
                    eigr_value = eigr["name"]
                    config_commands = [
                        f"router eigrp {eigr_value}",
                        f"network {ip} {ipadd.netmask}",
                        "pass f0/0"
                    ]
                    output = net_connect.send_config_set(config_commands)
                    print(f"Configured EIGRP {eigr_value} with network {ip}/{mask} on {device['host']}")
                    print(output)

            for command in device.get("post_commands", []):
                output = net_connect.send_command(command)
                print(f"Output for '{command}' on {device['host']}:\n{output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"Error with {device['host']}: {e}")
