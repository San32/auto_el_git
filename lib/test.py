import os

from PyQt5.QtWidgets import * 
# from PyQt5 import QtCore
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import cv2
import numpy as np

front_image = '/home/comm/data/images/001410389_wheelchair_56.jpg'

class ThumbnailView(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(1000, 500)
        self.main_img = QLabel()
        self.setCentralWidget(self.main_img)

        # front_image = 'gugu.jpg'
        front_image = '/home/comm/data/images/001410389_wheelchair_56.jpg'

        # Check gugu.jpg file
        if os.path.isfile(front_image):

            # 아래 두 개의 코드는 동일함
            self.main_img.setPixmap(QPixmap(front_image).scaled(self.width(), self.height()))
            # self.main_img.setPixmap(QPixmap(front_image).scaled(self.width(), self.height(), Qt.IgnoreAspectRatio))
        else:
            print('no file')

class CamPanel(QWidget):
    def __init__(self, v_thread = None, vi = None, name = None, logger = None, w_pix = 400, h_pix = 300):
        super().__init__()
        self.v_thread = v_thread
        self.vi = vi
        self.name = name
        self.logger = logger
        self.w_pix = w_pix
        self.h_pix = h_pix
        self.detect_state = False

        self.initUI()

    def __del__(self):
        try:
            self.logger.info(f'CamPanel  __del__)')
        except:
            pass

    def init_btn_panel(self):
        panel_btn = QHBoxLayout()
        self.btn_run = QPushButton("load")
        self.btn_run.clicked.connect(self.run)
        self.btn_play = QPushButton("play")
        self.btn_play.clicked.connect(self.play)
        self.btn_stop = QPushButton("stop")
        self.btn_stop.clicked.connect(self.stop)
        self.btn_save = QPushButton("save")
        self.btn_save.clicked.connect(self.save)
        self.btn_loadmodel = QPushButton("model")
        self.btn_loadmodel.clicked.connect(self.loadmodel)
        self.btn_detect = QPushButton("detect")
        self.btn_detect.clicked.connect(self.detect)
        # self.cancelButton = QPushButton("Cancel")
        self.info_label = QLabel("info")

        panel_btn.addWidget(self.btn_run)
        panel_btn.addWidget(self.btn_play)
        panel_btn.addWidget(self.btn_stop)
        panel_btn.addWidget(self.btn_save)
        panel_btn.addWidget(self.btn_loadmodel)
        panel_btn.addWidget(self.btn_detect)
        panel_btn.addWidget(self.info_label)

        return panel_btn

    def init_img_panel(self):
        panel_img = QHBoxLayout()
        self.img_label = QLabel()
        self.img_label.setStyleSheet("background-color: cyan;")
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.img_label.setFixedSize(self.w_pix, self.h_pix)
        self.img_label.setStyleSheet("background-color:black;")

        # front_image = '/home/comm/data/images/001410389_wheelchair_56.jpg'

        # # Check gugu.jpg file
        # if os.path.isfile(front_image):

        #     # 아래 두 개의 코드는 동일함
        #     self.img_label.setPixmap(QPixmap(front_image).scaled(self.width(), self.height()))
        #     # self.main_img.setPixmap(QPixmap(front_image).scaled(self.width(), self.height(), Qt.IgnoreAspectRatio))
        # else:
        #     print('no file')

        panel_img.addWidget(self.img_label)

        return panel_img


    def initUI(self):

        panel_btn = self.init_btn_panel()
        panel_img = self.init_img_panel()

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(panel_img)
        self.main_layout.addLayout(panel_btn)

        # box_img = QHBoxLayout()
        # box_img.setContentsMargins(0, 0, 0, 0)
        
        # self.b2 = QPushButton("2")
        # box_img.addWidget(self.img_label)
        # # hbox.addWidget(self.b2)

        # 

        # vbox = QVBoxLayout()
        # vbox.addLayout(box_img)
        # vbox.addLayout(box_btn)

        self.setLayout(self.main_layout)
        self.update_image()

        # self.resize(640, 480)
    
    def closeEvent(self, QCloseEvent):
        print("panel Enter CloseEvent")
        QCloseEvent.accept()

    def run(self):
        self.logger.info(f'run clicked : {self.vi}')
        self.v_thread.start()

    def play(self):
        self.logger.info(f'play clicked : {self.vi}')
        self.v_thread.set_play()

    def stop(self):
        self.logger.info(f'stop clicked : {self.vi}')
        self.v_thread.set_stop()

    def save(self):
        self.logger.info(f'save clicked : {self.vi}')

    def loadmodel(self):
        self.v_thread.load_model()

    def detect(self):
        self.logger.info(f'detect clicked : {self.vi}')
        self.detect_state = not self.detect_state

        if self.detect_state: 
            self.v_thread.set_detect()
            self.btn_detect.setText("no detect")
        else:
            self.v_thread.clear_detect()
            self.btn_detect.setText("detecting...")

    def update_image(self):
        pixmap = QPixmap(front_image)
        if not pixmap.isNull():
            # aspectMode = Qt.IgnoreAspectRatio, Qt.KeepAspectRatio, Qt.KeepAspectRatioByExpanding)
            self.img_label.setPixmap(QPixmap(front_image).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
            self.img_label.adjustSize()
            # self.img_label.setPixmap(QPixmap(front_image).scaled(self.width(), self.height(), Qt.IgnoreAspectRatio))
            self.resize(pixmap.size())

    # @pyqtSlot(np.ndarray)
    # def update_image(self, cv_img):
    #     """Updates the image_label with a new opencv image"""
    #     qt_img = self.convert_cv_qt(cv_img)
    #     self.img_label.setPixmap(qt_img)
    #     # self.img_label.setPixmap(QPixmap(qt_img).scaled(self.width(), self.height()))

    # def convert_cv_qt(self, cv_img):
    #     """Convert from an opencv image to QPixmap"""
    #     rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    #     h, w, ch = rgb_image.shape
    #     bytes_per_line = ch * w
    #     convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #     # p = convert_to_Qt_format.scaled(self.w_pix, self.h_pix, Qt.KeepAspectRatio)
    #     p = convert_to_Qt_format.scaled(w, h, Qt.KeepAspectRatio)
    #     return QPixmap.fromImage(p)

    @pyqtSlot(str)
    def update_textLabel(self, text):
        self.info_label.setText(text)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # window = ThumbnailView()
    # CamPanel(self, v_thread, vi, name, logger, w_pix = 400, h_pix = 300):
    window = CamPanel()
    window.show()
    sys.exit(app.exec_())