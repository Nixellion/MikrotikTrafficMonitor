'''
This script will run a few speed tests, calculate average upload and download speeds and edit all Simple Queues to match.

NOTE: Device that runs this speed test should not have any limits, and should be excluded from Queues.
'''

import routeros_api
import speedtest

servers = []
threads = None

s = speedtest.Speedtest()

download = 0
upload = 0

for i in range (0, 3):
    print (f"Running test {i}...")
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads, pre_allocate=False)

    results_dict = s.results.dict()
    download += results_dict['download']
    upload += results_dict['upload']

download = download/3
upload = upload/3

print (download, upload)

connection = routeros_api.RouterOsApiPool('192.168.1.1', username='admin', password='', plaintext_login=True)
api = connection.get_api()

list_queues = api.get_resource('/queue/simple')

for queue in list_queues.get():
    print(f"Queue {queue['name']}: limit_at {int(upload)-int(upload/10)}/{int(download)-int(download/10)}; max_limit {int(upload)}/{int(download)}")
    list_queues.set(id=queue['id'], limit_at=f"{int(upload)-int(upload/10)}/{int(download)-int(download/10)}", max_limit=f"{int(upload)}/{int(download)}")