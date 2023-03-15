import time
from Library.tester import *
from Library.project import *
import Library.deviceFun
import datetime
import threading
import queue
import csv
import os


class ProcessTest:
    def __init__(self, name_project, debug=False):
        """
        Konstruktor klasy ProcessTest
        :param name_project: Nazwa projektu który ma został załadowany
        :type name_project: str
        :param debug: Parametr określa czy tryb debugowania ma być włączony (domyśnie jest wyłączony)
        :type debug: bool
        """

        self.debug = debug
        self.listing = None
        self.project = None
        self.tester = None
        self.load_tester_parameters()
        self.load_project_parameters(name_project)

    def load_tester_parameters(self):
        """
        Wczytuje parametry urządzenia testującego z pliku json
        :return:
        """
        _current_directory = os.getcwd()
        _setting_directory = "Settings"
        _setting_file = "global_settings.json"
        _setting_tester_path = f"{_current_directory}/{_setting_directory}/{_setting_file}"
        self.tester = DeviceTester(_setting_tester_path)

    def load_project_parameters(self, name_project):
        """
        Wczytuje dane projektu z pliku ustawień json
        :param name_project: Nazwa projektu do wczytania
        :return:
        """

        _current_directory = os.getcwd()
        _project_directory = "Projects"
        _setting_project_path = f"{_current_directory}/{_project_directory}/{name_project}/"
        self.project = ProjectTestOS(_setting_project_path)
        self.project.load_modules(self.tester.name, self.tester.version)

    def start(self):
        """
        Uruchamia cały główny proces
        :return:
        """

        if self.project.init_enable:
            self.start_initialization()

        self.start_test()

        if self.project.final_enable:
            self.start_finalization()

    def start_initialization(self):
        """
        Uruchamia inicjalizacje
        :return:
        """
        self.listing = []

        # print(f'Run_init: {self.project.init_test}')

        _name_step = "Start"  # nazwa kroku który rozpoczyna proces

        while _name_step != "Koniec":
            # krok o nazwie koniec kończy dany process
            _name_step = self.perform_step(_name_step, self.project.init_test)

        self.show_log('init_listing')

    def start_test(self):
        """
        Uruchamia testowanie
        :return:
        """

        self.listing = []
        # print(f'Run_test: {self.project.test}')

        _name_step = "Start"  # nazwa kroku który rozpoczyna proces

        while _name_step != "Koniec":
            # krok o nazwie koniec kończy dany process
            _name_step = self.perform_step(_name_step, self.project.test)

        self.show_log('test_listing')

    def perform_step(self, name_step, all_steps):
        """
        Wykonaj krok poprzez podanie nazwy kroku do wykonanie
        :param name_step: Nazwa kroku
        :type name_step: str
        :param all_steps: Zbiór wszystkich kroków do wykonania
        :type all_steps: dict
        :return:
        """

        _current_step = self.load_selected_step(all_steps, name_step)

        if bool(_current_step['OneTestForAllModule']):
            return self.run_procedures_for_device(_current_step)
        else:
            if bool(_current_step['SetFlag']):
                self.run_step_by_step_procedures_for_test_sockets(_current_step)
            else:
                self.run_procedures_for_test_sockets_in_parallel(_current_step)
        return _current_step['NextStep']

    def load_selected_step(self, all_steps, name_step):
        """
        Wczytuje parametry wybranego kroku
        :param name_step: Nazwa kroku
        :type name_step: str
        :param all_steps: Zbiór wszystkich kroków do wykonania
        :type all_steps: dict
        :return:
        """

        print(f'NameStep: {name_step}')
        if self.debug:
            print(f'AllSteps: {all_steps}')
        _current_step = next((_sub for _sub in all_steps if _sub['Name'] == name_step), None)
        return _current_step

    def run_procedures_for_device(self, current_step):
        """
        Wykonuje wszystkie procedury/funkcje danego urzadzenia (testera) wedlug wczytanego kroku
        funkcje urządzenia znajdują się w katalogu Library plik deviceFun.py
        :param current_step: Parametry kroku do wykonania
        :type current_step: dict
        :return: Zwraca nazwe nastepnego kroku do wykonania
        :rtype: str
        """

        for function in current_step['Function']:
            _status = self.start_procedure_of_the_device(current_step, function)
            if _status[0] is False and bool(current_step['AlwaysRun']) is False:
                return current_step['FailTestNextStep']

        return current_step['NextStep']

    def start_procedure_of_the_device(self, current_step, procedure_parameters):
        """
        Wykonuje procedure/funkcje danego urzadzenia na podstawie podanych parametrów
        :param current_step: Parametry kroku do wykonania
        :type current_step: dict
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :return: Zwraca status wykonanej procedury
        :rtype: list
        """

        print(procedure_parameters['NameFun'])
        _lib_fun = Library.deviceFun
        _function_information = self.prepare_test_procedure_information(procedure_parameters, current_step['Name'])
        _threads = []
        self.call_procedure(procedure_parameters, _function_information, _lib_fun, _threads)
        self.wait_for_threads_to_finish(_threads)
        _status = []
        self.receive_data_from_threads(_status, _threads)
        return _status

    def run_step_by_step_procedures_for_test_sockets(self, current_step):
        """
        Uruchom krok po kroku procedury/funkcje we wszystkich gniazdach
        Korzysta z procedur/funkcji danego projektu wraz z procedurami danego gniazda testowego
        :param current_step: Parametry kroku do wykonania
        :return:
        """

        lib_fun = self.import_project_procedures()
        for module in self.project.modules:
            for socket in module['Sockets']:
                for function in current_step['Function']:
                    self.run_procedure_for_step_by_step_mode(current_step, function, lib_fun, module, socket)

    def run_procedure_for_step_by_step_mode(self, current_step, procedure_parameters, lib_fun, module, socket):
        """
        Uruchom procedure/funkcje dla trybu Step by step
        :param current_step: Parametry kroku
        :type current_step: dict
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :param lib_fun: Biblioteka z zaimportowanymi funkcjami
        :type lib_fun: ModuleType
        :param module: Parametry modułu testującego
        :type module: dict
        :param socket: Parametry gniazda testujacego
        :type socket: dict
        :return:
        """

        self.show_data_of_the_called_procedure(procedure_parameters, module, socket)

        if self.read_status_of_previous_steps(module['Name'], socket['Name']) \
                or bool(current_step['AlwaysRun']):
            self.call_procedure_for_step_by_step_mode(current_step, procedure_parameters, lib_fun, module, socket)

    def call_procedure_for_step_by_step_mode(self, current_step, procedure_parameters, lib_fun, module, socket):
        """
        Wywołaj procedure/funkcje dla trybu step by step
        :param current_step: Parmetry kroku
        :type current_step: dict
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :param lib_fun: Biblioteka z zaimportowanymi funkcjami
        :type lib_fun: ModuleType
        :param module: Parametry modułu testującego
        :type module: dict
        :param socket: Parametry gniazda testujacego
        :type socket: dict
        :return:
        """
        function_information = self.prepare_test_procedure_information(procedure_parameters, current_step['Name'], module['Name'],
                                                                       socket['Name'])
        threads = []
        self.call_procedure(procedure_parameters, function_information, lib_fun, threads, socket['libFun'])
        self.wait_for_threads_to_finish(threads)
        _status = []
        self.receive_data_from_threads(_status, threads)

    def show_data_of_the_called_procedure(self, procedure_parameters, module, socket):
        """
        Wyswietla parametry modułu, gniazda i procedury
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :param module: Parametry modułu testującego
        :type module: dict
        :param socket: Parametry gniazda testujacego
        :type socket: dict
        :return:
        """

        if self.debug:
            print(module, socket, procedure_parameters['NameFun'])

    def run_procedures_for_test_sockets_in_parallel(self, current_step):
        """
        Uruchom procedury/funkcje równolegle (wieluwątkach) dla każdego gniazda testującego
        :param current_step: Parametry kroku
        :type current_step: dict
        :return:
        """

        lib_fun = self.import_project_procedures()
        threads = []
        for module in self.project.modules:
            for socket in module['Sockets']:
                thread_fun = threading.Thread(target=self.call_test_socket_in_separate_thread,
                                              args=(lib_fun, module, socket, current_step, threads,))
                thread_fun.start()
        self.wait_for_threads_to_finish(threads)
        _status = []
        self.receive_data_from_threads(_status, threads)

    def import_project_procedures(self):
        """
        Importuje procedury projectu (plik python)
        :return: Zaimportowane procedury
        :rtype: ModuleType
        """

        project_function = f'Projects.{self.project.name_project}.{self.project.name_project}'
        lib_fun = dynamic_import(project_function)
        if self.debug:
            print(lib_fun.__name__)
            print(self.project.modules)
        return lib_fun

    def receive_data_from_threads(self, _status, threads):
        """
        Odbierz dane ze zbioru zakonczonych wątków
        :param _status: status procedury testowej
        :type _status: list
        :param threads: Zbiór wątków
        :type threads: list
        :return:
        """

        for thread_fun in threads:
            recv_info = thread_fun[1].get()
            if self.debug:
                print('Return: {}'.format(recv_info))
            thread_fun[2]['Status'] = recv_info['Status']
            thread_fun[2]['ErrorInformation'] = recv_info['ErrorInformation']
            thread_fun[2]['Date'] = recv_info['Date']
            thread_fun[2]['TestTime'] = recv_info['TestTime']
            thread_fun[2]['EndDate'] = recv_info['EndDate']
            thread_fun[2]['Input'] = recv_info['Input']
            thread_fun[2]['Output'] = recv_info['Output']
            if recv_info['Serial'] is not None:
                thread_fun[2]['Serial'] = recv_info['Serial']
            if self.debug:
                print('thread_fun[2]: {}'.format(thread_fun[2]))
            self.listing.append(thread_fun[2])
            _status.append(thread_fun[2]['Status'])

    @staticmethod
    def wait_for_threads_to_finish(threads):
        """
        Czekaj na zakończenie watków ze zbioru
        :param threads: Zbiór watków
        :type threads: list
        :return:
        """

        for thread_fun in threads:
            thread_fun[0].join()

    def call_procedure(self, procedure_parameters, function_information, lib_fun, threads, socket=None):
        """
        Wywołaj procedure/funkcje
        :param procedure_parameters: Parametry procedury/funkcji
        :type procedure_parameters: dict
        :param function_information: Informacje na temat wykonywanej procedury
        :type function_information: dict
        :param lib_fun: Biblioteka z zaimportowanymi funkcjami
        :type lib_fun: ModuleType
        :param threads: Zbiór wątków
        :type threads: list
        :param socket: Parametry gniazda testującego
        :type socket: dict
        :return:
        """

        que = queue.Queue()
        thread_fun = self.run_background_worker(lib_fun, procedure_parameters['NameFun'],
                                                procedure_parameters['Parameters'], que,
                                                procedure_parameters['Delay'], socket)
        fun_step = [thread_fun, que, function_information]
        threads.append(fun_step)
        return thread_fun

    @staticmethod
    def prepare_test_procedure_information(procedure_parameters, name_step, module_name=None, socket_name=None):
        """
        Przygotuj informacje na temat wywoływanej procedury/funkcji
        :param procedure_parameters: Parametry procedury
        :type procedure_parameters: dict
        :param name_step: Nazwa kroku
        :type name_step: str
        :param module_name: Nazwa modułu
        :type module_name: str
        :param socket_name: Nazwa gniazda
        :type socket_name: str
        :return: Zwraca wstępnie przygotowane dane do wykonanej procedurze
        :rtype: dict
        """

        function_information = {
            'Name': name_step,
            'Module': module_name,
            'Dut': socket_name,
            'NameFunction': procedure_parameters['NameFun'],
            'Status': None,
            'ErrorInformation': None,
            'Date': None,
            'TestTime': None,
            'EndDate': None,
            'Input': procedure_parameters['Parameters'],
            'Output': None,
            'Serial': None
        }
        return function_information

    def call_test_socket_in_separate_thread(self, _lib_fun, module, socket, current_step, _threads):
        """
        Wywołaj procedury gniazda testowego w osobnym wątku
        :param _lib_fun: Biblioteka z zaimportowanymi funkcjami
        :type _lib_fun: ModuleType
        :param module: Parametry modułu testowego
        :type module: dict
        :param socket: Parametry gniazda testujacego
        :type socket: dict
        :param current_step: Parametry kroku
        :type current_step: dict
        :param _threads: Zbiór wątków
        :type _threads: list
        :return:
        """

        for function in current_step['Function']:
            self.show_data_of_the_called_procedure(function, module, socket)
            if self.read_status_of_previous_steps(module['Name'], socket['Name']) \
                    or bool(current_step['AlwaysRun']):
                function_information = self.prepare_test_procedure_information(function, current_step['Name'], module['Name'],
                                                                               socket['Name'])
                thread_fun = self.call_procedure(function, function_information, _lib_fun, _threads, socket['libFun'])
                thread_fun.join()

    def start_finalization(self):
        """
        Rozpocznij finalizacje
        :return:
        """

        self.listing = []
        # print(f'Run_final: {self.project.final_test}')

        _name_step = "Start"  # nazwa kroku który rozpoczyna proces
        print(self.project.final_test)

        while _name_step != "Koniec":
            # krok o nazwie koniec kończy dany process
            _name_step = self.perform_step(_name_step, self.project.final_test)

        self.show_log('final_listing')


    @background_worker
    def run_background_worker(self, lib_fun, function_name, function_parameters, que, delay, lib_dut=None):
        """
        Uruchamia procedury w nowo utworzonym wątku
        :param lib_dut: Moduł zaimportowanymi procedurami dla danego gniazda dut
        :type lib_dut: ModuleType
        :param lib_fun: Moduł zaimportowanymi funkcjami projektu
        :type lib_fun: ModuleType
        :param function_name: Nazwa uruchomionej funkcji
        :type function_name: str
        :param function_parameters: Parametry wejściowe funkcji
        :type function_parameters: list
        :param que: Obiekt przechwytujący dane z uruchomionego wątku
        :type que: queue.Queue
        :param delay: Opóżnienie w uruchomieniu wątku (wartości w ms)
        :return:
        """

        time.sleep(delay / 1000)
        start_time = datetime.datetime.now()
        item = getattr(lib_fun, function_name)
        if callable(item):
            if lib_dut is not None:
                return_ext_module = item(function_parameters, lib_dut)
            else:
                return_ext_module = item(function_parameters)
            serial = None
            if len(return_ext_module) > 2:
                serial = return_ext_module[2]['Serial']

            end_time = datetime.datetime.now()

            step_information = {'Step': None, 'Name': None, 'Module': None, 'Dut': None, 'NameFunction': function_name,
                                'Status': return_ext_module[0], 'ErrorInformation': return_ext_module[1],
                                'Date': start_time, 'TestTime': end_time - start_time, 'EndDate': end_time,
                                'Input': function_parameters, 'Output': return_ext_module, 'Serial': serial}

            que.put(step_information)

    def show_log(self, name_file, _save_csv=True):
        """
        Metoda wyświetla liste przeprowadzonych testow wraz z danymi
        :param _save_csv: Parametr określa czy zapisanać liste testow do pliku csv
        :type _save_csv: bool
        :param name_file: Nazwa pliku CSV do zapisania wyniku
        :type name_file: str
        :return:
        """

        for step_listing in self.listing:
            print(step_listing)

        if _save_csv:
            self.save_log_to_csv_file(name_file)

    def save_log_to_csv_file(self, name_file):
        """
        Metoda zapisuje liste wykonanych testów do pliku csv
        :param name_file:Nazwa pliku CSV bez rozszerzenia .csv
        :type name_file: str
        :return:
        """

        fields = []
        for name, dict_ in self.listing[0].items():
            fields.append(name)
        filename = "Projects/{}/Test_listing/{}.csv".format(self.project.name_project, name_file)
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter=';', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)

            writer.writeheader()
            writer.writerows(self.listing)

    def read_status_of_previous_steps(self, _module_name, _dut_name):
        """
        Odczytuje status poprzednich kroków dla danego modułu i gniazda z loga
        :param _module_name: Nazwa modulu
        :type _module_name: str
        :param _dut_name: Nazwa gniazda
        :type _dut_name: str
        :return: Zwraca szukany status
        :rtype: bool
        """

        read_status = True

        for item in reversed(self.listing):
            if item['Module'] == _module_name and item['Dut'] == _dut_name:
                read_status = read_status and item['Status']

        if read_status is None:
            read_status = False

        if self.debug:
            print('Read_status: {}'.format(read_status))

        return read_status
