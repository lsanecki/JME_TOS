from Library.json_settings_support import *
import Library.device_procedures
import Projects.Mercury_TS.Mercury_TS
import datetime
import threading
import queue


def set_option(param):
    if param == 1:
        return True
    return False


def run_test(test_steps):
    # nr_step = 10
    step_next_nr = 10

    while step_next_nr != 0:
        step_next_nr = run_step(step_next_nr, test_steps)


def run_step(nr_step, test_steps):
    step_test = TestStep()

    step = next((sub for sub in test_steps if sub['StepNr'] == nr_step), None)
    read_step_parameters(nr_step, step, step_test)
    now = datetime.datetime.now()
    print('[{}] {}: {} - {}'.format(now, step_test.nr, step_test.title, step_test.description))
    print(step_test.show_message)
    if step_test.one_test_all_module:
        for function in step_test.fun_for_all_module:
            now = datetime.datetime.now()
            print('[{}] K: {}, Funkcja: {}, Parametry: {}'.format(now,
                                                                  step_test.nr,
                                                                  function['NameFun'],
                                                                  function['Parameters']))

            lib_fun = Library.deviceFun
            test_information = [step_test.nr, function['NameFun']]

            threads = []

            run_function(function, lib_fun, test_information, threads)

            thread_join(threads)
            thread_load_return_data(threads)
    else:
        if step_test.flag:
            for module in step_test.module:
                for test_socket in module['Dut']:
                    for function in test_socket['Function']:
                        now = datetime.datetime.now()
                        print('[{}] K: {}, Modul: {}, Gniazdo: {}, Fun: {}, Parametry: {}'.format(now,
                                                                                                  step_test.nr,
                                                                                                  module['Name'],
                                                                                                  test_socket['Name'],
                                                                                                  function['NameFun'],
                                                                                                  function['Parameters']
                                                                                                  ))
                        lib_fun = Projects.Mercury_TS.Mercury_TS
                        test_information = [step_test.nr, module['Name'], test_socket['Name'], function['NameFun']]

                        threads = []

                        run_function(function, lib_fun, test_information, threads)

                        thread_join(threads)
                        thread_load_return_data(threads)

        else:
            threads = []

            for module in step_test.module:
                for test_socket in module['Dut']:
                    for function in test_socket['Function']:
                        now = datetime.datetime.now()
                        print('[{}] K: {} Modul: {}, Gniazdo: {}, Fun: {}, Parametry: {}'.format(now,
                                                                                                 step_test.nr,
                                                                                                 module['Name'],
                                                                                                 test_socket['Name'],
                                                                                                 function['NameFun'],
                                                                                                 function['Parameters']
                                                                                                 ))
                        lib_fun = Projects.Mercury_TS.Mercury_TS
                        test_information = [step_test.nr, module['Name'], test_socket['Name'], function['NameFun']]
                        run_function(function, lib_fun, test_information, threads)

            thread_join(threads)
            thread_load_return_data(threads)

            print('[{}] {}: Koniec'.format(now, step_test.nr))

    return step_test.next_nr


def thread_join(threads):
    for thread_fun in threads:
        thread_fun[0].join()


def thread_load_return_data(threads):
    for thread_fun in threads:
        print('Return: {}'.format(thread_fun[1].get()))


def run_function(function, lib_fun, test_information, threads):
    function_name = function['NameFun']
    function_parameters = function['Parameters']
    que = queue.Queue()
    item = getattr(lib_fun, function_name)
    if callable(item):
        thread_fun = threading.Thread(target=item, args=(function_parameters, test_information, que,))
        fun_step = [thread_fun, que]
        threads.append(fun_step)
        thread_fun.start()


def read_step_parameters(nr_step, step, step_test):
    step_test.nr = nr_step
    step_test.title = step['Title']
    step_test.description = step['Description']
    step_test.show_message = step['ShowMsg']
    step_test.delay = step['Delay']
    step_test.flag = set_option(step['SetFlag'])
    step_test.one_test_all_module = set_option(step['OneTestForAllModule'])
    step_test.fun_for_all_module = step['Function']
    step_test.next_nr = step['NextStep']
    step_test.fail_nr = step['FailTestNextStep']
    step_test.module = step['Module']


def main():
    set_json = JsonSettingSupport.load_file("Projects/Mercury_TS/Project_settings/ProjectSettings.json")

    # print(dir(fun_for_project))

    print(len(set_json['Project']))

    # Wczytanie danych
    project_setting = set_json['Project']['Settings']
    init_step = set_json['Project']['InitStep']
    test_step = set_json['Project']['TestStep']
    final_step = set_json['Project']['FinalStep']

    print(project_setting)
    print(init_step)
    print(len(test_step))
    # print(final_step)

    run_test(test_step)


if __name__ == '__main__':
    main()
