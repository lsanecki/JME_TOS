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


def pause(param):
    time.sleep(param[0] / 1000)
    print('pause input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_ping(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_ping input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_connect_db(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_connect_db input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_multimeter(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_multimeter input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_signal_matrix(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_signal_matrix input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_power_matrix(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_power_matrix input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_power_supply(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_power_supply input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def check_printer(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('check_printer input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def wait_for_close_cover(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('wait_for_close_cover input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def set_power_matrix(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('set_power_matrix input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def power_230v(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('power_230v input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info


def set_signal_matrix(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    print('set_signal_matrix input: {}'.format(param))
    status = True
    error_info = "0"

    return status, error_info
