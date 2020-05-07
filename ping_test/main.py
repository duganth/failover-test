import sched
import time
import multiprocessing
import graphyte
from pythonping import ping


def send_to_graphite(host, target, metric, time):
    target = target.replace('.', '_')
    graphyte.init(host, prefix=target)
    graphyte.send('result', metric, time)


def ping_target(target, graphite, b='default'):
    result = ping(target, count=1, timeout=.5)
    success = (0, 1)['Reply' in str(result)]
    print(success, time.time()//1, target)
    send_to_graphite(graphite, str(target), success, time.time()//1)


def schedule_pings(duration, target, graphite):
    s = sched.scheduler(time.time, time.sleep)
    for i in range(duration):
        s.enter(i, 1, ping_target, argument=(target, graphite,))
    s.run()


def main():
    targets = ['8.8.8.8', '8.8.4.4']
    duration = 480
    graphite = '192.168.15.27'
    for ip in targets:
        p = multiprocessing.Process(target=schedule_pings,
                                    args=(duration, ip, graphite))
        p.start()


if __name__ == "__main__":
    main()
