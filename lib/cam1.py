from PyQt5.QtWidgets import * 
# from PyQt5 import QtCore
from PyQt5.QtGui import * 
from PyQt5.QtCore import *
from PyQt5.QtTest import *
import sys

import numpy as np
import cv2
from time import time
from datetime import datetime
import qimage2ndarray
import queue 

import log
import torch

from PIL import Image, ImageFont, ImageDraw

#path set
yolov5_path = '/home/comm/data/yolov5'
pt_path = '/home/comm/conda_work/cv2/auto_el_git/data/weights/best.pt'


class Colors:
    # Ultralytics color palette https://ultralytics.com/
    def __init__(self):
        # hex = matplotlib.colors.TABLEAU_COLORS.values()
        hexs = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb(f'#{c}') for c in hexs]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))

colors = Colors()


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    thread_state_signal = pyqtSignal(str)

    def __init__(self, vi, default_img, name, logger):
        super().__init__()
        self.logger = logger
        self.__working = False
        self.__play_flag = False
        self.__detect_flag = False
        self.__save_flag = False
        self.model = None
        self.vi = vi
        self.default_img = cv2.imread(default_img)
        self.default_cv_img = cv2.imread(default_img)
        self.name = name
        self.q = queue.Queue(1)
        self.last_frame = None
        # self.load_model()
        fontpath = "/usr/share/fonts/truetype/nanum/NanumMyeongjo.ttf"
        self.font = ImageFont.truetype(fontpath, 20)

    def __del__(self):
        try:
            self.cap.release()
            self.logger.info(f'VideoThread __del__,  cap.release()')
        except:
            pass

    """queue를 사용하여 계속해서 입력하고,
    flag를 확인해서 처리한다
    """
    def run(self):
        count = 0
        re_count = 0
        self.logger.info(f'thread start')
        self.cap = cv2.VideoCapture(self.vi)
        self.logger.info(f'connecting {self.vi}...')
        QTest.qWait(1000)

        while(True):
            """cap.isOpened 이면 처리
            False 이면 reconnect
            """
            if self.cap.isOpened():
                w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                try:
                    re_count = 0
                    while(True):
                        if self.cap.isOpened():
                            # self.logger.info(f'camera is open : {self.vi}...')
                            check, frame = self.cap.read()
                            fps = ''
                            if check:
                                self.last_frame = frame
                            else:
                                # pass
                                print("check fault")
                                self.cap.release()
                                # QTest.qWait(1000)
                                self.cap = cv2.VideoCapture(self.vi)
                                QTest.qWait(1000)
                                break

                            if self.__play_flag: #화면 play
                                if self.__detect_flag:
                                    if self.model != None: 
                                        start_time = time()
                                        results = self.score_frame(self.last_frame)
                                        self.last_frame, label_list = self.plot_boxes(results, self.last_frame)
                                        end_time = time()
                                        # fps = 1/np.round(end_time - start_time, 3)
                                        fps = int(1./(end_time - start_time ))
                                        fps = "FPS : %0.1f" % fps
                                        label_list = "label_list"
                                self.change_pixmap_signal.emit(self.put_text(self.last_frame, label_list, w, h, fps))
                                # QTest.qWait(100)
                            else:
                                label_list = "label_list  2222"
                                self.change_pixmap_signal.emit(self.put_text(self.default_img, label_list, w, h, fps))

                                # QTest.qWait(1000)
                                # self.logger.info(f'play : {self.vi} : {count}')
                                # self.thread_state_signal.emit(f'{count}')
                                # self.change_pixmap_signal.emit(self.default_img)
                            
                        else:
                            self.logger.info(f'cap.isOpened() : faile {self.vi}...')
                            break
                except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                    print('예외가 발생했습니다.', e)
                    self.logger.info(f' cap.isOpened() try 예외가 발생했습니다.')
                    self.cap.release()
                        
                # # QTest.qWait(1000)
                # now = datetime.now()
                # tt = now.strftime('%Y-%m-%d %H:%M:%S')
                # self.logger.info(f"현재시간 : {tt}")
            else:  # cap.isOpened(): False // reconnect
                re_count = 0
                while(True):
                    try:
                        # QTest.qWait(1000) 
                        self.cap.release()
                        self.cap = cv2.VideoCapture(self.vi)
                        QTest.qWait(1000) 

                        if self.cap.isOpened():
                            self.logger.info(f'connect OK {self.vi}...')
                            break
                        else: 
                            re_count = re_count +1
                            self.logger.info(f'camera failed {re_count} times : {self.vi}...')
                        
                    except:
                        self.logger.info(f're connect try failed {self.vi}...')
        
    def put_text(self, frame, label_list, w, h, fps):
        # 한글 표출
        img_pillow = Image.fromarray(frame)
        draw = ImageDraw.Draw(img_pillow)
        b,g,r,a = 0,0,255,255

        text = self.name
        draw.text((10,30), text, font=self.font, fill=(b,g,r,a)) #text를 출력

        text = self.vi
        draw.text((10,50), text, font=self.font, fill=(b,g,r,a)) #text를 출력

        text = f'width:{w} height:{h}'
        draw.text((10,100), text, font=self.font, fill=(b,g,r,a)) #text를 출력

        text = label_list
        draw.text((10,150), text, font=self.font, fill=(b,g,r,a)) #text를 출력

        frame = np.array(img_pillow) #다시 OpenCV가 처리가능하게 np 배열로 변환

        # cv2.putText(frame, self.name,(10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        # cv2.putText(frame, self.vi,(10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        # cv2.putText(frame, f'width:{w} height:{h}',(10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        # cv2.putText(frame, f'FPS:{fps}',(10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        return frame



    def set_play(self):
        self.__play_flag = True

    def set_stop(self):
        self.__play_flag = False

    def set_detect(self):
        self.__detect_flag = True

    def clear_detect(self):
        self.__detect_flag = False

    def load_model(self):
        """
        Loads Yolo5 model from pytorch hub.
        :return: Trained Pytorch model.
        """
        self.model = torch.hub.load(yolov5_path, 'custom',source='local', path=pt_path, force_reload=True)
        self.classes = self.model.names
        # self.out_file = out_file
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(self.device)
    
    def score_frame(self, frame):
        """
        Takes a single frame as input, and scores the frame using yolo5 model.
        :param frame: input frame in numpy/list/tuple format.
        :return: Labels and Coordinates of objects detected by model in the frame.
        """
        self.model.to(self.device)
        frame = [frame]
        results = self.model(frame)
        labels, cord = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:, :-1].cpu().numpy()
        return labels, cord

    def class_to_label(self, x):
        """
        For a given label value, return corresponding string label.
        :param x: numeric label
        :return: corresponding string label
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Takes a frame and its results as input, and plots the bounding boxes and label on to the frame.
        :param results: contains labels and coordinates predicted by model on the given frame.
        :param frame: Frame which has been scored.
        :return: Frame with bounding boxes and labels ploted on it.
        """
        labels, cord = results
        label_list = []
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:
                x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
                str = self.class_to_label(labels[i]) + ": %0.1f" % row[4]
                cv2.rectangle(frame, (x1, y1), (x2, y2), colors(int(labels[i])), 2)
                cv2.putText(frame, str, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, colors(int(labels[i])), 2)
                label_list.append(str)
        return frame , label_list

            
  
