import mediapipe as mp
import numpy as np
import cv2
import time
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

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
