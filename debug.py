import os
import logging
import logging.config
import yaml

basedir = os.path.dirname(os.path.realpath(__file__))

global setup_complete
setup_complete = False


def setup_logging(
    default_path=os.path.join(basedir, 'config', 'logger.yaml'),
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    global setup_complete
    if not setup_complete:
        path = default_path
        value = os.getenv(env_key, None)
        if value:
            path = value
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = yaml.safe_load(f.read())

            logpath = os.path.join(basedir, config['handlers']['debug_file_handler']['filename'])
            print ("Set log path to", logpath)
            config['handlers']['debug_file_handler']['filename'] = logpath

            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)
        setup_complete = True


