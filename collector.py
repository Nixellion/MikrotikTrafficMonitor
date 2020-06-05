import requests
import traceback
from time import sleep
from datetime import datetime, date

from dbo import Accounting

class Collector(object):
    '''
    Collector is based on code of Uroš Vovk
    www.urosvovk.com/bandwidth-usage-report-per-ip-address/
    '''

    def __init__(self, router_ip):
        self.router_ip = router_ip
        self.accounting_url = "http://{}/accounting/ip.cgi".format(self.router_ip)
        self.local_network = ".".join(self.router_ip.split('.')[0:-1]) + '.'

    def collect(self):
        response = requests.get(self.accounting_url)
        data = response.text
        #print (data)
        data_collector = {}
        for l in data.split("\n")[:-1]:
            is_upload = True
            src, dst, b, p, su, du = l.split()
            if src.startswith(self.local_network):  # upload
                k = src
            else:  # download
                k = dst
                is_upload = False

            if k not in data_collector:
                data_collector[k] = [0, 0]

            if is_upload:
                data_collector[k][0] = data_collector[k][0] + int(b)
            else:
                data_collector[k][1] = data_collector[k][1] + int(b)

        for key, val in data_collector.items():

            Accounting.create(
                address=key,
                date=datetime.utcnow(),
                upload=val[0],
                year=datetime.utcnow().year,
                month=datetime.utcnow().month,
                download=val[1],
            )

