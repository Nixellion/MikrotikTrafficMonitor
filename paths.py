'''
Configuration file that holds static and dynamically generated paths, like path to your current app directory.

'''

import os

# APP_DIR will point to the parent directory of paths.py file
APP_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_DIR = os.path.join(APP_DIR, "config")
DATA_DIR = os.path.join(APP_DIR, "data")
