# from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QFrame, QLabel, QProgressBar, QLCDNumber, QComboBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt


class MainWinInterfaceUI(object):
    def __init__(self):
        self.close_app_button = None
        self.print_label_button = None
        self.project_settings_button = None
        self.change_project_button = None
        self.release_safety_button = None
        self.menu_layout = None
        self.test_layout = None
        self.separate_test_layout = None
        self.test_area_layout = None
        self.test_info_label = None
        self.test_info_layout = None
        self.project_info_name_label = None
        self.project_info_layout_vertical = None
        self.window_layout = None

    def setup_ui(self, widget):
        """
        Tworzy główne okno
        :param widget:
        :return:
        """
        widget.setObjectName("Widget")
        self.window_layout = QVBoxLayout(self)
        self.separate_test_layout = QHBoxLayout()

        self.test_layout = QVBoxLayout()

        self.project_info_layout_vertical = QVBoxLayout()

        self.project_info_name_label = QLabel("Nazwa projektu")
        self.project_info_layout_vertical.addWidget(self.project_info_name_label)

        self.test_layout.addLayout(self.project_info_layout_vertical)

        self.test_info_layout = QVBoxLayout()

        self.test_info_label = QLabel("Komunikaty")
        self.test_info_layout.addWidget(self.test_info_label)

        self.test_layout.addLayout(self.test_info_layout)

        self.test_area_layout = QGridLayout()
        # TODO: wczytaj z projektu
        self.test_layout.addLayout(self.test_area_layout)

        self.separate_test_layout.addLayout(self.test_layout)

        self.menu_layout = QVBoxLayout()

        self.release_safety_button = QPushButton("Zwolnij przycisk bezpieczeństwa")
        self.menu_layout.addWidget(self.release_safety_button)

        self.change_project_button = QPushButton("Zmień produkt")
        self.menu_layout.addWidget(self.change_project_button)

        self.project_settings_button = QPushButton('Ustawienia')
        self.menu_layout.addWidget(self.project_settings_button)

        self.print_label_button = QPushButton('Drukuj etykiete')
        self.menu_layout.addWidget(self.print_label_button)

        self.close_app_button = QPushButton('Zamknij aplikacje')
        self.menu_layout.addWidget(self.close_app_button)

        self.separate_test_layout.addLayout(self.menu_layout)

        self.window_layout.addLayout(self.separate_test_layout)

    def create_module(self, module_parameters, position):
        module_frame = QFrame()
        module_frame.setObjectName('module')
        module_layout = QVBoxLayout(module_frame)
        module_name_label = QLabel(module_parameters['Name'])
        module_layout.addWidget(module_name_label)
        print(module_parameters['Name'])

        print(position)
        layout_sockets = QHBoxLayout()

        for socket in module_parameters['Sockets']:
            frame_socket = QFrame()
            frame_socket.setObjectName('socket')
            print(socket['Name'])
            socket_layout = QVBoxLayout(frame_socket)

            socket_name_label = QLabel(socket['Name'])
            socket_name_label.setObjectName('name_socket')
            socket_layout.addWidget(socket_name_label)
            socket_status_label = QLabel('Status')
            socket_status_label.setObjectName('status_socket')
            socket_layout.addWidget(socket_status_label)

            layout_sockets.addWidget(frame_socket)
        module_layout.addLayout(layout_sockets)

        self.test_area_layout.addWidget(module_frame, position[1], position[0])
