from PySide6.QtWidgets import QPushButton, QMainWindow, QLabel, QStatusBar
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon
from login import LoginScreen
from DBManager import DatabaseManager
from adminSettings import AdminSettingsWindow
from employeeTable import EmployeeTableWindow

from reset import EZResetWidget

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.DBManager = DatabaseManager("hashedCredentials.db")

        self.resetWidget = EZResetWidget()

        self.setWindowTitle("Main Window")
        self.setGeometry(150, 100, 800, 400)

        self.setWindowIcon(QIcon("ui_elements/TimeTableLogo.ico"))

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
        self.buttonAdminReset.setGeometry(200, 240, 200, 40) #parameters for setGeometry?
        self.buttonAdminReset.clicked.connect(self.checkLoginCredentials) #call login before opening settings

        # Button to reset hashedCredentials database
        self.buttonResetDB = QPushButton("Reset user DB to original values", self)
        self.buttonResetDB.setStyleSheet("background-color: #2A3345;")
        self.buttonResetDB.setGeometry(200, 320, 200, 40) #parameters for setGeometry = x, y, width, height
        self.buttonResetDB.clicked.connect(self.resetWidget.resetDatabase)

        # Button to reset employees database
        self.buttonResetEmployee = QPushButton("Reset employee DB to original values", self)
        self.buttonResetEmployee.setStyleSheet("background-color: #2A3345;")
        self.buttonResetEmployee.setGeometry(400, 240, 200, 40) #parameters for setGeometry = x, y, width, height
        self.buttonResetEmployee.clicked.connect(self.resetWidget.resetEmployeesDB)

        # Button to open employee spreadsheet
        self.buttonViewEmployees = QPushButton("Open Employee Spreadsheet", self)
        self.buttonViewEmployees.setStyleSheet("background-color: #2A3345;")
        self.buttonViewEmployees.setGeometry(400, 200, 200, 40) #parameters for setGeometry = x, y, width, height
        self.buttonViewEmployees.clicked.connect(self.openEmployeeSpreadsheet)


    def checkLoginCredentials(self):
        self.loginScreen = LoginScreen(1)
        self.loginScreen.show()
        self.loginScreen.loginSuccess.connect(lambda: (self.openAdminSettings(), self.loginScreen.close())) #upon login success signal, call adminSettings

    def openAdminSettings(self):
        self.adminSettings = AdminSettingsWindow()
        self.adminSettings.show()

    def openEmployeeSpreadsheet(self):
        self.employeeTable = EmployeeTableWindow()
        self.employeeTable.show()

    def pingStatusBar(self):
        self.status_bar.showMessage("Pinging status bar")
        QTimer.singleShot(2000, lambda: self.status_bar.showMessage("I've been pinged"))
