import threading
import random
import time
import queue


def fun1(param, que):
    print(f'fun1: {param[0]}, sleep: {param[1]}')
    time.sleep(param[1] / 1000)
    que.put(param[1])
    print(f'fun1: {param[0]}, done')


def main():
    threads = []

    for i in range(100):
        param = [i, random.randint(0, 10000)]
        que = queue.Queue()
        t1 = threading.Thread(target=fun1, args=(param, que,))
        step = [t1, que]
        threads.append(step)

        print(f'\nStart: {i}')
        t1.start()

    for t in threads:
        t[0].join()

    for t2 in threads:
        print(t2[1].get())
    print('Koniec')


if __name__ == '__main__':
    main()
