import time
import threading
import queue
import importlib


def dynamic_import(_import_module):
    """
    Metoda importuje modul z funkcjami dla danego projektu
    :param _import_module: Nazwa modułu który zostanie zaimportowany
    :type _import_module: str
    :return : Zwraca zaimportowany moduł
    :rtype: ModuleType
    """

    return importlib.import_module(_import_module)


def background_devFun(fun):
    print('Start: {}'.format(fun.__name__))

    def wew(*a, **kw):
        t1 = threading.Thread(target=fun, args=a, kwargs=kw)
        t1.start()

        return t1

    print('Stop: {}'.format(fun.__name__))

    return wew


@background_devFun
def przykladowa_fun(lib_fun, function_name, function_parameters, que):
    item = getattr(lib_fun, function_name)
    if callable(item):
        return_ext_module = item(function_parameters)
        print('return_ext_module: {}'.format(return_ext_module))
        que.put(return_ext_module)


que = queue.Queue()

project_function = 'Liblary.deviceFun'

lib_fun = dynamic_import(project_function)
name_fun = 'test1'
fun_param = [1, 2, 3]

thread1 = przykladowa_fun(lib_fun, name_fun, fun_param, que)
print('Czekam')
thread1.join()

print('Queue: {}'.format(que.get()))
