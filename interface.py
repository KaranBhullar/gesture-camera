import mediapipe as mp
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import time

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        #mediapipe
        self.mp_hands = mp.solutions.hands  # Initialize MediaPipe hands
        self.hands = self.mp_hands.Hands()  # Create a Hands object
        self.mp_drawing = mp.solutions.drawing_utils  # Drawing utilities
        self.ok_gesture_detected = False
        self.ok_gesture_start_time = None

    def run(self):
        #Video Capture
        cap = cv2.VideoCapture(0)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                processed_frame = self.process_frame(cv_img)
                self.change_pixmap_signal.emit(cv_img)

                if self.ok_gesture_detected:
                    if time.time() - self.ok_gesture_start_time >= 3:
                        cv2.imwrite("snapshot.jpg", cv_img)
                        self.ok_gesture_detected = False  # Reset gesture flag
        #Shuts down system
        cap.release()

    def process_frame(self, frame):
        # Convert frame to RGB for MediaPipe
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = self.hands.process(rgb_image)

        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                
                              # Check thumb and index finger tip landmarks (simplified for brevity)
                thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip= hand_landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]

                # Calculate distance between thumb and index finger tips
                distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5

                # Threshold for 'OK' gesture (adjust as needed)
                if distance < 0.1 and middle_tip.y < index_tip.y and ring_tip.y < index_tip.y :  
                    self.ok_gesture_detected = True
                    self.ok_gesture_start_time = time.time()  # Record start time

        return frame


    def stop(self):
        #run_flag set to false
        self._run_flag = False
        self.wait()


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

        self.thread = VideoThread()
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
    
if __name__=="__main__":
    app = QApplication(sys.argv)
    a = App()
    a.show()
    sys.exit(app.exec_())