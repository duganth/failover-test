import requests
import sys
import time
import graphyte
from optparse import OptionParser
import os


def parse_options():
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", help="url", default="http://ipv4.download.thinkbroadband.com/1GB.zip")
    parser.add_option("-g", "--graphite-host", dest="graphite_host", help="graphite host (with port)", default='127.0.0.1')
    parser.add_option("-x", "--graphite-prefix", dest="graphite_prefix", help="graphite prefix for the metrics", default='1gig')
    return parser.parse_args()


(options, args) = parse_options()
link = options.url
file_name = "tmp"
start_time = time.time()
response = requests.get(link, stream=True)
graphyte.init(options.graphite_host, prefix='httpdl_'+options.graphite_prefix)

with open(file_name, "wb") as f:
    response = requests.get(link, stream=True)
    total_length = int(response.headers.get('content-length'))

    if total_length is None:
        f.write(response.content)
    else:
        floor = int(time.perf_counter()//1)
        chunks = 0
        for data in response.iter_content(chunk_size=4096):
            if not floor - int(time.perf_counter()//1) == 0:
                print(f'Downloaded at {chunks*4096}bps at {floor+start_time}')
                print(time.strftime("%H:%M:%S", time.localtime()))
                graphyte.send('bps', chunks*4096, floor+start_time)
                floor = int(time.perf_counter()//1)
                chunks = 0
            chunks += 1
            f.write(data)


os.remove(file_name)


