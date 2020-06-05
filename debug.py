'''
This file contains debugging stuff, like logger configuration, error wrap functions and the like.
'''

import os
import traceback
import logging
import logging.config
import yaml
from flask import Response, jsonify, render_template
import functools

basedir = os.path.dirname(os.path.realpath(__file__))


def setup_logging(
        default_path=os.path.join(basedir, 'config', 'logger.yaml'),
        default_level=logging.INFO,
        env_key='LOG_CFG',
        logname=None
):
    """Setup logging configuration

    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())

        logpath = os.path.join(basedir, config['handlers']['debug_file_handler']['filename'])
        print("Set log path to", logpath)
        config['handlers']['debug_file_handler']['filename'] = logpath

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def catch_errors_json(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": str(e), "traceback": traceback.format_exc()})

    return wrapped


loggers = {}


def get_logger(name):
    global loggers

    if loggers.get(name):
        # print (f"Logger {name} exists, reuse.")
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)
        loggers[name] = logger
        setup_logging()
        return logger


log = logger = get_logger("default")

def catch_errors_json(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            log.error(traceback.format_exc())
            return jsonify({"error": str(e), "traceback": traceback.format_exc()})

    return wrapped

def catch_errors_html(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            log.error(traceback.format_exc())
            return render_template("error.html", error=str(e), error_trace=traceback.format_exc())

    return wrapped
