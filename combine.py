# -----------------------------------------------------------
# Face Mask Detection System With Alert Function
#
# (C) 2021 Lo Hong Kai, 0198293
# UOW KDU PG UNIVERSITY COLLEGE
# Final Year Project 2021
# -----------------------------------------------------------

import re
import smtplib
import sys
import time
import tkinter
import tkinter.messagebox
import urllib
from email.message import EmailMessage
from urllib.request import urlopen

import cv2
import imutils
import numpy as np
import pyrebase
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from imutils.video import VideoStream
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

firebaseConfig = {
    'apiKey': "AIzaSyBZRN-qaq0NluYrPUxg6l1m2ppmpVQt4-0",
    'authDomain': "face-mask-detection-2021-8710d.firebaseapp.com",
    'databaseURL': "https://face-mask-detection-2021-8710d-default-rtdb.firebaseio.com/",
    'projectId': "face-mask-detection-2021-8710d",
    'storageBucket': "face-mask-detection-2021-8710d.appspot.com",
    'messagingSenderId': "78703109154",
    'appId': "1:78703109154:web:11a0b3be7bee28a057567b",
    'measurementId': "G-VDV219Y7T0"
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()


# //////////// LOGIN ///////////////////////
class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        print("[INFO] starting login ui...")
        loadUi("ui/login.ui", self)

        self.password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.loginButton.clicked.connect(self.loginfunction)
        self.createAccButton.clicked.connect(self.gotocreate)

        self.errorMessage.setVisible(False)

    def loginfunction(self):
        # Check internet connection
        if not is_internet():
            self.errorMessage.setText("Please check you internet connection or try again later.")
            self.errorMessage.setVisible(True)
        else:
            email = self.email.text()
            password = self.password.text()
            # Check is empty
            if not email or not password:
                self.errorMessage.setText("All fields cannot be empty.")
                self.errorMessage.setVisible(True)
            else:
                # Validate the email
                regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.fullmatch(regex, email):
                    self.errorMessage.setText("Invalid email format.")
                    self.errorMessage.setVisible(True)
                else:
                    try:
                        # login here
                        user = auth.sign_in_with_email_and_password(email, password)
                        # After login
                        uid = user['localId']
                        print("Successfully logged in with email: ", email, "and Password: ", password)
                        self.gotoDetectorScreen(email, uid)
                    except:
                        self.errorMessage.setText("Incorrect email or password.")
                        self.errorMessage.setVisible(True)

    def gotocreate(self):
        createacc = CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoDetectorScreen(self, email, uid):
        ui_OutputDialog = MaskDetector(email, uid)
        widget.addWidget(ui_OutputDialog)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# //////////// CREATE ACCOUNT ///////////////////////
class CreateAcc(QDialog):
    def __init__(self):
        super(CreateAcc, self).__init__()
        print("[INFO] starting register ui...")
        loadUi("ui/register.ui", self)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmPassword.setEchoMode(QtWidgets.QLineEdit.Password)

        self.registerButton.clicked.connect(self.createaccfunction)
        self.loginhereButton.clicked.connect(self.gotologin)

        self.errorMessage.setVisible(False)

    def createaccfunction(self):
        # Check internet connection
        if not is_internet():
            self.errorMessage.setText("Please check you internet connection or try again later.")
            self.errorMessage.setVisible(True)
        else:
            email = self.email.text()
            input_password = self.password.text()
            confirmPassword = self.confirmPassword.text()
            # Check is empty
            if not email or not input_password or not confirmPassword:
                self.errorMessage.setText("All fields cannot be empty.")
                self.errorMessage.setVisible(True)
            else:
                # Validate the email
                regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                if not re.fullmatch(regex, email):
                    self.errorMessage.setText("Invalid email format.")
                    self.errorMessage.setVisible(True)
                else:
                    # Compare password
                    if input_password == confirmPassword:
                        password = confirmPassword
                        # validate password
                        if len(password) < 8:
                            self.errorMessage.setText("Password must have at least 8 characters.")
                            self.errorMessage.setVisible(True)
                        elif re.search('[0-9]', password) is None:
                            self.errorMessage.setText("Password must has at least a digit.")
                            self.errorMessage.setVisible(True)
                        elif re.search('[A-Z]', password) is None:
                            self.errorMessage.setText("Password must has at least 1 uppercase letter.")
                            self.errorMessage.setVisible(True)
                        elif re.search('[a-z]', password) is None:
                            self.errorMessage.setText("Password must has at least 1 lowercase letter.")
                            self.errorMessage.setVisible(True)
                        elif re.search('[@#$%^&*?]', password) is None:
                            self.errorMessage.setText("Password must has at least 1 special symbols.")
                            self.errorMessage.setVisible(True)
                        else:
                            try:
                                # Register here
                                auth.create_user_with_email_and_password(email, password)
                                print("Successfully registered with email:", email, "and Password:", password)
                                msg = QtWidgets.QMessageBox()
                                msg.setIcon(QtWidgets.QMessageBox.Information)
                                msg.setText("Account has been successfully created.")
                                msg.setWindowTitle("Register")
                                msg.exec_()

                                self.gotologin()
                            except:
                                self.errorMessage.setText("Email has already been taken.")
                                self.errorMessage.setVisible(True)
                    else:
                        self.errorMessage.setText("Passwords doesn't match!")
                        self.errorMessage.setVisible(True)

    def gotologin(self):
        login = Login()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# //////////// DETECTION SCREEN ///////////////////////
class MaskDetector(QDialog):
    def __init__(self, email, uid):
        super(MaskDetector, self).__init__()
        print("[INFO] starting detector screen...")
        self.email = email
        self.uid = uid
        print("Email at detector:", email)
        print("ID at detector:", uid)
        self.available_cameras = QCameraInfo.availableCameras()
        # if not self.available_cameras:
        #     print("No Camera la")
        #     pass  # quit

        loadUi("ui/camera.ui", self)

        # Update date & time
        now = QDate.currentDate()
        current_date = now.toString('dddd - dd MMMM yyyy')
        self.dateLabel.setText(current_date)
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)  # update every second
        self.showTime()

        self.cameraComboBox.addItems([c.description() for c in self.available_cameras])
        self.cameraComboBox.currentIndexChanged.connect(self.select_camera)
        # Mask detector screen
        self.Worker = Worker(0, email, uid)
        self.Worker.start()
        self.Worker.ImageUpdate.connect(self.ImageUpdateSlot)

        # Quit
        self.quitButton.clicked.connect(self.closeEvent)

    # time
    def showTime(self):
        currentTime = QTime.currentTime()
        # hh: 12hour format / HH: 24hour format
        displayTxt = currentTime.toString('HH:mm:ss ap')
        self.timeLabel.setText(displayTxt)

    def select_camera(self, i):
        # change camera source here
        print("Index:", i)
        # i = 0;
        self.Worker = Worker(i, self.email)
        self.Worker.start()
        self.Worker.ImageUpdate.connect(self.ImageUpdateSlot)

    def ImageUpdateSlot(self, Image):
        self.cameraLabel.setPixmap(QPixmap.fromImage(Image))

    # Quit
    def closeEvent(self, event):
        msgBox = QMessageBox(
            QMessageBox.Question,
            "Face Mask Detection System",
            "Are you sure you want to exit the application?",
            buttons=QMessageBox.Yes | QMessageBox.No
        )
        msgBox.setDefaultButton(QMessageBox.No)
        # msgBox.setStyleSheet("QLabel{ color: white}")
        msgBox.exec_()
        reply = msgBox.standardButton(msgBox.clickedButton())
        if reply == QMessageBox.Yes:
            sys.exit()


