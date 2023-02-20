from Liblary.libJson import *


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
    step = next((sub for sub in test_steps if sub['StepNr'] == nr_step), None)
    step_title = step['Title']
    step_description = step['Description']
    step_show_message = step['ShowMsg']
    step_delay = step['Delay']
    step_set_flag = set_option(step['SetFlag'])
    step_one_test_all_module = set_option(step['OneTestForAllModule'])
    step_fun_for_all_module = step['Function']
    step_next_nr = step['NextStep']
    step_fail_nr = step['FailTestNextStep']
    step_module = step['Module']
    print('{}: {} - {}'.format(nr_step, step_title, step_description))
    return step_next_nr


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
