from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSlot, Qt
import numpy as np
import VideoThread as v

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture Camera")
        self.width = 700
        self.height = 500

        #Creates button to start camera
        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)

        #Creates button to close camera
        self.close_button = QPushButton("Close Camera")
        self.close_button.clicked.connect(self.close_camera)

        #Create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.width, self.height)

        #Creates vbox and buttons and image_label
        self.original_layout = QVBoxLayout()
        self.original_layout.addWidget(self.image_label)
        self.original_layout.addWidget(self.start_button)
        self.original_layout.addWidget(self.close_button)

        # set the vbox layout as the widgets layout
        self.setLayout(self.original_layout)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    #Function to start camera
    def start_camera(self):

        self.thread = v.VideoThread()
        self.thread.change_pixmap_signal.connect(self.update)
        self.thread.start()

    #Function to close camera
    def close_camera(self):

        self.camera_active = False
        self.thread.stop()

        # Restore the original layout
        self.setLayout(self.original_layout)
        self.image_label.clear()

    def clearLayout(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    @pyqtSlot(np.ndarray)
    def update(self, cv_img):
        #updates label with new image
        qt_img = self.cv_to_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def cv_to_qt(self, cv_img):
        #converts opencv capture to qt capture
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt.scaled(self.width, self.height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)