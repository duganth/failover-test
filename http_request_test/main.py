import sched
import time
import multiprocessing
import graphyte
from urllib.request import urlopen


def send_to_graphite(host, target, metric, time):
    target = target.replace('.', '_')
    graphyte.init(host, prefix=target)
    graphyte.send('result', metric, time)


def gen_requests(target, graphite, b='default'):
    result = urlopen("http://"+target).getcode()
    success = (0, 1)[str(result) == '200']
    print(success, time.time()//1, target)
    send_to_graphite(graphite, str(target), success, time.time()//1)


def schedule_requests(duration, target, graphite):
    s = sched.scheduler(time.time, time.sleep)
    for i in range(duration):
        s.enter(i, 1, gen_requests, argument=(target, graphite))
    s.run()


def main():
    targets = ['example.com', 'plor.io']
    duration = 480
    graphite = '192.168.15.27'
    for ip in targets:
        p = multiprocessing.Process(target=schedule_requests,
                                    args=(duration, ip, graphite,))
        p.start()


if __name__ == "__main__":
    main()
