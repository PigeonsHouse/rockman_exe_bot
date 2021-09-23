import yaml

with open('settings/config.yaml', encoding='UTF-8') as file:
    config_dict: dict = yaml.safe_load(file)

with open('settings/status.yaml', encoding='UTF-8') as file:
    status_dict: dict = yaml.safe_load(file)