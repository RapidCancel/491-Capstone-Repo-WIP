from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout
from PySide6.QtGui import QShortcut, QIcon
from DBManager import DatabaseManager

class LoginScreen(QWidget):
    loginSuccess = Signal()

    def __init__(self, caseCode):
        super().__init__()

        caseDict = {0: self.case0Login, 1: self.case1Authenticate}  # result = caseDict.get(caseCode)
        self.caseParameters = caseDict.get(caseCode)    # returns list of case parameters

        self.setWindowTitle(self.caseParameters()[0])   # WindowName from case#
        self.setWindowIcon(QIcon("ui_elements/TimeTableLogo.ico"))

        self.DBManager = DatabaseManager(self.caseParameters()[1])  # FileName from case#
        self.setGeometry(100, 100, 300, 150)
        self.setStyleSheet("background-color: #2A3345;")

        # Layout and widgets
        layout = QVBoxLayout(self)

        #self.username_label = QLabel("TimeTablez User Login:")
        #layout.addWidget(self.usernam`e_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username...")
        layout.addWidget(self.username_input)
        self.username_input.setStyleSheet("background-color: #1D2430;")

        #self.password_label = QLabel("Password:")
        #layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password...")
        self.password_input.setEchoMode(QLineEdit.Password)  # Hides password input
        layout.addWidget(self.password_input)
        self.password_input.setStyleSheet("background-color: #1D2430;")

        self.loginButton = QPushButton("Login")
        layout.addWidget(self.loginButton)
        self.loginButton.setStyleSheet("background-color: #49CF5A;")
        self.loginButton.clicked.connect(lambda: self.loginCheck()) # call loginCheck

        self.loginShortcut = QShortcut(Qt.Key_Return, self)      # Return key shortcut for login
        self.loginShortcut.activated.connect(self.loginButton.clicked)


    #   Switch case functions for different login needs

    def case0Login(self):
        parameters = ["Login", "hashedLogin.db"] # WindowName, FileName, Can Add other stuff later
        return parameters

    def case1Authenticate(self):
        parameters = ["Authenticate Credentials", "hashedLogin.db"]
        return parameters

    def loginCheck(self):       # Retrieve parameters from DB file
        usernameInput = self.username_input.text()
        passwordHash = self.DBManager.fetchOneValue("SELECT hashedPassword FROM users WHERE username = ?", (usernameInput,))
        passwordHash = passwordHash[0] if passwordHash else None # Extract/reformat the data from tuple into a string
        passwordInputHashed = self.DBManager.hashString(self.password_input.text())
        if (passwordInputHashed == passwordHash):
            self.loginSuccess.emit()
        else:
            self.loginButton.setText("Invalid Credentials, Please Try Again.")
            self.loginButton.setStyleSheet("background-color: #F26A6D;")
            self.password_input.clear()
            QTimer.singleShot(1250, lambda: self.loginButton.setText("Login")) #Timer on 2 seconds
            QTimer.singleShot(1250, lambda: self.loginButton.setStyleSheet("background-color: #49CF5A;"))
