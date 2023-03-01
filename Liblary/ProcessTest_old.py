from Liblary.libJson import *
from Liblary.testStep import *
import Liblary.deviceFun
import datetime
import threading
import queue
import importlib
import csv


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

    @staticmethod
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
        self.project_init_enable = self.convert_to_bool(self.project_setting['EnableInitStep'])
        self.project_finally_enable = self.convert_to_bool(self.project_setting['EnableFinalStep'])
        self.project_function = 'Projects.{}.{}'.format(self.project_name, self.project_name)

    @staticmethod
    def dynamic_import(_import_module):
        """
        Metoda importuje modul z funkcjami dla danego projektu
        :param _import_module: Nazwa modułu który zostanie zaimportowany
        :type _import_module: str
        :return : Zwraca zaimportowany moduł
        :rtype: ModuleType
        """

        return importlib.import_module(_import_module)

    def run(self):
        """
        Metoda uruchamia testowanie według wytycznych z pliku ustawień projektu
        :return:
        """

        if self.project_init_enable:
            self.run_project_init()

        self.test_listing = []
        self.run_project_test()

        if self.project_finally_enable:
            self.run_project_finally()

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
                print('_status: {}'.format(_status))

                if not _status[0]:
                    return step_test.fail_nr
        else:
            lib_fun = self.dynamic_import(self.project_function)
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
                for function in test_socket['Function']:
                    self.execute_function_without_flag(function, _lib_fun, module, _step_test,
                                                       test_socket, threads)
        self.thread_join(threads)
        self.thread_load_return_data(threads)

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

    def execute_function_without_flag(self, _function, _lib_fun, _module, _step_test, _test_socket, _threads):
        """
        Metoda wykonuje funkcje dla danego gniazda DUT bez włączonej flagi 
        (w danym kroku fuknkcje sa wykonywane współbieżnie)
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
        :param _threads: Zbiór wszystkich aktywnych wątków
        :type _threads: list
        :return: 
        """

        _now = datetime.datetime.now()
        if self.debug:
            self.show_step_information(_function, _module, _now, _step_test, _test_socket)
        step_info = self.prepare_sub_step_info(_function['NameFun'],
                                               _now,
                                               _step_test,
                                               _module['Name'],
                                               _test_socket['Name'])
        self.run_function(_function, _lib_fun, _threads, step_info)

    @staticmethod
    def show_step_information(_function, _module, _now, _step_test, _test_socket):
        """
        Metoda wyświetla dane o aktualnie wykonywanej fukcji
        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _module: Wybrany moduł testujacy
        :type _module: dict
        :param _now: Data uruchomienia funkcji
        :type _now: Datetime
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: StepTest
        :param _test_socket: Wybranne gniazdo
        :type _test_socket: dict
        :return:
        """

        print('[{}] K: {} Modul: {}, Gniazdo: {}, Fun: {}, Parametry: {}'.format(_now,
                                                                                 _step_test.nr,
                                                                                 _module['Name'],
                                                                                 _test_socket[
                                                                                     'Name'],
                                                                                 _function[
                                                                                     'NameFun'],
                                                                                 _function[
                                                                                     'Parameters']
                                                                                 ))

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

        _now = datetime.datetime.now()
        if self.debug:
            self.show_step_information(_function, _module, _now, _step_test, _test_socket)

        step_info = self.prepare_sub_step_info(_function['NameFun'],
                                               _now,
                                               _step_test,
                                               _module['Name'],
                                               _test_socket['Name'])
        threads = []
        self.run_function(_function, _lib_fun, threads, step_info)
        self.thread_join(threads)
        self.thread_load_return_data(threads)

    def execute_function_for_all_module(self, _function, _step_test):
        """
        Metoda wykonuje funkcje dla całego kroku
        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: StepTest
        :return:
        """

        now = datetime.datetime.now()
        print('NameFun: {},CriticalFun: {}'.format(_function['NameFun'], _function['CriticalFun']))

        if self.debug:
            print('[{}] K: {}, Funkcja: {}, Parametry: {}'.format(now,
                                                                  _step_test.nr,
                                                                  _function['NameFun'],
                                                                  _function['Parameters']))
        lib_fun = Liblary.deviceFun
        step_info = self.prepare_sub_step_info(_function['NameFun'],
                                               now,
                                               _step_test)
        threads = []
        self.run_function(_function, lib_fun, threads, step_info)
        self.thread_join(threads)
        _status = self.thread_load_return_data_critical(threads)
        # self.search_status_test_by_step_nr(self.last_step, _step_information['Module'], _step_information['Dut'])
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

    @staticmethod
    def prepare_sub_step_info(_function, _now_date, _step_test, _module=None, _test_socket=None):
        """
        Meroda wczytuje dane o wykonywanej funkcji
        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _now_date: Data wykonywania funkcji
        :type _now_date: datetime.datetime
        :param _step_test: Informacje o aktualnie wykonywanym kroku
        :type _step_test: StepTest
        :param _module: Wybrany moduł testujacy
        :type _module: dict
        :param _test_socket: Wybranne gniazdo
        :type _test_socket: dict
        :return:
        """

        sub_step_info = FunctionInfo()
        sub_step_info.step_information['Step'] = _step_test.nr
        sub_step_info.step_information['Name'] = _step_test.title
        sub_step_info.step_information['NameFunction'] = _function
        sub_step_info.step_information['Date'] = _now_date
        sub_step_info.step_information['Module'] = _module
        sub_step_info.step_information['Dut'] = _test_socket
        step_info = sub_step_info.step_information
        return step_info

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
        _step_test.delay = _step['Delay']
        _step_test.flag = self.convert_to_bool(_step['SetFlag'])
        _step_test.one_test_all_module = self.convert_to_bool(_step['OneTestForAllModule'])
        _step_test.fun_for_all_module = _step['Function']
        _step_test.next_nr = _step['NextStep']
        _step_test.fail_nr = _step['FailTestNextStep']
        _step_test.module = _step['Module']

    def search_status_test_by_step_nr(self, _step_nr, _module_name, _dut_name):
        """
        Metoda szuka status wybranego kroku
        :param _step_nr: Nr kroku
        :type _step_nr: int
        :param _module_name: Nazwa modulu
        :type _module_name: str
        :param _dut_name: Nazwa gniazda
        :type _dut_name: str
        :return: Zwraca szukany status
        :rtype: bool
        """

        read_status = True

        for item in reversed(self.test_listing):
            if item['Step'] == _step_nr and item['Module'] == _module_name and item['Dut'] == _dut_name:
                read_status = read_status and item['Status']

        if read_status is None:
            read_status = False

        if self.debug:
            print('Read_status: {}'.format(read_status))
        return read_status

    def run_function(self, _function, _lib_fun, _threads, _step_information):
        """
        Metoda uruchamia aktualnie wybrana funkcje testu
        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _lib_fun: Moduł zaimportowanymi funkcjami projektu
        :type _lib_fun: ModuleType
        :param _threads: Zbiór wszystkich aktywnych wątków
        :type _threads: list
        :param _step_information: Informacje o aktualnie wykonywanym kroku
        :type _step_information: dict
        :return:
        """

        function_name, function_parameters, test_information = self.prepare_test_information_to_thread(_function,
                                                                                                       _step_information)
        if self.search_status_test_by_step_nr(self.last_step, _step_information['Module'], _step_information['Dut']):
            que = queue.Queue()
            item = getattr(_lib_fun, function_name)
            if callable(item):
                thread_fun = threading.Thread(target=item, args=(function_parameters, test_information, que,))
                fun_step = [thread_fun, que, _step_information]
                _threads.append(fun_step)
                thread_fun.start()

    @staticmethod
    def prepare_test_information_to_thread(_function, _step_information):
        """
        Metoda przygotowuje informacje wykonywanego testu do przekazania dla wywołanego wątku
        :param _function: Wykonywana funkcja
        :type _function: dict
        :param _step_information: Informacje o aktualnie wykonywanym kroku
        :type _step_information: dict
        :return: Zwraca odpowiednio przygotowane dane
        :rtype: tuple
        """

        test_information = [_step_information['Step'],
                            _step_information['Module'],
                            _step_information['Dut'],
                            _function['NameFun']]
        function_name = _function['NameFun']
        function_parameters = _function['Parameters']
        return function_name, function_parameters, test_information

    def thread_join(self, _threads):
        """
        Metoda czeka na zakończenie wszystkich wątków zawartych w podanej liście
        :param _threads: Lista aktualnych wątków
        :type _threads: list
        :return:
        """

        for thread_fun in _threads:
            thread_fun[0].join()

    def thread_load_return_data(self, _threads):
        """
        Metoda odczytuje dane z zakończonych wątków znajdujacych się w podanej liście
        :param _threads: Lista zakończonych wątków
        :type _threads: list
        :return:
        """

        for thread_fun in _threads:
            recv_info = thread_fun[1].get()
            if self.debug:
                print('Return: {}'.format(recv_info))
            thread_fun[2]['Status'] = recv_info[1]
            thread_fun[2]['ErrorInformation'] = recv_info[3]
            thread_fun[2]['TestTime'] = recv_info[0] - thread_fun[2]['Date']
            self.test_listing.append(thread_fun[2])

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

    def thread_load_return_data_critical(self, _threads):
        """
        Metoda odczytuje dane z zakończonych wątków znajdujacych się w podanej liście
        :param _threads: Lista zakończonych wątków
        :type _threads: list
        :return:
        """

        _status = []

        for thread_fun in _threads:
            recv_info = thread_fun[1].get()
            if self.debug:
                print('Return: {}'.format(recv_info))
            thread_fun[2]['Status'] = recv_info[1]
            thread_fun[2]['ErrorInformation'] = recv_info[3]
            thread_fun[2]['TestTime'] = recv_info[0] - thread_fun[2]['Date']
            self.test_listing.append(thread_fun[2])
            _status.append(thread_fun[2]['Status'])

        return _status
