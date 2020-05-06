import requests
import time
import graphyte
from optparse import OptionParser


def parse_options():
    parser = OptionParser()
    default_url = "http://ipv4.download.thinkbroadband.com/1GB.zip"
    parser.add_option("-u", "--url", dest="url",
                      help="url", default=default_url)
    parser.add_option("-g", "--graphite-host", dest="graphite_host",
                      help="graphite host (with port)", default='127.0.0.1')
    parser.add_option("-x", "--graphite-prefix", dest="graphite_prefix",
                      help="graphite prefix for the metrics", default='bps')
    return parser.parse_args()


def main():
    (options, args) = parse_options()
    link = options.url
    file_name = "tmp"
    graphyte.init(options.graphite_host,
                  prefix='http_dl_'+options.graphite_prefix)
    with open(file_name, "wb") as f:
        with requests.get(link, stream=True) as response:
            total_length = int(response.headers.get('content-length'))
            next_perf = time.time()//1
            if total_length is None:
                f.write(response.content)
            else:
                chunks = 0
                for data in response.iter_content(chunk_size=4096):
                    if not time.time()//1 - next_perf//1 == 0:
                        graphyte.send('bps', chunks*4096, time.time()//1)
                        print(f'{chunks*4096}bps at {time.time()}')
                        next_perf = int(time.time()//1)
                    chunks += 1
                    f.write(data)


if __name__ == "__main__":
    main()
