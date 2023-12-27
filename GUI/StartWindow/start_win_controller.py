from __future__ import unicode_literals

import os

from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from start_win_view import StartWinInterfaceUI


class StartWinController(QWidget, StartWinInterfaceUI):
    def __init__(self, parent=None, ):
        super(StartWinController, self).__init__(parent, )
        self.setup_ui(self)
        self.add_logo()
        self.set_hello_label()

    def add_project_name_to_como_box(self, path_projects_dir):
        list_project = os.listdir(path_projects_dir)
        self.combo_box_select_product.addItems(list_project)

    def add_logo(self):
        path_logo = 'image/JM_logoIkona.png'
        self.label_logo.setPixmap(QPixmap(path_logo))

    def set_hello_label(self):
        self.label_hello.setAlignment(QtCore.Qt.AlignCenter)


def main():
    import sys

    path_project = 'D:/PycharmProjects/JME_TOS/Projects'

    app = QApplication(sys.argv)
    window = StartWinController()

    file_qss = open("start_win_style.qss", 'r')

    with file_qss:
        qss = file_qss.read()
        app.setStyleSheet(qss)

    window.add_project_name_to_como_box(path_project)

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