class CamPanel(QWidget):
    def __init__(self, v_thread, vi, name, logger, w_pix = 400, h_pix = 300):
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

    def initUI(self):

        box_img = QHBoxLayout()
        box_img.setContentsMargins(0, 0, 0, 0)
        self.img_label = QLabel()
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.img_label.setFixedSize(self.w_pix, self.h_pix)
        self.img_label.setStyleSheet("background-color:black;")
        self.b2 = QPushButton("2")
        box_img.addWidget(self.img_label)
        # hbox.addWidget(self.b2)

        box_btn = QHBoxLayout()
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

        box_btn.addWidget(self.btn_run)
        box_btn.addWidget(self.btn_play)
        box_btn.addWidget(self.btn_stop)
        box_btn.addWidget(self.btn_save)
        box_btn.addWidget(self.btn_loadmodel)
        box_btn.addWidget(self.btn_detect)
        box_btn.addWidget(self.info_label)

        vbox = QVBoxLayout()
        vbox.addLayout(box_img)
        vbox.addLayout(box_btn)

        self.setLayout(vbox)

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

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.img_label.setPixmap(qt_img)
        # self.img_label.setPixmap(QPixmap(qt_img).scaled(self.width(), self.height()))

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # p = convert_to_Qt_format.scaled(self.w_pix, self.h_pix, Qt.KeepAspectRatio)
        p = convert_to_Qt_format.scaled(w, h, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    @pyqtSlot(str)
    def update_textLabel(self, text):
        self.info_label.setText(text)

    


if __name__ == "__main__":
    import sys
    logger = log.get_logger("test")

    app = QApplication(sys.argv)
    default_img = '/home/comm/data/images/001410389_wheelchair_56.jpg'
    vi = "rtsp://admin:asdQWE12!%40@101.122.3.11:558/LiveChannel/18/media.smp"
    name = "시청역 E/L"

    v_thread = VideoThread(vi, default_img, name, logger)
    camPanel = CamPanel(v_thread, vi, name, logger)
    
    v_thread.change_pixmap_signal.connect(camPanel.update_image)
    v_thread.thread_state_signal.connect(camPanel.update_textLabel)

    camPanel.show()
    sys.exit(app.exec_())