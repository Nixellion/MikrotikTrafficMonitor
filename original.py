import urllib2
import sqlite3
import os
import sys
import pytz

from time import sleep
from datetime import datetime

# settings
router_ip='192.168.1.1'


accounting_url = "http://%s/accounting/ip.cgi" % router_ip
local_network = ".".join(router_ip.split('.')[0:-1]) + '.'
slqlitedb = '%s/data.db' % os.path.dirname(os.path.realpath(sys.argv[0]))

#print "#" * 30
#print router_ip
#print accounting_url
#print local_network
#print slqlitedb
#print "#" * 30


con = sqlite3.connect(slqlitedb)
cur = con.cursor()

cur.execute('''create table if not exists accounting (address TEXT, date TEXT, upload INTEGER, download INTEGER)''')
cur.execute('''drop view if exists sum_per_month''')
cur.execute('''
create view sum_per_month as
                select
                        distinct address,
                        strftime('%m.%Y', date) as month,
                        sum(upload)/1000000 as upload,
                        sum(download)/1000000 as download
                from accounting
                group by address, month''')


while True:
        response = urllib2.urlopen(accounting_url)
        data = response.read()
        data_collector = {}
        for l in data.split("\n")[:-1]:
                        is_upload = True
                        src, dst, b, p, su, du = l.split()
                        if src.startswith(local_network):       # upload
                                k = src
                        else:                                                           # download
                                k = dst
                                is_upload = False

                        if k not in data_collector:
                                data_collector[k] = [0, 0]

                        if is_upload:
                                data_collector[k][0] = data_collector[k][0] + int(b)
                        else:
                                data_collector[k][1] = data_collector[k][1] + int(b)

        for key,val in data_collector.items():
                cur.execute("insert into accounting values (?, ?, ?, ?)", (key, datetime.now(pytz.utc), val[0], val[1]))
        con.commit()
        sleep(5)
con.close()