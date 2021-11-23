import yaml

with open('settings/config.yaml', encoding='UTF-8') as file:
    config_dict: dict = yaml.safe_load(file)

with open('settings/status.yaml', encoding='UTF-8') as file:
    status_dict: dict = yaml.safe_load(file)

def update_status():
    with open('settings/status.yaml', 'w', encoding='UTF-8') as file:
        yaml.dump(status_dict, file, default_flow_style=False)