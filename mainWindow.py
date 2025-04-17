from PySide6.QtWidgets import QPushButton, QMainWindow, QLabel, QStatusBar
from PySide6.QtCore import Qt, QTimer, Signal
from login import LoginScreen
from DBManager import DatabaseManager
from adminSettings import AdminSettingsWindow

class MainWindow(QMainWindow):
    credentialsVerified = Signal()
    callAdminSettings = Signal()

    def __init__(self):
        super().__init__()

        self.DBManager = DatabaseManager("hashedCredentials.db")

        self.setWindowTitle("Main Window")
        self.setGeometry(150, 100, 800, 400)

        self.setStyleSheet("background-color: #1D2430;")

        # Central widget
        label = QLabel("Welcome to QMainWindow!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No status message.")

        # Button to activate status bar message
        self.buttonPingSB = QPushButton("Ping status bar", self)
        self.buttonPingSB.setStyleSheet("background-color: #2A3345;")
        self.buttonPingSB.setGeometry(200, 160, 200, 40) #parameters for setGeometry = x, y, width, height
        self.buttonPingSB.clicked.connect(self.pingStatusBar)

        # Button to change admin username and password
        self.buttonAdminReset = QPushButton("Change login credentials", self)
        self.buttonAdminReset.setStyleSheet("background-color: #2A3345;")
        self.buttonAdminReset.setGeometry(200, 320, 200, 40) #parameters for setGeometry?
        self.buttonAdminReset.clicked.connect(self.checkLoginCredentials) #call login before opening settings

        # Button to reset database
        self.buttonDefaultDB = QPushButton("Reset DB to original values", self)
        self.buttonDefaultDB.setStyleSheet("background-color: #2A3345;")
        self.buttonDefaultDB.setGeometry(200, 240, 200, 40) #parameters for setGeometry = x, y, width, height
        self.buttonDefaultDB.clicked.connect(self.DBManager.resetDatabase)


    def checkLoginCredentials(self):
        self.loginScreen = LoginScreen(1)
        self.loginScreen.show()
        print("checkLoginCredentials() triggered!")
        self.loginScreen.loginSuccess.connect(lambda: (self.openAdminSettings(), self.loginScreen.close())) #upon login success signal, call adminSettings

    def openAdminSettings(self):
        print("openAdminSettings() triggered!")
        self.adminSettings = AdminSettingsWindow()
        self.adminSettings.show()

    def pingStatusBar(self):
        self.status_bar.showMessage("Pinging status bar")
        QTimer.singleShot(2000, lambda: self.status_bar.showMessage("I've been pinged"))
