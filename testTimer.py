from time import sleep
from threading import Timer
import queue


def task(message, que):
    print(message)
    que.put('Done')


que = queue.Queue()
timer = Timer(3, task, args=('Hello world', que,))

timer.start()

sleep(1)
if timer.is_alive():
    print('Canceling the timer...')
    timer.cancel()

timer.join()

print('Koniec')
