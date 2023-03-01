import importlib


def dynamic_import(import_module):
    return importlib.import_module(import_module)


if __name__ == '__main__':
    custom = "Projects.Mercury_TS.Mercury_TS"

    module = dynamic_import(custom)

    # directory list of the imported module
    print(module.__name__)
    print(module.__doc__)
    print(dir(module))
