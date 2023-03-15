from Library.ProcessTest_new import *
from Library.tester import *
from Library.project import *

import os


def main():
    '''
    current_directory = os.getcwd()
    setting_directory = "Settings"
    setting_file = "global_settings.json"
    setting_tester_path = f"{current_directory}/{setting_directory}/{setting_file}"
    current_tester = DeviceTester(setting_tester_path)

    project_directory = "Projects"
    name_project = "Mercury_TS2"
    setting_project_path = f"{current_directory}/{project_directory}/{name_project}/"
    current_project = ProjectTestOS(setting_project_path)
    current_project.load_modules(current_tester.name, current_tester.version)
    '''

    process_test = ProcessTest('Mercury_TS2')
    process_test.start()


if __name__ == '__main__':
    main()
