import requests
import time
import graphyte
import os
from optparse import OptionParser


def parse_options():
    parser = OptionParser()
    default_url = "https://speed.hetzner.de/10GB.bin"
    parser.add_option("-u", "--url", dest="url",
                      help="url", default=default_url)
    parser.add_option("-g", "--graphite-host", dest="graphite_host",
                      help="graphite host (with port)", default='127.0.0.1')
    return parser.parse_args()


def main():
    (options, args) = parse_options()
    os.system('ip link set eth0 qlen 1000')
    os.system('tc qdisc add dev eth0 root tbf rate 512kbit latency 60ms burst 1540')
    link = options.url
    file_name = "tmp"
    graphyte.init(options.graphite_host,
                  prefix='http_dl_'+options.url)
    with open(file_name, "wb") as f:
        with requests.get(link, stream=True) as response:
            total_length = int(response.headers.get('content-length'))
            if total_length is None:
                f.write(response.content)
            else:
                for data in response.iter_content(chunk_size=4096):
                    graphyte.send('bps', 1, time.time()//1)
                    f.write(data)


if __name__ == "__main__":
    main()
