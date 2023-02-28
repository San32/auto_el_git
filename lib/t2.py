from PyQt5.QtWidgets import * 
# from PyQt5 import QtCore
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import time
import numpy as np
import cv2
import sys

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.vi = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/18/media.smp"

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(self.vi)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()


class ImgFrame(QLabel):
    # ResizeSignal = pyqtSignal(int)
    def __init__(self, width, height):
        super().__init__()  
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setGeometry(0,0,width, height)
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(3)
        self.setText("")
        front_image = '/home/comm/data/images/001410389_wheelchair_56.jpg'

        self.pix = QPixmap(front_image)

        self.setPixmap(self.pix)
        self.installEventFilter(self)

    def paintEvent(self, event):        
        if not self.pix.isNull(): 
            size = self.size()
            painter = QPainter(self)

            point = QPoint(0,0)
            # scaledPix = self.pix.scaled(size, Qt.KeepAspectRatio, transformMode = Qt.FastTransformation)
            scaledPix = self.pix.scaled(size, Qt.IgnoreAspectRatio, transformMode = Qt.FastTransformation)
            # start painting the label from left upper corner
            # point.setX((size.width() - scaledPix.width())/2)
            # point.setY((size.height() - scaledPix.height())/2)
            painter.drawPixmap(point,scaledPix)

    @pyqtSlot(np.ndarray)
    def changePixmap(self, cv_img):
        self.pix = self.convert_cv_qt(cv_img)
        self.repaint() 

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)




class Cam(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Qt live label demo")

        """
        controll box
        """
        cont_box = QHBoxLayout()

        self.btn_play = QPushButton("Play", self)
        self.btn_play.setCheckable(True)
        self.btn_play.clicked.connect(self.change_btn_play)

        self.btn_detect = QPushButton("detect", self)
        self.btn_detect.setCheckable(True)

        self.btn_show = QPushButton("text", self)
        self.btn_show.setCheckable(True)

        cont_box.addWidget(self.btn_play)
        cont_box.addWidget(self.btn_detect)
        cont_box.addWidget(self.btn_show)

        """
        image Widget
        """
        # create the label that holds the image
        self.image_label = ImgFrame(400,300)

        """
        main Widget
        """
        main_box = QVBoxLayout()
        main_box.addWidget(self.image_label)
        main_box.addLayout(cont_box)

        self.setLayout(main_box)

        """
        thread 
        """
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.image_label.changePixmap)
    
    # method called by button
    def change_btn_play(self):
 
        # if button is checked
        if self.btn_play.isChecked():
 
            print("self.btn_play.isChecked()")
            # setting background color to light-blue
            self.btn_play.setStyleSheet("background-color : lightblue")
            self.thread._run_flag = True
            self.thread.start()
            self.btn_play.setText("Pause")
 
        # if it is unchecked
        else:
            print("unchecked")
            # set background color back to light-grey
            self.btn_play.setStyleSheet("background-color : lightgrey")
            # start the thread
            self.thread.stop()
            self.btn_play.setText("Play")

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt live label demo")
        self.disply_width = 800
        self.display_height = 480

        self.cam1 = Cam()
        self.cam1.thread.vi =  "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/18/media.smp"
        self.cam2 = Cam()
        self.cam2.thread.vi =  "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/19/media.smp"
        
        box = QHBoxLayout()
        box.addWidget(self.cam1)
        box.addWidget(self.cam2)

        self.setLayout(box)



if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())

