import sys
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MyForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI(parent)

    def setupUI(self, parent):
        self.vbox = QVBoxLayout()
        self.but1 = QPushButton('button1')
        self.but2 = QPushButton('button2')
        self.but1.clicked.connect(self.clicked_func)
        self.but2.clicked.connect(self.clicked_func)
        self.vbox.addWidget(self.but1)
        self.vbox.addWidget(self.but2)
        self.setLayout(self.vbox)

    @pyqtSlot()
    def clicked_func(self):
        widget = self.sender()
        t = widget.text()
        QMessageBox.information(self, t, t)

class FormDI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI(parent)

    def setupUI(self, parent):
        self.hbox = QHBoxLayout()

        self.label = QLabel('디지털 인풋')
        self.label.setStyleSheet("background-color: yellow; border: 1px solid black;")
        self.label.setMinimumSize(100, 25)
        self.DI_1 = QPushButton('DI 1')
        self.DI_2 = QPushButton('DI 2')
        self.DI_3 = QPushButton('DI 3')
        self.DI_4 = QPushButton('DI 4')
        self.DI_5 = QPushButton('DI 5')

        self.DI_1.clicked.connect(self.clicked_func)
        self.DI_2.clicked.connect(self.clicked_func)
        self.DI_3.clicked.connect(self.clicked_func)
        self.DI_4.clicked.connect(self.clicked_func)
        self.DI_5.clicked.connect(self.clicked_func)

        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.DI_1)
        self.hbox.addWidget(self.DI_2)
        self.hbox.addWidget(self.DI_3)
        self.hbox.addWidget(self.DI_4)
        self.hbox.addWidget(self.DI_5)

        self.setLayout(self.hbox)

    @pyqtSlot()
    def clicked_func(self):
        widget = self.sender()
        t = widget.text()
        # QMessageBox.information(self, t, t)
        print(t)

    @pyqtSlot()
    def clicked_func(self):
        widget = self.sender()
        t = widget.text()
        # QMessageBox.information(self, t, t)
        print(t)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MyForm()
    mywindow.show()

    di = FormDI()
    di.show()

    app.exec_()


####################