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
