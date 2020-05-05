import iperf3
import graphyte
import sys
import time
from optparse import OptionParser


def parse_options():
    parser = OptionParser()
    parser.add_option("-t", "--target-host", dest="host", help="iperf3 target host", default='127.0.0.1')
    parser.add_option("-p", "--target-port", dest="port", help="iperf3 target port", default=5201)
    parser.add_option("-u", "--udp", dest="udp", help="if you want udp", action="store_true")
    parser.add_option("-r", "--reverse", dest="reverse", help="if you want reverse", action="store_true")
    parser.add_option("-d", "--duration", dest="duration", help="iperf3 test duration", default=10)
    parser.add_option("-g", "--graphite-host", dest="graphite_host", help="graphite host (with port)", default='127.0.0.1:2003')
    parser.add_option("-x", "--graphite-prefix", dest="graphite_prefix", help="graphite prefix for the metrics", default='')
    return parser.parse_args()


def perform_test(duration, target_hostname, target_port, protocol, reverse):
    try:
        client = iperf3.Client()
        client.duration = int(duration)
        client.server_hostname = target_hostname
        client.reverse = reverse
        client.blksize = 1400
        client.bandwith = 1000000
        client.protocol = protocol
        client.port = int(target_port)
        return client.run()
    except OSError:
        print("ERROR: iperf3 may not be installed", file=sys.stderr)
        sys.exit(1)


def send_to_graphite(graphite_host, prefix, intervals, start_time):
    graphyte.init(graphite_host, prefix='iperf_'+prefix)
    for interval in intervals:
        time = start_time + interval['sum']['start']
        graphyte.send('bps', interval['sum']['bits_per_second'], time)


def main():
    (options, args) = parse_options()
    start_time = time.time()
    protocol = 'udp' if options.udp else 'tcp'
    result = perform_test(options.duration, options.host, options.port,
                          protocol, options.reverse)
    intervals = result.json['intervals']
    send_to_graphite(options.graphite_host, options.graphite_prefix,
                     intervals, start_time)


if __name__ == "__main__":
    main()
