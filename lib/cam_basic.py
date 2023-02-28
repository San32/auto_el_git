import sys
import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QAction

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.stopped = False

    def run(self):
        cap = cv2.VideoCapture(self.url)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640, 480))

        while not self.stopped:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(qt_image)

                out.write(frame)

        cap.release()
        out.release()

    def stop(self):
        self.stopped = True

class App(QWidget):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle("IP Camera Viewer")
        self.resize(640, 480)

        self.video_thread = VideoThread(url)
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.start()

        vbox_layout = QVBoxLayout()
        self.label = QLabel()
        vbox_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        hbox_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_video)
        hbox_layout.addWidget(self.save_button)

        self.stop_action = QAction("Stop", self)
        self.stop_action.setShortcut("Ctrl+S")
        self.stop_action.triggered.connect(self.stop_video)
        self.addAction(self.stop_action)

        vbox_layout.addLayout(hbox_layout)
        self.setLayout(vbox_layout)

    def update_image(self, qt_image):
        self.label.setPixmap(QPixmap.fromImage(qt_image))

    def save_video(self):
        self.video_thread.stop()
    
    def stop_video(self):
        self.video_thread.stop()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    url = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/18/media.smp"
    ex = App(url)
    ex.show()
    sys.exit(app.exec_())
