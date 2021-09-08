import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
import tkinter, tkinter.messagebox
import winsound

import smtplib
import imghdr
from email.message import EmailMessage

from PyQt5.uic.properties import QtGui


class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()

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
        self.Worker = Worker(0)
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
        self.Worker = Worker(i)
        self.Worker.start()
        self.Worker.ImageUpdate.connect(self.ImageUpdateSlot)

    def ImageUpdateSlot(self, Image):
        self.cameraLabel.setPixmap(QPixmap.fromImage(Image))

    # Quit
    def closeEvent(self, event):
        msgBox = QMessageBox(
            QMessageBox.Question,
            "Window Close",
            "Are you sure you want to exit the application?",
            buttons=QMessageBox.Yes | QMessageBox.No
        )
        msgBox.setDefaultButton(QMessageBox.No)
        # msgBox.setStyleSheet("QLabel{ color: white}")
        msgBox.exec_()
        reply = msgBox.standardButton(msgBox.clickedButton())
        if reply == QMessageBox.Yes:
            sys.exit()


class Worker(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def __init__(self, index):
        QThread.__init__(self)
        self.index = index

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
        maskNet = load_model("mask_detector.model")

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

                if withoutMask > 0.995 or mask > 0.5:
                    # determine the class label and color we'll use to draw the bounding box and text
                    label = "Mask" if mask > withoutMask else "No Mask"
                    color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

                    # include the probability in the label
                    label_text = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                    # display the label and bounding box rectangle on the output frame
                    cv2.putText(frame, label_text, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

                    if label == "No Mask":
                        # capture the unmask ppl
                        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
                        img_name = "violators_img/Unmasked_ppl_{}.jpg".format(timestamp)
                        cv2.imwrite(img_name, frame)
                        print("{} written!".format(img_name))

                        # Send email here
                        self.sendEmail("facemaskdetector2021@gmail.com", "hongkailo2000@gmail.com", "Facemask123", img_name)
                        print("Email sent!")

                        # Alert message box
                        self.messagebox("Warning", "Access Denied!\nPlease wear a Face Mask.")

            # show the video
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ConvertToQtFormat = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            Pic = ConvertToQtFormat.scaled(1280, 720, 1)
            self.ImageUpdate.emit(Pic)

    def messagebox(self, title, text):
        root = tkinter.Tk()
        root.withdraw()
        tkinter.messagebox.showwarning(title, text)
        root.destroy()

    def sendEmail(self, sender, receiver, password, attachment):
        Sender_Email = sender
        Reciever_Email = receiver
        Password = password
        newMessage = EmailMessage()
        newMessage['Subject'] = "Face Mask Detector System"
        newMessage['From'] = Sender_Email
        newMessage['To'] = Reciever_Email
        newMessage.set_content('Person has been detected without face mask.')
        files = [attachment]
        for file in files:
            with open(file, 'rb') as f:
                file_data = f.read()
                file_name = f.name
            newMessage.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465)  as smtp:
            smtp.login(Sender_Email, Password)
            smtp.send_message(newMessage)

    def run(self):
        self.check()


app = QApplication(sys.argv)
mainWindow = Ui_OutputDialog()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.setWindowTitle("Face Mask Detector")
widget.setFixedWidth(970)
widget.setFixedHeight(960)
widget.show()
app.exec_()
