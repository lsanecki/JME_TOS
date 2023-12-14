# from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QFrame, QLabel, QProgressBar, QLCDNumber, QComboBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt


class StartWinInterfaceUI(object):
    def __init__(self):
        self.label_logo = None
        self.button_close_device = None
        self.button_run_device = None
        self.combo_box_select_product = None
        self.label_select_product = None
        self.label_hello = None
        self.window_layout = None

    def setup_ui(self, widget):
        """Tworzy główne okno"""
        widget.setObjectName("Widget")
        self.window_layout = QVBoxLayout(self)
        self.label_logo = QLabel("Logo")
        self.window_layout.addWidget(self.label_logo)

        self.label_hello = QLabel("Witaj")
        self.label_hello.setObjectName("heading")
        self.window_layout.addWidget(self.label_hello)

        self.label_select_product = QLabel("Wybierz wyrob")
        self.label_select_product.setObjectName("subheading")
        self.window_layout.addWidget(self.label_select_product)

        self.combo_box_select_product = QComboBox()
        self.window_layout.addWidget(self.combo_box_select_product)

        self.button_run_device = QPushButton("Uruchom")
        self.window_layout.addWidget(self.button_run_device)
        
        self.button_close_device = QPushButton("Zakoncz")
        self.window_layout.addWidget(self.button_close_device)



def main():
    pass


if __name__ == "__main__":
    main()
