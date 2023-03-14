import random
import time

min_time = 0
max_time = 1000


def fun1_1(param):
    time.sleep(random.randint(min_time, max_time) / 1000)
    module = 'module2'
    dut = "dut_left"
    print(f"Module: {module}, Dut: {dut}, Fun: fun1_1, input: {param}")
    status = True
    error_info = "0"

    return status, error_info
