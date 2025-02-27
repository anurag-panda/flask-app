import cv2
import numpy as np
from datetime import datetime

class Camera:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_face(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            return True, (x, y, w, h)
        return False, None

    def process_frame(self, frame):
        face_detected, face_rect = self.detect_face(frame)
        if face_detected:
            (x, y, w, h) = face_rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()
