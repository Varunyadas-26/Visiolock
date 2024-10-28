import sys
import os
import time
import cv2
import numpy as np
import datetime
import serial
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QSizePolicy)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QSize
from deepface import DeepFace  # Ensure you have DeepFace installed

# Constants
chat_id = 2135362504
bot = telepot.Bot('7493024394:AAF5AmVees3es8z2p6eSQuolS0I1M4xQKI8')  # Replace with your actual bot token

# Initialize global variables
runIs = True
sentcommand = 0
command = "0"
sendsecondscount = 0
onestring = "1"
zerostring = "0"
alertstring = "ALERT"
openstring = "OPEN"
atmode = 0
username = "NIL"
resetcount = 0
name = "NIL"

# Connect to Arduino
print('Connecting to Arduino........')
try:
    arduino = serial.Serial(port='COM3', baudrate=9600)
except:
    print('Failed to Connect with Arduino!')
    runIs = False
else:
    print("Successfully connected to the Arduino")

class LoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('VisioLock')
        self.setGeometry(200, 200, 300, 200)

        self.usernameLabel = QLabel('Username:', self)
        self.usernameTextBox = QLineEdit(self)
        self.passwordLabel = QLabel('Password:', self)
        self.passwordTextBox = QLineEdit(self)
        self.passwordTextBox.setEchoMode(QLineEdit.Password)
        self.loginButton = QPushButton('Login', self)
        self.errorLabel = QLabel('', self)

        layout = QVBoxLayout()
        layout.addWidget(self.usernameLabel)
        layout.addWidget(self.usernameTextBox)
        layout.addWidget(self.passwordLabel)
        layout.addWidget(self.passwordTextBox)
        layout.addWidget(self.loginButton)
        layout.addWidget(self.errorLabel)

        self.loginButton.clicked.connect(self.checkLogin)

        self.setLayout(layout)

    def checkLogin(self):
        global username
        username = self.usernameTextBox.text()
        password = self.passwordTextBox.text()

        if username in ['admin', 'user1'] and password in ['password', 'pass1']:
            self.hide()
            self.faceDetectionApp = FaceDetectionApp()
            self.faceDetectionApp.show()
        else:
            self.errorLabel.setText("Invalid credentials. Please try again.")

class FaceDetectionApp(QWidget):
    global username

    def __init__(self):
        super().__init__()
        self.camera = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_detected = False
        self.photo_counter = 1
        self.initUI()

    def initUI(self):
        global username
        self.setWindowTitle('VisioLock')
        self.setFixedSize(670, 600)

        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)
        self.label.setAlignment(Qt.AlignCenter)
        font = self.label.font()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setText("TURN ON CAMERA")

        self.startButton = QPushButton('Start Camera', self)
        self.stopButton = QPushButton('Stop Camera', self)

        self.nameTextBox = QLineEdit(self)
        self.nameTextBox.setPlaceholderText("Enter Name")

        self.snapButton = QPushButton('Snap', self)
        self.snapButton.clicked.connect(self.capturePhotos)

        button_size = QSize(100, 50)
        self.startButton.setFixedSize(button_size)
        self.stopButton.setFixedSize(button_size)
        self.nameTextBox.setFixedSize(100, 30)
        self.snapButton.setFixedSize(100, 30)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.startButton)
        button_layout.addWidget(self.stopButton)
        button_layout.addWidget(self.nameTextBox)
        button_layout.addWidget(self.snapButton)

        if username != "admin":
            self.snapButton.hide()
            self.nameTextBox.hide()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.startButton.clicked.connect(self.startCamera)
        self.stopButton.clicked.connect(self.stopCamera)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)

    def startCamera(self):
        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)

        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                height, width, channel = frame.shape
                self.label.setFixedSize(width, height)
                self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.timer.start(10)
                self.face_detected = True
        else:
            print("Error: Camera not accessible.")

    def stopCamera(self):
        self.timer.stop()
        self.face_detected = False
        if self.camera.isOpened():
            self.camera.release()
            self.label.clear()
            self.label.setAlignment(Qt.AlignCenter)
            font = self.label.font()
            font.setPointSize(20)
            self.label.setFont(font)
            self.label.setText("TURN ON CAMERA")
            self.showLoginScreen()

    def updateFrame(self):
        global atmode
        global username, resetcount, name, sentcommand, onestring, zerostring
        global alertstring, openstring

        if self.face_detected and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                if username == "admin":
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = img.shape
                    bytesPerLine = ch * w
                    qImg = QImage(img.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qImg)
                    self.label.setPixmap(pixmap)
                else:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                    if len(faces) > 0:
                        for face in faces:
                            (x, y, w, h) = face
                            face_crop = frame[y:y + h, x:x + w]
                            res = DeepFace.find(face_crop, db_path='Database/', enforce_detection=False, model_name='Facenet512')
                            if len(res[0]['identity']) > 0:
                                name = res[0]['identity'][0].split('/')
                                name = name[1]
                            else:
                                name = "Unknown"

                            for (x, y, w, h) in faces:
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                                cv2.putText(frame, name, (x, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, cv2.LINE_AA)

                            resetcount += 1
                            if name == "Unknown" and resetcount > 20:
                                if sentcommand == 0:
                                    sentcommand = 1
                                    arduino.write(zerostring.encode())
                                    time.sleep(2)
                                    arduino.flush()
                                    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    cv2.imwrite(f"unknown_{current_time}.jpg", frame)
                                    bot.sendPhoto(chat_id=chat_id, photo=open(f'unknown_{current_time}.jpg', 'rb'))
                                    bot.sendMessage(chat_id=chat_id, text="UNKNOWN PERSON DETECTED")
                                    sentcommand = 0

                                time.sleep(8)
                                resetcount = 0
                            else:
                                if resetcount > 20:
                                    if sentcommand == 0:
                                        sentcommand = 1
                                        arduino.write(onestring.encode())
                                        time.sleep(2)
                                        arduino.flush()
                                        bot.sendMessage(chat_id=chat_id, text=f"{name} APPROVED")
                                        sentcommand = 0
                                        resetcount = 0

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stopCamera()

    def capturePhotos(self):
        global name

        # Get the name from the QLineEdit widget
        current_name = self.nameTextBox.text().strip()

        if current_name == "":
            QMessageBox.warning(self, "Error", "Please enter your name.")
            return

        if self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                photo_path = f'photos/{current_name}_{self.photo_counter}.jpg'
                cv2.imwrite(photo_path, frame)
                self.photo_counter += 1
                QMessageBox.information(self, "Success", f"Photo saved as {photo_path}")

    def showLoginScreen(self):
        self.loginScreen = LoginScreen()
        self.loginScreen.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login = LoginScreen()
    login.show()
    sys.exit(app.exec_())
