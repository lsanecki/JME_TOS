import time

from Liblary.libJson import *
from Liblary.testStep import *
from Liblary.global_function import *
import Liblary.deviceFun
import datetime
import threading
import queue
import importlib
import csv


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


class ProcessTest:
    def __init__(self, _path_project, _debug=False):
        """
        Konstruktor klasy ProcessTest
        :param _path_project: Lokalizacja do testowanego projektu (wybieramy folder projektu)
        :type _path_project: str
        :param _debug: Paramater do uruchomienia debugowania dla testowanego projektu
        :type _debug: bool
        """

        self.last_step = None
        self.project_finally = None
        self.project_test = None
        self.project_init = None
        self.project_setting = None
        self.path_project_settings = None
        self.test_listing = None
        self.project_function = None
        self.project_finally_enable = None
        self.project_init_enable = None
        self.project_labels = None
        self.project_socket_in_module_count = None
        self.project_test_module_count = None
        self.project_index = None
        self.project_name = None
        self.debug = _debug
        self.path_project = _path_project
        self.load_project_from_file(_path_project)
        self.load_project_parameters()

    def load_project_from_file(self, _path_project):
        """
        Metoda do wczytania danych testowanego projektu z pliku Json
        :param _path_project: Lokalizacja do testowanego projektu (wybieramy folder projektu)
        :type _path_project: str
        :return:
        """

        self.path_project_settings = _path_project + 'Project_settings/ProjectSettings.json'
        _load_project_settings = JsonSetting.load_file(self.path_project_settings)
        self.project_setting = _load_project_settings['Project']['Settings']
        self.project_init = _load_project_settings['Project']['InitStep']
        self.project_test = _load_project_settings['Project']['TestStep']
        self.project_finally = _load_project_settings['Project']['FinalStep']

    def load_project_parameters(self):
        """
        Przypisuje parametry projektu
        :return:
        """

        self.project_name = self.project_setting['Name']
        self.project_index = self.project_setting['Index']
        self.project_test_module_count = self.project_setting['CountTestModule']
        self.project_socket_in_module_count = self.project_setting['Sockets']
        self.project_labels = self.project_setting['Labels']
        self.project_init_enable = convert_to_bool(self.project_setting['EnableInitStep'])
        self.project_finally_enable = convert_to_bool(self.project_setting['EnableFinalStep'])
        self.project_function = 'Projects.{}.{}'.format(self.project_name, self.project_name)

    def run(self):
        """
        Metoda uruchamia testowanie według wytycznych z pliku ustawień projektu
        :return:
        """

        if self.project_init_enable:
            self.run_project_init()

        self.test_listing = []
        self.run_project_test()
        # show result test

        self.show_test_result()

        if self.project_finally_enable:
            self.run_project_finally()

    def show_test_result(self):
        modules = []
        duts = []
        for step_listing in self.test_listing:
            modules.append(step_listing['Module'])
            duts.append(step_listing['Dut'])
        modules = list(set(modules))
        duts = list(set(duts))
        if self.debug:
            print('Modules', modules)
            print('Duts', duts)
        result_test = []
        for module in modules:
            for dut in duts:
                status = self.search_status_test_by_step_nr(module, dut)
                if module is not None and dut is not None:
                    test = {
                        'Module': module,
                        'Dut': dut,
                        'Status': status
                    }
                    result_test.append(test)
        print(result_test)

    def run_project_init(self):
        """
        Metoda uruchamia procedury inicjalizacji projektu
        :return:
        """

        pass

    def run_project_test(self):
        """
        Metoda uruchamia procedury testu projektu
        :return:
        """

        step_next_nr = 10

        while step_next_nr != 0:
            step_next_nr = self.run_step(step_next_nr)

    def run_step(self, _nr_step):
        """
        Metoda do wykonania wybranego kroku testu
        :param _nr_step: Numer kroku testu
        :type _nr_step: int
        :return: Zwraca numer kroku nastepnego testu
        :rtype: int
        """

        now, step_test = self.prepare_step(_nr_step)
        if step_test.one_test_all_module:
            for function in step_test.fun_for_all_module:
                _status = self.execute_function_for_all_module(function, step_test)
                # print('_status: {}'.format(_status))

                if not _status[0]:
                    return step_test.fail_nr
        else:
            lib_fun = dynamic_import(self.project_function)
            if step_test.flag:
                self.select_function_with_flag(lib_fun, step_test)
            else:
                self.select_function_without_flag(lib_fun, step_test)
        self.last_step = _nr_step
        return step_test.next_nr

    def select_function_without_flag(self, _lib_fun, _step_test):
        """
        Metoda do wybrania funkcji bez właczonej flagi, funkcje są wybierane w wielu wątkach
        :param _lib_fun: Moduł zaimportowanymi funkcjami projektu
        :type _lib_fun: ModuleType
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: TestStep
        :return:
        """

        threads = []
        for module in _step_test.module:
            for test_socket in module['Dut']:
                thread_fun = threading.Thread(target=self.thread_run_socket,
                                              args=(_lib_fun, module, test_socket, _step_test, threads,))
                thread_fun.start()

        # self.thread_join(threads)
        self.thread_function_join(threads)

        # self.thread_load_return_data(threads)
        _status = []
        self.load_return_function_info(_status, threads)

    def load_return_function_info(self, _status, threads):
        for thread_fun in threads:
            recv_info = thread_fun[1].get()
            if self.debug:
                print('Return: {}'.format(recv_info))
            thread_fun[2]['Status'] = recv_info['Status']
            thread_fun[2]['ErrorInformation'] = recv_info['ErrorInformation']
            thread_fun[2]['Date'] = recv_info['Date']
            thread_fun[2]['TestTime'] = recv_info['TestTime']
            thread_fun[2]['EndDate'] = recv_info['EndDate']
            if self.debug:
                print('thread_fun[2]: {}'.format(thread_fun[2]))
            self.test_listing.append(thread_fun[2])
            _status.append(thread_fun[2]['Status'])

    def thread_function_join(self, threads):
        for thread_fun in threads:
            thread_fun[0].join()

    def thread_run_socket(self, _lib_fun, _module, _test_socket, _step_test, _threads):
        for _function in _test_socket['Function']:
            if self.search_status_test_by_step_nr(_module['Name'], _test_socket['Name']) or _step_test.always_run:
                if self.debug:
                    self.show_function_info(_function, _step_test.nr, _module, _test_socket)

                fun_info = self.prepare_function_info(_function['NameFun'], _step_test, _module['Name'],
                                                      _test_socket['Name'])

                thread_fun = self.execute_function(_function, _lib_fun, _threads, fun_info)
                thread_fun.join()

    @staticmethod
    def show_function_info(_function, _step_nr, _module=None, _test_socket=None):
        _name_module = _module['Name']
        _name_dut = _test_socket['Name']
        _name_function = _function['NameFun']
        _function_parameters = _function['Parameters']
        print(
            f'[{datetime.datetime.now()}] '
            f'K: {_step_nr} '
            f'Modul: {_name_module}, '
            f'Gniazdo: {_name_dut}, '
            f'Fun: {_name_function}, '
            f'Parametry: {_function_parameters}')

    def execute_function(self, _function, _lib_fun, _threads, fun_info):
        que = queue.Queue()
        thread_fun = self.run_background(_lib_fun, _function['NameFun'], _function['Parameters'], que,
                                         _function['Delay'])
        fun_step = [thread_fun, que, fun_info]
        _threads.append(fun_step)
        return thread_fun

    @staticmethod
    def prepare_function_info(_name_function, _step_test, _name_module=None, _name_dut=None):
        function_information = {
            'Step': _step_test.nr,
            'Name': _step_test.title,
            'Module': _name_module,
            'Dut': _name_dut,
            'NameFunction': _name_function,
            'Status': None,
            'ErrorInformation': None,
            'Date': None,
            'TestTime': None,
            'EndDate': None
        }

        return function_information

    def select_function_with_flag(self, _lib_fun, _step_test):
        """
        Metoda do wybrania funkcji z włączoną flagą, funkcje są wybierane po kolei
        :param _lib_fun: Moduł zaimportowanymi funkcjami projektu
        :type _lib_fun: ModuleType
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: TestStep
        :return:
        """

        for module in _step_test.module:
            for test_socket in module['Dut']:
                for function in test_socket['Function']:
                    self.execute_function_with_flag(function, _lib_fun, module, _step_test, test_socket)

    def execute_function_with_flag(self, _function, _lib_fun, _module, _step_test, _test_socket):
        """
        Metoda wykonuje funkcje dla danego gniazda DUT krok po kroku (flaga wlaczona)

        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _lib_fun: Moduł zaimportowanymi funkcjami projektu
        :type _lib_fun: ModuleType
        :param _module: Wybrany moduł testujacy
        :type _module: dict
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: StepTest
        :param _test_socket: Wybranne gniazdo
        :type _test_socket: dict
        :return:
        """
        if self.search_status_test_by_step_nr(_module['Name'], _test_socket['Name']) or _step_test.always_run:
            if self.debug:
                self.show_function_info(_function, _step_test.nr, _module['Name'], _test_socket['Name'])

            threads = []
            fun_info = self.prepare_function_info(_function['NameFun'], _step_test, _module['Name'],
                                                  _test_socket['Name'])
            self.execute_function(_function, _lib_fun, threads, fun_info)

            _status = []

            self.thread_function_join(threads)

            self.load_return_function_info(_status, threads)

    def execute_function_for_all_module(self, _function, _step_test):
        """
        Metoda wykonuje funkcje dla całego kroku
        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: StepTest
        :return:
        """

        if self.debug:
            self.show_function_info(_function, _step_test.nr)
        _lib_fun = Liblary.deviceFun

        threads = []
        fun_info = self.prepare_function_info(_function['NameFun'], _step_test)

        self.execute_function(_function, _lib_fun, threads, fun_info)

        self.thread_function_join(threads)

        _status = []

        self.load_return_function_info(_status, threads)

        return _status

    def prepare_step(self, _nr_step):
        """
        Metoda wczytuje krok do testowania
        :param _nr_step: Numer kroku do wczytania
        :type _nr_step: int
        :return: Zwraca parametru wczytanego kroku
        :rtype: tuple
        """

        step_test = TestStep()
        step = next((sub for sub in self.project_test if sub['StepNr'] == _nr_step), None)
        self.load_step_parameters(_nr_step, step, step_test)
        now = datetime.datetime.now()
        print('[{}] {}: {} - {}'.format(now, step_test.nr, step_test.title, step_test.description))
        # print(step_test.show_message)
        return now, step_test

    def load_step_parameters(self, _nr_step, _step, _step_test):
        """
        Metoda przypisuje dane wykonywanego kroku do objektu StepTest
        :param _nr_step: Numer wybranego kroku
        :type _nr_step: int
        :param _step: Dane aktualnie wykonywanego kroku
        :type _step: dict
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: StepTest
        :return:
        """

        _step_test.nr = _nr_step
        _step_test.title = _step['Title']
        _step_test.description = _step['Description']
        _step_test.show_message = _step['ShowMsg']
        _step_test.flag = convert_to_bool(_step['SetFlag'])
        _step_test.one_test_all_module = convert_to_bool(_step['OneTestForAllModule'])
        _step_test.fun_for_all_module = _step['Function']
        _step_test.next_nr = _step['NextStep']
        _step_test.fail_nr = _step['FailTestNextStep']
        _step_test.module = _step['Module']
        _step_test.always_run = convert_to_bool(_step['AlwaysRun'])

    def search_status_test_by_step_nr(self, _module_name=None, _dut_name=None):
        """
        Metoda szuka status
        :param _module_name: Nazwa modulu
        :type _module_name: str
        :param _dut_name: Nazwa gniazda
        :type _dut_name: str
        :return: Zwraca szukany status
        :rtype: bool
        """

        read_status = True

        for item in reversed(self.test_listing):
            if item['Module'] == _module_name and item['Dut'] == _dut_name:
                read_status = read_status and item['Status']

        if read_status is None:
            read_status = False

        if self.debug:
            print('Read_status: {}'.format(read_status))

        return read_status

    def run_project_finally(self):
        """
        Metoda uruchamia procedury finalizacji projektu
        :return:
        """

        pass

    def show_test_listing(self, _save_csv=True):
        """
        Metoda wyświetla liste przeprowadzonych testow wraz z danymi
        :param _save_csv: Parametr określa czy zapisanać liste testow do pliku csv
        :return:
        """

        for step_listing in self.test_listing:
            print(step_listing)

        if _save_csv:
            self.save_listing_to_csv()

    def save_listing_to_csv(self):
        """
        Metoda zapisuje liste wykonanych testów do pliku csv
        :return:
        """

        fields = []
        for name, dict_ in self.test_listing[0].items():
            fields.append(name)
        filename = f"Projects/{self.project_name}/Test_listing/test_listing.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

            writer.writeheader()
            writer.writerows(self.test_listing)

    @run_background_method
    def run_background(self, lib_fun, function_name, function_parameters, que, delay=0):
        time.sleep(delay / 1000)
        start_time = datetime.datetime.now()
        item = getattr(lib_fun, function_name)
        if callable(item):
            return_ext_module = item(function_parameters)
            # print('return_ext_module: {}'.format(return_ext_module))

            end_time = datetime.datetime.now()

            step_information = {'Step': None, 'Name': None, 'Module': None, 'Dut': None, 'NameFunction': function_name,
                                'Status': return_ext_module[0], 'ErrorInformation': return_ext_module[1],
                                'Date': start_time, 'TestTime': end_time - start_time, 'EndDate': end_time}

            que.put(step_information)
