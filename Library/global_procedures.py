import importlib
import threading
import platform


def dynamic_import(_import_module):
    """
    Metoda importuje modul z funkcjami dla danego projektu
    :param _import_module: Nazwa modułu który zostanie zaimportowany
    :type _import_module: str
    :return : Zwraca zaimportowany moduł
    :rtype: ModuleType
    """

    return importlib.import_module(_import_module)


def background_worker(function):
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


def is_platform_windows():
    """
    Sprawdza czy korzystamy z systemu windows
    :return: Zwraca informacje czy korzystamy z windowsa
    :rtype: bool
    """
    return platform.system() == "Windows"


def is_platform_linux():
    """
    Sprawdza czy korzystamy z systemu linux
    :return: Zwraca informacje czy korzystamy z linuxa
    :rtype: bool
    :return:
    """
    return platform.system() == "Linux"
