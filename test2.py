from PySide6.QtWidgets import QPushButton, QMainWindow, QLabel, QStatusBar, QMenuBar, QMenu, QToolBar
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QAction
from login import LoginScreen
from DBManager import DatabaseManager
from adminSettings import AdminSettingsWindow
from employeeTable import employeeTableWindow
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

        # Initialize UI elements
        self.init_menu()
        self.init_toolbar()

    def init_menu(self):
        """Creates dropdown menu with admin reset and DB reset options."""
        menu_bar = self.menuBar()

        # Create dropdown menu
        dropdown_menu = QMenu("Options", self)
        menu_bar.addMenu(dropdown_menu)

        # Admin reset
        admin_reset_action = QAction("Change Login Credentials", self)
        admin_reset_action.triggered.connect(self.checkLoginCredentials)
        dropdown_menu.addAction(admin_reset_action)

        # Reset user database
        reset_db_action = QAction("Reset User DB", self)
        reset_db_action.triggered.connect(self.resetWidget.resetDatabase)
        dropdown_menu.addAction(reset_db_action)

        # Reset employee database
        reset_employee_action = QAction("Reset Employee DB", self)
        reset_employee_action.triggered.connect(self.resetWidget.resetEmployeesDB)
        dropdown_menu.addAction(reset_employee_action)

    def init_toolbar(self):
        """Creates toolbar with remaining buttons adjacent to the dropdown menu."""
        toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # Status bar ping button
        self.buttonPingSB = QPushButton("Ping Status Bar")
        self.buttonPingSB.setStyleSheet("background-color: #2A3345;")
        self.buttonPingSB.clicked.connect(self.pingStatusBar)
        toolbar.addWidget(self.buttonPingSB)

        # Open Employee Spreadsheet
        self.buttonViewEmployees = QPushButton("Open Employee Spreadsheet")
        self.buttonViewEmployees.setStyleSheet("background-color: #2A3345;")
        self.buttonViewEmployees.clicked.connect(self.openEmployeeSpreadsheet)
        toolbar.addWidget(self.buttonViewEmployees)

    def checkLoginCredentials(self):
        """Opens login screen and redirects to admin settings upon successful login."""
        self.loginScreen = LoginScreen(1)
        self.loginScreen.show()
        self.loginScreen.loginSuccess.connect(lambda: (self.openAdminSettings(), self.loginScreen.close()))

    def openAdminSettings(self):
        """Opens admin settings."""
        self.adminSettings = AdminSettingsWindow()
        self.adminSettings.show()

    def openEmployeeSpreadsheet(self):
        """Opens employee spreadsheet."""
        self.employeeTable = employeeTableWindow()
        self.employeeTable.show()

    def pingStatusBar(self):
        """Displays a temporary status bar message."""
        self.status_bar.showMessage("Pinging status bar")
        QTimer.singleShot(2000, lambda: self.status_bar.showMessage("I've been pinged"))


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
