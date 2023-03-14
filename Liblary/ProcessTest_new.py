import time
from Liblary.libJson import *
from Liblary.testStep import *
from Liblary.global_function import *
from Liblary.tester import *
from Liblary.project import *
import Liblary.deviceFun
import datetime
import threading
import queue
import csv
import os


class ProcessTest:
    def __init__(self, _name_project, _debug=False):
        self.debug = _debug
        self.listing = None
        self.project = None
        self.tester = None
        self.load_tester()
        self.load_project(_name_project)

    def load_tester(self):
        current_directory = os.getcwd()
        setting_directory = "Settings"
        setting_file = "global_settings.json"
        setting_tester_path = f"{current_directory}/{setting_directory}/{setting_file}"
        self.tester = DeviceTester(setting_tester_path)

    def load_project(self, name_project):
        current_directory = os.getcwd()
        project_directory = "Projects"
        setting_project_path = f"{current_directory}/{project_directory}/{name_project}/"
        self.project = ProjectTestOS(setting_project_path)
        self.project.load_modules(self.tester.name, self.tester.version)

    def run(self):
        if self.project.init_enable:
            self.run_init()

        self.run_test()

        if self.project.final_enable:
            self.run_final()

    def run_init(self):
        self.listing = []

        # print(f'Run_init: {self.project.init_test}')

    def run_test(self):
        self.listing = []
        # print(f'Run_test: {self.project.test}')

        name_step = "Start"

        while name_step != "Koniec":
            name_step = self.execute_step(name_step, self.project.test)

        self.show_listing('test_listing')

    def execute_step(self, name_step, all_steps):
        print(f'NameStep: {name_step}')
        if self.debug:
            print(f'AllSteps: {all_steps}')
        current_step = next((sub for sub in all_steps if sub['Name'] == name_step), None)
        # print('step', current_step)

        if bool(current_step['OneTestForAllModule']):
            for function in current_step['Function']:
                print(function['NameFun'])
                _lib_fun = Liblary.deviceFun

                function_information = {
                    'Name': name_step,
                    'Module': None,
                    'Dut': None,
                    'NameFunction': function['NameFun'],
                    'Status': None,
                    'ErrorInformation': None,
                    'Date': None,
                    'TestTime': None,
                    'EndDate': None,
                    'Input': function['Parameters'],
                    'Output': None,
                    'Serial': None
                }

                threads = []
                que = queue.Queue()
                thread_fun = self.run_background_worker(_lib_fun, function['NameFun'], function['Parameters'], que,
                                                        function['Delay'])
                fun_step = [thread_fun, que, function_information]
                threads.append(fun_step)

                for thread_fun in threads:
                    thread_fun[0].join()

                _status = []
                for thread_fun in threads:
                    recv_info = thread_fun[1].get()
                    # if self.debug:
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
                    # if self.debug:
                    print('thread_fun[2]: {}'.format(thread_fun[2]))
                    self.listing.append(thread_fun[2])
                    _status.append(thread_fun[2]['Status'])

                if _status[0] is False and bool(current_step['AlwaysRun']) is False:
                    return current_step['FailTestNextStep']

        else:
            if bool(current_step['SetFlag']):
                project_function = f'Projects.{self.project.name_project}.{self.project.name_project}'
                lib_fun = dynamic_import(project_function)
                print(lib_fun.__name__)
                print(self.project.modules)
                for module in self.project.modules:
                    print(module)
                    for socket in module['Sockets']:
                        print(socket)

                        dut_lib = socket['libFun']
                        print(dut_lib)
                        for function in current_step['Function']:
                            if self.search_status_test_by_step_nr(module['Name'], socket['Name']) \
                                    or bool(current_step['AlwaysRun']):
                                print(function['NameFun'])
                                threads = []
                                function_information = {
                                    'Name': name_step,
                                    'Module': module['Name'],
                                    'Dut': socket['Name'],
                                    'NameFunction': function['NameFun'],
                                    'Status': None,
                                    'ErrorInformation': None,
                                    'Date': None,
                                    'TestTime': None,
                                    'EndDate': None,
                                    'Input': function['Parameters'],
                                    'Output': None,
                                    'Serial': None
                                }
                                que = queue.Queue()
                                thread_fun = self.run_background_worker(lib_fun, function['NameFun'],
                                                                        function['Parameters'], que,
                                                                        function['Delay'], socket['libFun'])
                                fun_step = [thread_fun, que, function_information]
                                threads.append(fun_step)

                                for thread_fun in threads:
                                    thread_fun[0].join()

                                _status = []
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

            else:
                project_function = f'Projects.{self.project.name_project}.{self.project.name_project}'
                lib_fun = dynamic_import(project_function)
                print(lib_fun.__name__)
                print(self.project.modules)
                threads = []
                for module in self.project.modules:
                    print(module)
                    for socket in module['Sockets']:
                        print(socket)
                        thread_fun = threading.Thread(target=self.thread_run_socket,
                                                      args=(lib_fun, module, socket, current_step, threads,))
                        thread_fun.start()
                for thread_fun in threads:
                    thread_fun[0].join()

                _status = []
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

        return current_step['NextStep']

    def thread_run_socket(self, _lib_fun, module, socket, current_step, _threads):
        for function in current_step['Function']:
            if self.search_status_test_by_step_nr(module['Name'], socket['Name']) \
                    or bool(current_step['AlwaysRun']):
                function_information = {
                    'Name': current_step['Name'],
                    'Module': module['Name'],
                    'Dut': socket['Name'],
                    'NameFunction': function['NameFun'],
                    'Status': None,
                    'ErrorInformation': None,
                    'Date': None,
                    'TestTime': None,
                    'EndDate': None,
                    'Input': function['Parameters'],
                    'Output': None,
                    'Serial': None
                }
                que = queue.Queue()
                thread_fun = self.run_background_worker(_lib_fun, function['NameFun'], function['Parameters'], que,
                                                        function['Delay'], socket['libFun'])
                fun_step = [thread_fun, que, function_information]
                _threads.append(fun_step)
                thread_fun.join()

    def run_final(self):
        self.listing = []
        # print(f'Run_final: {self.project.final_test}')

    @background_worker
    def run_background_worker(self, lib_fun, function_name, function_parameters, que, delay, lib_dut=None):
        """
        Uruchamia funkcje w nowo utworzonym wątku
        :param lib_dut:
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

    def show_listing(self, name_file, _save_csv=True):
        """
        Metoda wyświetla liste przeprowadzonych testow wraz z danymi
        :param _save_csv: Parametr określa czy zapisanać liste testow do pliku csv
        :type _save_csv: bool
        :param name_file:
        :return:
        """

        for step_listing in self.listing:
            print(step_listing)

        if _save_csv:
            self.save_listing_to_csv(name_file)

    def save_listing_to_csv(self, name_file):
        """
        Metoda zapisuje liste wykonanych testów do pliku csv
        :param name_file:
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

    def search_status_test_by_step_nr(self, _module_name=None, _dut_name=None):
        """
        Metoda szuka status dla podanego modułu i kroku
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
