'''
Main application file
'''

import eventlet
eventlet.monkey_patch()

from flask import Flask, Response, render_template, Markup, request, redirect
from flask_socketio import SocketIO

from datetime import datetime
import dbo

# region Logger
import logging
from debug import setup_logging

log = logger = logging.getLogger("default")
setup_logging()
# endregion

from configuration import read_config
import jinja_filters
from peewee import fn

config = read_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BLAAAA_GeneerateMeDynamicallyForBetterSecurity'

socketio = SocketIO(app, async_mode='eventlet')


app.jinja_env.filters['html_line_breaks'] = jinja_filters.html_line_breaks


@app.context_processor
def inject_global_variables():
    return dict(
        config=config,
        now=datetime.utcnow(),
        Accounting=dbo.Accounting,
        MonthlyArchive=dbo.MonthlyArchive,
        fn=fn
    )


def add_background_task(task, interval):
    def tsk():
        while True:
            try:
                log.debug(f"Running background task {task.__name__}...")
                task()
                log.debug(f"Completed background task {task.__name__}!")
            except Exception as e:
                log.error(f"Can't run background task '{task.__name__}': {e}", exc_info=True)
            socketio.sleep(interval)

    socketio.start_background_task(tsk)


if __name__ == '__main__':
    from collector import Collector
    c = Collector(config['router_ip'])

    add_background_task(c.collect, config['interval'])
    add_background_task(dbo.cleanup_database, 6 * 60 * 60)
    config = read_config()

    from views import app as views
    from api import app as api
    app.register_blueprint(views)
    app.register_blueprint(api)

    try:
        if config['host'] == "0.0.0.0":
            host = 'localhost'
        else:
            host = config['host']
        log.info(f"Running at http://{host}:{config['port']}")
        socketio.run(app, debug=False, host=config['host'], port=config['port'])
    except:
        print("Unable to start", exc_info=True)



