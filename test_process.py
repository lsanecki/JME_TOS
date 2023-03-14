from Liblary.ProcessTest import *

import os


def main():
    path_project = 'Projects/Mercury_TS/'
    if not os.path.exists(path_project):
        print("Project nie istnieje")
        exit(1)

    tester = ProcessTest(path_project)

    tester.run()

    print('ID: {}'.format(id(tester)))
    # tester.show_test_listing()


if __name__ == '__main__':
    main()
