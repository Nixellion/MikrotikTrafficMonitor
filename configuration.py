import os
import yaml

from paths import CONFIG_DIR

def read_config(name="config"):
    with open(os.path.join(CONFIG_DIR, name+".yaml"), "r") as f:
        data = yaml.load(f.read())
    return data

def write_config(data, name="config"):
    with open(os.path.join(CONFIG_DIR, name+".yaml"), "w+") as f:
        f.write(yaml.dump(data, default_flow_style=False))