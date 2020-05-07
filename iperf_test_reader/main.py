import tailer
import os
import multiprocessing
import re
import time
import graphyte
from pathlib import Path


def send_to_graphite(host, target, metric, time):
    target = target.replace('.', '_')
    graphyte.init(host, prefix=target)
    graphyte.send('result', metric, time)


def parse_line(line):
    if 'sender' in line or 'receiver' in line or 'connected' in line:
        return None
    if re.search('\[.*\d\]', line):
        elements = line.split(' ')
        index = elements.index('KBytes/sec')
        result = (0, 1)[float(elements[index-1]) > 0]
        interval = re.search('\d+.\d+-\d+.\d+', line)
        interval = int(interval[0].split('.')[0])
        return(result, interval)
    return None


def run_iperf(target, file_name, duration=10, port=5201):
    os.system(f'iperf3 -c {target} -p {port} --logfile {file_name} -f K -t {duration}')
    with open(file_name, 'a') as f:
        f.write('EXIT')


def read_iperf(file_name, graphite, target):
    start_time = int(time.time()) 
    for line in tailer.follow(open(file_name)):
        result = parse_line(line)
        if result is not None:
            print(result)
            send_to_graphite(graphite, str(target), result[0],
                             start_time+result[1])
        print(line)
        if line == 'EXIT':
            break


def main():
    target = '127.0.0.1'
    graphite = '192.168.15.27'
    duration = 480
    file_name = 'tst'
    Path(file_name).touch()
    os.system('ip link set eth0 qlen 1000')
    os.system('tc qdisc add dev eth0 root tbf rate 4024kbit latency 50ms burst 4540')
    p = multiprocessing.Process(target=run_iperf, args=(target,
                                                        file_name, duration, ))
    c = multiprocessing.Process(target=read_iperf, args=(file_name, graphite,
                                                         target))
    p.start()
    c.start()


if __name__ == '__main__':
    main()
