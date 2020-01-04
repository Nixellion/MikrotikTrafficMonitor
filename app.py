#!/usr/bin/python3
# -*- coding: utf-8 -*-
import eventlet

eventlet.monkey_patch()

from datetime import datetime

import pytz

from flask import Flask, url_for, Response, render_template

from flask_socketio import SocketIO

from dbo import Accounting, config, cleanup_database_loop
from peewee import fn

from collector import Collector

# region Logger
import logging
from debug import setup_logging

log = logger = logging.getLogger("app")
setup_logging()
# endregion

app = Flask(__name__)
app.config.from_object(__name__)

socketio = SocketIO(app)


@app.context_processor
def inject_global_variables():
    return dict(
        Accounting=Accounting,
        config=config,
        now=datetime.utcnow(),
        fn=fn
    )

@app.route("/")
def index():
    return render_template("report.html")

def main():
    c = Collector()
    socketio.start_background_task(c.collect)
    socketio.start_background_task(cleanup_database_loop)
    socketio.run(app, debug=False, host='0.0.0.0', port=config("general", "PORT"))


if __name__ == '__main__':
    main()
    '''
    q = Accounting.select(Accounting.address, fn.strftime('%Y-%m', Accounting.date).alias('month'), fn.SUM(Accounting.download).alias('download'), fn.SUM(Accounting.upload).alias('upload')).group_by(Accounting.address, 'month').distinct()
    print (q)
    for a in q:
        print (a.address, a.month, a.download/1000000, a.upload/1000000)


    q = Accounting.select()
    s = 0
    for a in q:

        if a.address == '192.168.88.244':
            print (a.address, a.date, a.download/1000000, a.upload/1000000)
            s += a.download
    print ("SUM", s)
    '''