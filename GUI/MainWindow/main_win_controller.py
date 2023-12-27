from __future__ import unicode_literals

import os

from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from main_win_view import MainWinInterfaceUI
from Library.json_settings_support import JsonSettingSupport


class TableGridPosition:
    def __init__(self, count_row, count_column):
        self.count_row = count_row
        self.count_column = count_column
        self.actual_position = [0, 0]

    def get_actual_position(self):
        return self.actual_position

    def next_position(self):
        if self.actual_position[0] == self.count_column - 1:
            if self.actual_position[1] == self.count_row - 1:
                self.actual_position = [0, 0]
            else:
                self.actual_position = (0, self.actual_position[1] + 1)
        else:
            self.actual_position = (self.actual_position[0] + 1, self.actual_position[1])


class MainWinController(QWidget, MainWinInterfaceUI):
    def __init__(self, parent=None, ):
        super(MainWinController, self).__init__(parent, )
        self.setup_ui(self)

    def create_test_socket(self, sockets_parameters):
        table_position = TableGridPosition(2, 2)

        for item in sockets_parameters:
            # print(item['Name'])

            self.create_module(item, table_position.get_actual_position())
            table_position.next_position()

            # print(item['Sockets'])
            # for socket in item['Sockets']:
            #     print(socket['Name'])


def main():
    import sys

    path_project_settings = 'D:/PycharmProjects/JME_TOS/Projects/Mercury_TS/Project_settings/ProjectSettings.json'
    project_parameters = JsonSettingSupport.load_file(path_project_settings)

    project_modules_information = project_parameters['Project']['Settings']['Devices'][0]['Modules']

    app = QApplication(sys.argv)
    window = MainWinController()

    file_qss = open("main_win_style.qss", 'r')

    with file_qss:
        qss = file_qss.read()
        app.setStyleSheet(qss)

    # window.add_project_name_to_como_box(path_project)
    window.create_test_socket(project_modules_information)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
