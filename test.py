from PySide6.QtWidgets import (
QPushButton, QMainWindow, QStatusBar, QMenuBar, QWidget, QVBoxLayout,
QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QApplication, QMenu
)
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
        mainWidget = QWidget(self)
        self.setCentralWidget(mainWidget)

        # Set up main layout and horizontal layout
        main_layout = QVBoxLayout()
        secondary_layout = QHBoxLayout()

        # Create dropdown menu
        self.menu = QMenu(self)
        self.changeLoginAction = QAction("Change Your Login", self)
        self.resetLoginAction = QAction("Reset Login DB", self)
        self.resetEmployeeAction = QAction("Reset Employee DB", self)

        self.menu.addAction(self.changeLoginAction)
        self.menu.addAction(self.resetLoginAction)
        self.menu.addAction(self.resetEmployeeAction)

        # Connect dropdown options to functions
        self.changeLoginAction.triggered.connect(self.checkLoginCredentials)
        self.resetLoginAction.triggered.connect(self.resetWidget.resetDatabase)
        self.resetEmployeeAction.triggered.connect(self.resetWidget.resetEmployeesDB)

        # Create buttons
        self.buttonOpenMenu = QPushButton("Options")    # Opens the dropdown menu
        self.buttonOpenMenu.setStyleSheet("background-color: #2A3345;")
        self.buttonOpenMenu.clicked.connect(self.displayDropdownMenu) #Might have to put this in function

        self.buttonEmployeeTable = QPushButton("View Employees")
        self.buttonEmployeeTable.setStyleSheet("background-color: #2A3345;")
        self.buttonEmployeeTable.clicked.connect(self.openEmployeeSpreadsheet)

        self.buttonPingSB = QPushButton("Ping Status Bar")
        self.buttonPingSB.setStyleSheet("background-color: #2A3345;")
        self.buttonPingSB.clicked.connect(self.pingStatusBar)

        # Setup horizontal layout for buttons at the top
        secondary_layout.addWidget(self.buttonOpenMenu)
        secondary_layout.addWidget(self.buttonEmployeeTable)
        secondary_layout.addWidget(self.buttonPingSB)

        # Create the table widget
        self.table = QTableWidget(10, 4)  # 10 rows (hours) and 4 columns (people)
        self.table.setHorizontalHeaderLabels(["Alice", "Bob", "Charlie", "Dave"])
        self.table.setVerticalHeaderLabels([f"{hour}:00" for hour in range(8, 18)])

        # Setup the main layout
        main_layout.addLayout(secondary_layout)  # Dropdown and buttons on top
        main_layout.addWidget(self.table)  # Table below
        mainWidget.setLayout(main_layout)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No status message.")


    def displayDropdownMenu(self):
        self.menu.exec(self.buttonOpenMenu.mapToGlobal(self.buttonOpenMenu.rect().bottomLeft()))

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
