# encoding: utf-8

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import yaml

# Inits the logging system. Only shell logging, and exception and warning catching.
# File logging can be started by calling log.start_file_logger(name).
from .utils import log
from . import vectorizer
from .model import CannonModel

def merge(user, default):
    """Merges a user configuration with the default one."""

    if isinstance(user, dict) and isinstance(default, dict):
        for kk, vv in default.items():
            if kk not in user:
                user[kk] = vv
            else:
                user[kk] = merge(user[kk], vv)

    return user


NAME = 'astra_thecannon'


# Loads config
config_path = os.path.dirname(__file__) + '/etc/{0}.yml'.format(NAME)
with open(config_path, "r") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

# If there is a custom configuration file, updates the defaults using it.
custom_config_path = os.path.expanduser('~/.{0}/{0}.yml'.format(NAME))
if os.path.exists(custom_config_path):
    with open(custom_config_path, "r") as fp:
        custom_config = yaml.load(fp, Loader=yaml.FullLoader)
    config = merge(custom_config, config)


__version__ = '0.1.2dev'

