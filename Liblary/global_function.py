import importlib
import threading


def dynamic_import(_import_module):
    """
    Metoda importuje modul z funkcjami dla danego projektu
    :param _import_module: Nazwa modułu który zostanie zaimportowany
    :type _import_module: str
    :return : Zwraca zaimportowany moduł
    :rtype: ModuleType
    """

    return importlib.import_module(_import_module)


def convert_to_bool(_parameter):
    """
    Metoda do konwersji parametru typu int na typ bool (dla 1 przyjmuje wartość True)
    :param _parameter: Parametr do konwersji na typ bool
    :type _parameter: int
    :return: Zwraca przekonwertowaną na typ bool wartość
    :rtype: bool
    """

    if _parameter == 1:
        return True
    return False


def run_background_method(function):
    """
    Uruchamia podaną funkcje/metodę w osobnym wątku (dekolator)
    :param function: Funkcja/ Metoda do uruchomienia w osobnym wątku
    :return:
    """

    def inside_function(*a, **kw):
        worker = threading.Thread(target=function, args=a, kwargs=kw)
        worker.start()

        return worker

    return inside_function
