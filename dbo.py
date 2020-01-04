# region  IMPORTS 
import os

import yaml
import operator
import time
from datetime import date, datetime, timedelta

import pytz
from dateutil.relativedelta import relativedelta

from functools import reduce
from peewee import *
# endregion

# region Logger
import logging
from debug import setup_logging

log = logger = logging.getLogger("dbo")
setup_logging()
# endregion


# region  GLOBALS 
realpath = os.path.dirname(os.path.realpath(__file__))
rp = realpath

db_path = os.path.join(realpath, 'database.db')
db = SqliteDatabase(db_path)
# endregion

# region  FUNCTIONS 
def read_yaml(filename):
    with open(os.path.join(filename), "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

def read_config_data():
    return read_yaml("config")

def read_config(filename):
    data = read_yaml(os.path.join(realpath, 'config', filename + '.yaml'))
    return data

def write_config(filename, data):
    with open(os.path.join(realpath, 'config', filename + '.yaml'), "w+", encoding="utf-8") as f:
        f.write(yaml.dump(data, default_flow_style=False))


def config(*args):
    conf = read_config('config')
    return reduce(operator.getitem, args, conf)

def set_config(*args, value=None):
    conf = read_config('config')
    config(conf, args[:-1])[args[-1]] = value
    write_config('config', conf)


# endregion



class Accounting(Model):
    address = CharField()
    date = DateTimeField()
    upload = IntegerField()
    download = IntegerField()

    class Meta:
        database = db

class MontlyArchive(Model):
    address = CharField()
    date = DateField()
    upload = IntegerField()
    download = IntegerField()

    class Meta:
        database = db

def trunc_datetime(someDate):
    return someDate.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def compare_months(A, B):
    A = trunc_datetime(A)
    B = trunc_datetime(B)
    return A == B

def cleanup_database():
    '''
    Remove oldest entries, count their sum and record into MonthlyArchive DB.
    '''
    try:
        now = datetime.utcnow().date()
        data = {}
        query = Accounting.select()
        for entry in query:
            entry_date = entry.date.date()
            if entry_date < now - relativedelta(months=config("general", "keep_months")):
                if entry_date not in data:
                    data[entry_date] = [entry.date, entry.address, entry.download, entry.upload]
                else:
                    data[entry_date][1] = entry.download + data[entry_date][1]
                    data[entry_date][2] = entry.upload + data[entry_date][2]
                entry.delete_instance()
        for dt, data in sorted(data.items()):
            MontlyArchive.create(
                date = dt,
                address = data[0],
                download = data[1],
                upload = data[2]
            )
    except Exception as e:
        log.error("Database cleanup failed.", exc_info=True)

def cleanup_database_loop():
    while True:
        cleanup_database()
        # TODO Replace with proper scheduler
        time.sleep(21600) # 21600 second = 6 hours

log.info(" ".join(["Using DB", str(db), "At path:", str(db_path)]))

db.connect()
db.create_tables([Accounting])

