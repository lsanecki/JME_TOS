import time
from Library.tester_service import *
from Library.project_support import *
import Library.device_procedures
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

        self.START_PROCESS = "Start"
        self.END_PROCESS = "Koniec"
        self.debug = debug
        self.step_log = None
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
        self.tester = DeviceTesterService(_setting_tester_path)

    def load_project_parameters(self, name_project):
        """
        Wczytuje dane projektu z pliku ustawień json
        :param name_project: Nazwa projektu do wczytania
        :return:
        """

        _current_directory = os.getcwd()
        _project_directory = "Projects"
        _setting_project_path = f"{_current_directory}/{_project_directory}/{name_project}/"
        self.project = ProjectTestSupport(_setting_project_path)
        self.project.load_test_modules(self.tester.name, self.tester.version)

    def start(self):
        """
        Uruchamia cały główny proces
        :return:
        """

        if self.project.initialization_enabled:
            self.start_initialization()

        self.start_test()

        if self.project.finalization_enabled:
            self.start_finalization()

    def start_initialization(self):
        """
        Uruchamia inicjalizacje
        :return:
        """
        self.step_log = []

        # print(f'Run_init: {self.project.init_test}')

        _name_step = self.START_PROCESS  # nazwa kroku który rozpoczyna proces

        while _name_step != self.END_PROCESS:
            # krok o nazwie 'Koniec' kończy dany process
            _name_step = self.perform_step(_name_step, self.project.test_initialization)

        self.show_log('init_listing')

    def start_test(self):
        """
        Uruchamia testowanie
        :return:
        """

        self.step_log = []

        _name_step = self.START_PROCESS  # nazwa kroku który rozpoczyna proces

        while _name_step != self.END_PROCESS:
            # krok o nazwie 'Koniec' kończy dany process
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
        funkcje urządzenia znajdują się w katalogu Library plik device_procedures.py
        :param current_step: Parametry kroku do wykonania
        :type current_step: dict
        :return: Zwraca nazwe nastepnego kroku do wykonania
        :rtype: str
        """

        for _device_procedure_parameters in current_step['Function']:
            _status = self.start_procedure_of_the_device(current_step, _device_procedure_parameters)
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

        if self.debug:
            print(procedure_parameters['NameFun'])
        _device_procedure_library = Library.device_procedures
        _procedure_information = self.prepare_test_procedure_information(procedure_parameters, current_step['Name'])
        _threads = []
        self.call_procedure(procedure_parameters, _procedure_information, _device_procedure_library, _threads)
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

        _imported_project_procedures = self.import_project_procedures()
        for _test_module_parameters in self.project.test_modules:
            for _test_socket_parameters in _test_module_parameters['Sockets']:
                for _project_procedure_parameters in current_step['Function']:
                    self.run_procedure_for_step_by_step_mode(
                        current_step, _project_procedure_parameters, _imported_project_procedures,
                        _test_module_parameters, _test_socket_parameters)

    def run_procedure_for_step_by_step_mode(self,
                                            current_step, procedure_parameters, project_procedures,
                                            test_module_parameters, test_socket_parameters):
        """
        Uruchom procedure/funkcje dla trybu Step by step
        :param current_step: Parametry kroku
        :type current_step: dict
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :param project_procedures: Biblioteka z zaimportowanymi funkcjami
        :type project_procedures: ModuleType
        :param test_module_parameters: Parametry modułu testującego
        :type test_module_parameters: dict
        :param test_socket_parameters: Parametry gniazda testujacego
        :type test_socket_parameters: dict
        :return:
        """

        self.show_data_of_the_called_procedure(procedure_parameters, test_module_parameters, test_socket_parameters)

        if self.read_status_of_previous_steps(test_module_parameters['Name'], test_socket_parameters['Name']) \
                or bool(current_step['AlwaysRun']):
            self.call_procedure_for_step_by_step_mode(current_step, procedure_parameters, project_procedures,
                                                      test_module_parameters, test_socket_parameters)

    def call_procedure_for_step_by_step_mode(self, current_step, procedure_parameters, project_procedures,
                                             test_module_parameters, test_socket_parameters):
        """
        Wywołaj procedure/funkcje dla trybu step by step
        :param current_step: Parmetry kroku
        :type current_step: dict
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :param project_procedures: Biblioteka z zaimportowanymi funkcjami
        :type project_procedures: ModuleType
        :param test_module_parameters: Parametry modułu testującego
        :type test_module_parameters: dict
        :param test_socket_parameters: Parametry gniazda testujacego
        :type test_socket_parameters: dict
        :return:
        """
        _procedure_information = self.prepare_test_procedure_information(procedure_parameters, current_step['Name'],
                                                                         test_module_parameters['Name'],
                                                                         test_socket_parameters['Name'])
        _threads = []
        self.call_procedure(procedure_parameters, _procedure_information, project_procedures, _threads,
                            test_socket_parameters['libFun'])
        self.wait_for_threads_to_finish(_threads)
        _status = []
        self.receive_data_from_threads(_status, _threads)

    def show_data_of_the_called_procedure(self, procedure_parameters, test_module_parameters, test_socket_parameters):
        """
        Wyswietla parametry modułu, gniazda i procedury
        :param procedure_parameters: Parametry procedury/funkcji do wykonania
        :type procedure_parameters: dict
        :param test_module_parameters: Parametry modułu testującego
        :type test_module_parameters: dict
        :param test_socket_parameters: Parametry gniazda testujacego
        :type test_socket_parameters: dict
        :return:
        """

        if self.debug:
            print(test_module_parameters, test_socket_parameters, procedure_parameters['NameFun'])

    def run_procedures_for_test_sockets_in_parallel(self, current_step):
        """
        Uruchom procedury/funkcje równolegle (wieluwątkach) dla każdego gniazda testującego
        :param current_step: Parametry kroku
        :type current_step: dict
        :return:
        """

        _imported_project_procedures = self.import_project_procedures()
        _threads = []
        for _test_module_parameters in self.project.test_modules:
            for _test_socket_parameters in _test_module_parameters['Sockets']:
                _test_socket_thread = threading.Thread(target=self.call_test_socket_in_separate_thread,
                                                       args=(_imported_project_procedures, _test_module_parameters,
                                                             _test_socket_parameters, current_step, _threads,))
                _test_socket_thread.start()
        self.wait_for_threads_to_finish(_threads)
        _status = []
        self.receive_data_from_threads(_status, _threads)

    def import_project_procedures(self):
        """
        Importuje procedury projectu (plik python)
        :return: Zaimportowane procedury
        :rtype: ModuleType
        """

        _project_procedure_library_to_import = f'Projects.{self.project.name_project}.{self.project.name_project}'
        _imported_project_procedures = dynamic_import(_project_procedure_library_to_import)
        if self.debug:
            print(_imported_project_procedures.__name__)
            print(self.project.test_modules)
        return _imported_project_procedures

    def receive_data_from_threads(self, status, threads):
        """
        Odbierz dane ze zbioru zakonczonych wątków
        :param status: status procedury testowej
        :type status: list
        :param threads: Zbiór wątków
        :type threads: list
        :return:
        """

        for _procedure_thread_data in threads:
            _received_data_from_thread = _procedure_thread_data[1].get()
            if self.debug:
                print('Return: {}'.format(_received_data_from_thread))
            _procedure_thread_data[2]['Status'] = _received_data_from_thread['Status']
            _procedure_thread_data[2]['ErrorInformation'] = _received_data_from_thread['ErrorInformation']
            _procedure_thread_data[2]['Date'] = _received_data_from_thread['Date']
            _procedure_thread_data[2]['TestTime'] = _received_data_from_thread['TestTime']
            _procedure_thread_data[2]['EndDate'] = _received_data_from_thread['EndDate']
            _procedure_thread_data[2]['Input'] = _received_data_from_thread['Input']
            _procedure_thread_data[2]['Output'] = _received_data_from_thread['Output']
            if _received_data_from_thread['Serial'] is not None:
                _procedure_thread_data[2]['Serial'] = _received_data_from_thread['Serial']
            if self.debug:
                print('_procedure_thread_data[2]: {}'.format(_procedure_thread_data[2]))
            self.step_log.append(_procedure_thread_data[2])
            status.append(_procedure_thread_data[2]['Status'])

    @staticmethod
    def wait_for_threads_to_finish(threads):
        """
        Czekaj na zakończenie watków ze zbioru
        :param threads: Zbiór watków
        :type threads: list
        :return:
        """

        for _procedure_thread_data in threads:
            _procedure_thread_data[0].join()

    def call_procedure(self, procedure_parameters, procedure_information, imported_project_procedures, threads,
                       test_socket_procedure_collection=None):
        """
        Wywołaj procedure/funkcje
        :param procedure_parameters: Parametry procedury/funkcji
        :type procedure_parameters: dict
        :param procedure_information: Informacje na temat wykonywanej procedury
        :type procedure_information: dict
        :param imported_project_procedures: Biblioteka z zaimportowanymi funkcjami
        :type imported_project_procedures: ModuleType
        :param threads: Zbiór wątków
        :type threads: list
        :param test_socket_procedure_collection: Parametry gniazda testującego
        :type test_socket_procedure_collection: ModuleType
        :return:
        """

        _procedure_thread_queue = queue.Queue()
        _procedure_thread = self.run_background_worker(imported_project_procedures, procedure_parameters['NameFun'],
                                                       procedure_parameters['Parameters'], _procedure_thread_queue,
                                                       procedure_parameters['Delay'], test_socket_procedure_collection)
        _thread_data = [_procedure_thread, _procedure_thread_queue, procedure_information]
        threads.append(_thread_data)
        return _procedure_thread

    @staticmethod
    def prepare_test_procedure_information(
            procedure_parameters, name_step, test_module_name=None, test_socket_name=None):
        """
        Przygotuj informacje na temat wywoływanej procedury/funkcji
        :param procedure_parameters: Parametry procedury
        :type procedure_parameters: dict
        :param name_step: Nazwa kroku
        :type name_step: str
        :param test_module_name: Nazwa modułu
        :type test_module_name: str
        :param test_socket_name: Nazwa gniazda
        :type test_socket_name: str
        :return: Zwraca wstępnie przygotowane dane do wykonanej procedurze
        :rtype: dict
        """

        _procedure_information = {
            'Name': name_step,
            'Module': test_module_name,
            'Dut': test_socket_name,
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
        return _procedure_information

    def call_test_socket_in_separate_thread(self, imported_project_procedures, test_module_parameters,
                                            test_socket_parameters, current_step, threads):
        """
        Wywołaj procedury gniazda testowego w osobnym wątku
        :param imported_project_procedures: Biblioteka z zaimportowanymi funkcjami
        :type imported_project_procedures: ModuleType
        :param test_module_parameters: Parametry modułu testowego
        :type test_module_parameters: dict
        :param test_socket_parameters: Parametry gniazda testujacego
        :type test_socket_parameters: dict
        :param current_step: Parametry kroku
        :type current_step: dict
        :param threads: Zbiór wątków
        :type threads: list
        :return:
        """

        for _procedure_parameters in current_step['Function']:
            self.show_data_of_the_called_procedure(_procedure_parameters, test_module_parameters,
                                                   test_socket_parameters)
            if self.read_status_of_previous_steps(test_module_parameters['Name'], test_socket_parameters['Name']) \
                    or bool(current_step['AlwaysRun']):
                _procedure_information = self.prepare_test_procedure_information(_procedure_parameters,
                                                                                 current_step['Name'],
                                                                                 test_module_parameters['Name'],
                                                                                 test_socket_parameters['Name'])
                _procedure_thread = self.call_procedure(_procedure_parameters, _procedure_information,
                                                        imported_project_procedures, threads,
                                                        test_socket_parameters['libFun'])
                _procedure_thread.join()

    def start_finalization(self):
        """
        Rozpocznij finalizacje
        :return:
        """

        self.step_log = []

        _name_step = self.START_PROCESS  # nazwa kroku który rozpoczyna proces
        print(self.project.test_finalization)

        while _name_step != self.END_PROCESS:
            # krok o nazwie koniec kończy dany process
            _name_step = self.perform_step(_name_step, self.project.test_finalization)

        self.show_log('final_listing')

    @background_worker
    def run_background_worker(self, imported_project_procedures, procedure_name, procedure_input_parameters,
                              procedure_thread_queue, delay, test_socket_procedure_collection=None):
        """
        Uruchamia procedury w nowo utworzonym wątku
        :param test_socket_procedure_collection: Moduł zaimportowanymi procedurami dla danego gniazda dut
        :type test_socket_procedure_collection: ModuleType
        :param imported_project_procedures: Moduł zaimportowanymi funkcjami projektu
        :type imported_project_procedures: ModuleType
        :param procedure_name: Nazwa uruchomionej funkcji
        :type procedure_name: str
        :param procedure_input_parameters: Parametry wejściowe funkcji
        :type procedure_input_parameters: list
        :param procedure_thread_queue: Obiekt przechwytujący dane z uruchomionego wątku
        :type procedure_thread_queue: queue.Queue
        :param delay: Opóżnienie w uruchomieniu wątku (wartości w ms)
        :return:
        """

        time.sleep(delay / 1000)
        _start_time = datetime.datetime.now()
        _item = getattr(imported_project_procedures, procedure_name)
        if callable(_item):
            if test_socket_procedure_collection is not None:
                _received_data_from_the_completed_procedure = _item(
                    procedure_input_parameters, test_socket_procedure_collection)
            else:
                _received_data_from_the_completed_procedure = _item(procedure_input_parameters)
            _serial_number = None
            if len(_received_data_from_the_completed_procedure) > 2:
                _serial_number = _received_data_from_the_completed_procedure[2]['Serial']

            _end_time = datetime.datetime.now()

            step_information = {'Step': None, 'Name': None, 'Module': None, 'Dut': None, 'NameFunction': procedure_name,
                                'Status': _received_data_from_the_completed_procedure[0],
                                'ErrorInformation': _received_data_from_the_completed_procedure[1],
                                'Date': _start_time, 'TestTime': _end_time - _start_time, 'EndDate': _end_time,
                                'Input': procedure_input_parameters,
                                'Output': _received_data_from_the_completed_procedure, 'Serial': _serial_number}

            procedure_thread_queue.put(step_information)

    def show_log(self, name_file, save_csv=True):
        """
        Metoda wyświetla liste przeprowadzonych testow wraz z danymi
        :param save_csv: Parametr określa czy zapisanać liste testow do pliku csv
        :type save_csv: bool
        :param name_file: Nazwa pliku CSV do zapisania wyniku
        :type name_file: str
        :return:
        """

        for _step_log in self.step_log:
            print(_step_log)

        if save_csv:
            self.save_log_to_csv_file(name_file)

    def save_log_to_csv_file(self, name_file):
        """
        Metoda zapisuje liste wykonanych testów do pliku csv
        :param name_file:Nazwa pliku CSV bez rozszerzenia .csv
        :type name_file: str
        :return:
        """

        _fields = []
        for name, dict_ in self.step_log[0].items():
            _fields.append(name)
        _filename = "Projects/{}/Test_listing/{}.csv".format(self.project.name_project, name_file)
        with open(_filename, 'w', newline='') as csvfile:
            _writer = csv.DictWriter(csvfile, fieldnames=_fields, delimiter=';', quotechar='"',
                                     quoting=csv.QUOTE_MINIMAL)

            _writer.writeheader()
            _writer.writerows(self.step_log)

    def read_status_of_previous_steps(self, test_module_name, test_socket_name):
        """
        Odczytuje status poprzednich kroków dla danego modułu i gniazda z loga
        :param test_module_name: Nazwa modulu
        :type test_module_name: str
        :param test_socket_name: Nazwa gniazda
        :type test_socket_name: str
        :return: Zwraca szukany status
        :rtype: bool
        """

        _read_status = True

        for _item in reversed(self.step_log):
            if _item['Module'] == test_module_name and _item['Dut'] == test_socket_name:
                _read_status = _read_status and _item['Status']

        if _read_status is None:
            _read_status = False

        if self.debug:
            print('Read_status: {}'.format(_read_status))

        return _read_status
