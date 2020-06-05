# region ############################# IMPORTS #############################

import logging
from debug import setup_logging

log = logging.getLogger("default")
setup_logging()

import os
from datetime import datetime, timedelta
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase  # , FTS5Model, SearchField
from configuration import read_config, write_config
from paths import DATA_DIR
from dateutil.relativedelta import relativedelta

# endregion


# region ############################# GLOBALS #############################
realpath = os.path.dirname(os.path.realpath(__file__))
rp = realpath

db_path = os.path.join(DATA_DIR, 'database.db')
pragmas = [
    ('journal_mode', 'wal'),
    ('cache_size', -1000 * 32)]
db = SqliteExtDatabase(db_path, pragmas=pragmas)


# endregion


# region ############################# TABLE CLASSES #############################

class BroModel(Model):
    date_created = DateTimeField(default=datetime.now())
    date_updated = DateTimeField(default=datetime.now())
    date_deleted = DateTimeField(null=True)
    deleted = BooleanField(default=False)

    def mark_deleted(self):
        self.deleted = True
        self.date_deleted = datetime.now()
        self.save()


class Accounting(Model):
    address = CharField()
    date = DateTimeField()
    year = IntegerField()
    month = IntegerField()
    upload = IntegerField()
    download = IntegerField()

    class Meta:
        database = db

    @property
    def this_month(self):
        now = datetime.now()
        year = now.year
        month = now.month
        up = 0
        down = 0
        for a in self.select().where((Accounting.year == year) & (Accounting.month == month)):
            up += a.upload
            down += a.download
        return [down, up]

    def save(self, *args, **kwargs):
        self.date_updated = datetime.now()
        ret = super(Accounting, self).save(*args, **kwargs)

        try:
            mo = MonthlyArchive.get((MonthlyArchive.month == self.month) & (MonthlyArchive.address == self.address))
        except:
            mo = None

        if mo:
            mo.upload = mo.upload + self.upload
            mo.download = mo.download + self.download
            mo.save()
        else:
            MonthlyArchive.create(
                address=self.address,
                month=self.month,
                year=self.year,
                upload=self.upload,
                download=self.download
            )

        return ret


class MonthlyArchive(Model):
    address = CharField()
    year = IntegerField()
    month = IntegerField()
    upload = IntegerField()
    download = IntegerField()

    class Meta:
        database = db

    @property
    def this_month(self):
        print ("RUN CYKA!")
        sel = self.select().where((MonthlyArchive.year == datetime.utcnow().year) & (MonthlyArchive.month == datetime.utcnow().month))
        return sel


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
            if entry_date < now - relativedelta(months=config["keep_months"]):
                if entry_date not in data:
                    data[entry_date] = [entry.date, entry.address, entry.download, entry.upload]
                else:
                    data[entry_date][1] = entry.download + data[entry_date][1]
                    data[entry_date][2] = entry.upload + data[entry_date][2]
                entry.delete_instance()
        # for dt, data in sorted(data.items()):
        #     MonthlyArchive.create(
        #         date=dt,
        #         year=dt.year,
        #         month=dt.month,
        #         address=data[0],
        #         download=data[1],
        #         upload=data[2]
        #     )
    except Exception as e:
        log.error("Database cleanup failed.", exc_info=True)


# region Migration
config = read_config()
if config['database_migrate']:
    log.debug("=====================")
    log.debug("Migration stuff...")
    try:
        from playhouse.migrate import *

        migrator = SqliteMigrator(db)

        open_count = IntegerField(default=0)

        migrate(
            migrator.add_column('Entry', 'open_count', open_count)
        )
        log.debug("Migration success")
        log.debug("=====================")

        config['database_migrate'] = False
        write_config(config)
    except:
        log.error("Could not migrate", exc_info=True)
        log.debug("=====================")
# endregion

log.info(" ".join(["Using DB", str(db), "At path:", str(db_path)]))

# On init make sure we create database

db.connect()
db.create_tables([Accounting, MonthlyArchive])

# endregion
