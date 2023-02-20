from Liblary.libJson import *
from Liblary.testStep import *
import Liblary.deviceFun

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
    print('{}: {} - {}'.format(step_test.nr, step_test.title, step_test.description))
    print(step_test.show_message)
    if step_test.one_test_all_module:
        for function in step_test.fun_for_all_module:
            function_name = function['NameFun']
            function_parameters = function['Parameters']
            item = getattr(Liblary.deviceFun, function_name)
            if callable(item):
                item(function_parameters)


    else:
        if step_test.flag:
            pass

    return step_test.next_nr


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
    set_json = JsonSetting.load_file("Projects/sample_project/Project_settings/ProjectSettings.json")
    print(len(set_json['Project']))

    # Wczytanie danych
    project_setting = set_json['Project']['Settings']
    init_step = set_json['Project']['InitStep']
    test_step = set_json['Project']['TestStep']
    final_step = set_json['Project']['FinalStep']

    print(project_setting)
    # print(init_step)
    print(len(test_step))
    # print(final_step)

    run_test(test_step)


if __name__ == '__main__':
    main()
