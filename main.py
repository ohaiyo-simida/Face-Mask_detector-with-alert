import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.uic import loadUi
import pyrebase
import re

firebaseConfig = {'apiKey': "AIzaSyBM03d2RJ9rEpATRv25LIk-c6bkrtUsQfg",
                  'authDomain': "face-mask-detection-2021.firebaseapp.com",
                  'databaseURL': "https://face-mask-detection-2021.firebaseio.com/",
                  'projectId': "face-mask-detection-2021",
                  'storageBucket': "face-mask-detection-2021.appspot.com",
                  'messagingSenderId': "384900987758",
                  'appId': "1:384900987758:web:866dc09bc7bbfc2ea09f7f",
                  'measurementId': "G-SRHKT9DV2E"}

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()


class Login(QDialog):
    def __init__(self):
        super(Login, self).__init__()
        loadUi("ui/login.ui", self)
        # self.email.setPlaceholderText("Email...")
        # self.password.setPlaceholderText("Password...")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)

        self.loginButton.clicked.connect(self.loginfunction)
        self.createAccButton.clicked.connect(self.gotocreate)

        self.errorMessage.setVisible(False)

    def loginfunction(self):
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
                    auth.sign_in_with_email_and_password(email, password)
                    # TODO: After login
                    print("Successfully logged in with email: ", email, "and Password: ", password)
                except:
                    self.errorMessage.setText("Incorrect email or password.")
                    self.errorMessage.setVisible(True)

    def gotocreate(self):
        createacc = CreateAcc()
        widget.addWidget(createacc)
        widget.setCurrentIndex(widget.currentIndex() + 1)


# //////////// CREATE ACCOUNT ///////////////////////
class CreateAcc(QDialog):
    def __init__(self):
        super(CreateAcc, self).__init__()
        loadUi("ui/register.ui", self)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirmPassword.setEchoMode(QtWidgets.QLineEdit.Password)

        self.registerButton.clicked.connect(self.createaccfunction)
        self.loginhereButton.clicked.connect(self.gotologin)

        self.errorMessage.setVisible(False)

    def createaccfunction(self):
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
                        self.errorMessage.setText("Password min length is 8.")
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


app = QApplication(sys.argv)
mainWindow = Login()
widget = QtWidgets.QStackedWidget()
widget.addWidget(mainWindow)
widget.setWindowTitle("Face Mask Detector")
widget.setFixedWidth(970)
widget.setFixedHeight(960)
widget.show()
app.exec_()