# //////////// CAMERA WORKER ///////////////////////
class Worker(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, index, email, uid):
        QThread.__init__(self)
        self.index = index
        self.email = email
        self.uid = uid
        print("Email at worker: ", email)
        print("ID at worker: ", uid)

    def detect_and_predict_mask(self, frame, faceNet, maskNet):
        # grab the dimensions of the frame and then construct a blob
        # from it
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224), (104.0, 177.0, 123.0))

        # pass the blob through the network and obtain the face detections
        faceNet.setInput(blob)
        detections = faceNet.forward()
        # print(detections.shape)

        # initialize our list of faces, their corresponding locations,
        # and the list of predictions from our face mask network
        faces = []
        locs = []
        preds = []

        # loop over the detections
        for i in range(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the detection
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the confidence is
            # greater than the minimum confidence
            if confidence > 0.5:
                # compute the (x, y)-coordinates of the bounding box for
                # the object
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # ensure the bounding boxes fall within the dimensions of
                # the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                # extract the face ROI, convert it from BGR to RGB channel
                # ordering, resize it to 224x224, and preprocess it
                face = frame[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                # add the face and bounding boxes to their respective
                # lists
                faces.append(face)
                locs.append((startX, startY, endX, endY))

        # only make a predictions if at least one face was detected
        if len(faces) > 0:
            # for faster inference we'll make batch predictions on *all*
            # faces at the same time rather than one-by-one predictions
            # in the above `for` loop
            faces = np.array(faces, dtype="float32")
            preds = maskNet.predict(faces, batch_size=32)

        # return a 2-tuple of the face locations and their corresponding
        # locations
        return locs, preds

    def check(self):
        # Detect in real time
        # load our serialized face detector model from disk
        prototxtPath = r"face_detector\deploy.prototxt"
        weightsPath = r"face_detector\res10_300x300_ssd_iter_140000.caffemodel"
        faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

        # load the face mask detector model from disk
        maskNet = load_model("model/new_mask_detector.model")

        # initialize the video stream
        print("[INFO] starting video stream...")
        vs = VideoStream(src=self.index).start()

        # loop over the frames from the video stream
        self.ThreadActive = True
        while self.ThreadActive:
            # grab the frame from the threaded video stream and resize it
            # to have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=800)

            # detect faces in the frame and determine if they are wearing a face mask or not
            (locs, preds) = self.detect_and_predict_mask(frame, faceNet, maskNet)

            # loop over the detected face locations and their corresponding locations
            for (box, pred) in zip(locs, preds):
                # unpack the bounding box and predictions
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred

                if withoutMask > 0.995 or mask == 1:
                    # determine the class label and color we'll use to draw the bounding box and text
                    label = "Mask" if mask > withoutMask else "No Mask"
                    color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

                    # include the probability in the label
                    label_text = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                    # display the label and bounding box rectangle on the output frame
                    cv2.putText(frame, label_text, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

                    if label == "No Mask":
                        print("No Mask: ", withoutMask)

                        # get date and time
                        date = time.strftime("%Y-%m-%d")
                        date2 = time.strftime("%d-%b-%Y")
                        imageTime = time.strftime("%H:%M:%S %p")
                        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")

                        # capture the unmask ppl
                        print("[INFO] capturing the unmask people...")
                        img_name = "violators_img/Unmasked_ppl_{}.jpg".format(timestamp)
                        cv2.imwrite(img_name, frame)
                        print("[INFO] {} written!".format(img_name))

                        if is_internet():
                            # send email here
                            content = 'Person has been detected without face mask.\n\n' \
                                      'Date: ' + date2 + '\nTime: ' + imageTime
                            sender_Email = "facemaskdetector2021@gmail.com"
                            receiver_Email = self.email
                            password = "Facemask123"
                            self.sendEmail(sender_Email, receiver_Email, password, img_name, content)
                            print("[INFO] Email sent")

                            # Add to database
                            uid = self.uid
                            data = {"time": imageTime, "image": img_name}
                            db.child(uid).child(date).child(imageTime).set(data)
                            db.child(uid).child("date").push(date)
                            print("[INFO] Record added to database")

                        # Alert message box
                        messagebox("Warning", "Access Denied!\nPlease wear a Face Mask.")

            # show the video
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(1280, 720, 1)
            self.ImageUpdate.emit(Pic)

    def sendEmail(self, sender, receiver, password, attachment, content):
        newMessage = EmailMessage()
        newMessage['Subject'] = "Face Mask Detector System"
        newMessage['From'] = sender
        newMessage['To'] = receiver
        files = [attachment]
        newMessage.set_content(content)
        for file in files:
            with open(file, 'rb') as f:
                file_data = f.read()
                file_name = f.name
            newMessage.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465)  as smtp:
            smtp.login(sender, password)
            smtp.send_message(newMessage)

    def run(self):
        self.check()


# ###   PUBLIC FUNCTIONS    ###
def is_internet():
    """
    Query internet using python
    :return:
    """
    try:
        urlopen('https://www.google.com', timeout=1)
        return True
    except urllib.error.URLError as Error:
        print(Error)
        return False


def messagebox(title, text):
    root = tkinter.Tk()
    root.withdraw()
    tkinter.messagebox.showwarning(title, text)
    root.destroy()


# //////////////////////////////////////////   RUN HERE   //////////////////////////////////////////
if is_internet():
    app = QApplication(sys.argv)
    mainWindow = Login()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
    widget.setWindowTitle("Face Mask Detection System")
    widget.setFixedWidth(970)
    widget.setFixedHeight(960)
    widget.show()
    app.exec_()
else:
    messagebox("No internet", "Try:\n\n-Checking the network cables, modem, and router\n-Reconnecting to Wi-Fi")
    print("Internet disconnected")
    # sys.exit()
