import random
import time

min_time = 0
max_time = 1000


def fun_a(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('fun_a input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def fun_b(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('fun_b input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def fun_c(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('fun_c input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info
