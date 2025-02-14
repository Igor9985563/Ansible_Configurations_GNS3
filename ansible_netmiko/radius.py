import os
import yaml
from netmiko import ConnectHandler

# Загружаем данные из файла YAML
with open("radius.yaml") as f:
    data = yaml.safe_load(f)

# Создаём директорию для сохранения вывода
os.makedirs("../aaa_configuration", exist_ok=True)

# Перебираем все устройства
for device in data["devices"]:
    try:
        # Подключаемся к устройству
        net_connect = ConnectHandler(
            host=device["host"],
            username=device["username"],
            password=device["password"],
            device_type=device["device_type"]
        )

        # Команды для настройки AAA
        aaa_config_commands = [
            "username class secret class",
            "username admin secret cisco",
            "aaa new-model",
            "aaa authentication login default group radius local",  # Настройка аутентификации
            "aaa authentication enable default group radius enable",  # Аутентификация для enable
            "aaa session-id common",  # Общий идентификатор сессии
            "radius-server host 127.0.0.1 auth-port 1812 acct-port 1813 key testing123",  # Конфигурация RADIUS сервера
        ]

        # Отправляем команды на устройство
        output = net_connect.send_config_set(aaa_config_commands)
        print(f"AAA configuration on {device['host']}:\n{output}")

        # Сохраняем результат
        with open(f"aaa_configuration/{device['host']}_aaa_config.txt", "w") as file:
            file.write(output)

        # Выполняем дополнительные команды (например, проверка статуса или вывод команд)
        for command in device.get("post_commands", []):
            output = net_connect.send_command(command)
            with open(f"aaa_configuration/{device['host']}_{command.replace(' ', '_')}.txt", "w") as file:
                file.write(output)
            print(f"Output for '{command}' on {device['host']}:\n{output}")

        # Закрываем соединение
        net_connect.disconnect()

    except Exception as e:
        print(f"Error with {device['host']}: {e}")
