'''
HTML template views, actualy website frontend stuff
Could use flask-restful, I personally did not find much benefit in using it, yet.
'''

import os
from flask import Blueprint, request, redirect, Response, jsonify, send_from_directory, render_template
from debug import catch_errors_html
from paths import APP_DIR
from bro_utils import render_template_themed
from configuration import read_config
from dbo import MonthlyArchive
config = read_config()

app = Blueprint("views", __name__)

@app.route("/")
@catch_errors_html
def index():
    return render_template_themed("index.html")


@app.route("/months")
@catch_errors_html
def months():
    month = request.args.get("month", None)

    if month == None:
        query = MonthlyArchive.select()
    else:
        query = MonthlyArchive.select().where(MonthlyArchive.month == int(month))

    return render_template_themed("months.html", query=query)
# @app.route("/download/<var1>/<var2>")
# @catch_errors_html
# def dl(var1, var2):
#     return send_from_directory(os.path.join(APP_DIR, var1), os.path.join(APP_DIR, var1, var2))

