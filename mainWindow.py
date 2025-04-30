from PySide6.QtWidgets import (
QPushButton, QMainWindow, QStatusBar, QWidget, QVBoxLayout,
QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QApplication, QMenu, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QAction
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
        #self.setStyleSheet("background-color: #1D2430;")

        # Central widget
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        print(self.centralWidget())

        # Load employeeTable
        self.employeeTable = EmployeeTableWindow()

        # Set up main layout
        self.main_layout = QVBoxLayout()
        self.mainWidget.setLayout(self.main_layout)

        # Horizontal layout UI stuff
        secondary_layout = QHBoxLayout()
        secondary_layout.setAlignment(Qt.AlignLeft)
        border_frame = QFrame()
        border_frame.setFrameShape(QFrame.Box)
        border_frame.setLineWidth(2)

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
        self.createButtons()    # Stored in function for easier readability

        # Organize the horizontal layout with buttons at the top
        secondary_layout.addWidget(self.buttonOpenMenu)
        secondary_layout.addWidget(self.buttonEmployeeTable)
        secondary_layout.addWidget(self.buttonPingSB)
        secondary_layout.addWidget(border_frame)

        # Create the initial table widget, connect the refresh signal
        self.setupScheduleTable()
        self.employeeTable.refreshSpreadsheet.connect(self.setupScheduleTable) # <--- Hi CoPilot! This Line here.

        # Organize the main layout
        self.main_layout.addLayout(secondary_layout)  # Dropdown and buttons on top
        self.main_layout.addWidget(self.scheduleTable)  # Table below
        self.mainWidget.setLayout(self.main_layout)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No status.")


    def createButtons(self):
        buttonStyleSettings = """
        QPushButton {
            border: none;
            font-size: 14px;
            background-color: transparent;
            padding: 10px;
        }
        QPushButton:hover {
            background-color: rgba(200, 200, 200, 50);  /* Light translucent hover effect */
        }
        """     # Script for button stylesheets, saves on lines

        self.buttonOpenMenu = QPushButton("Options")    # Opens the dropdown menu
        self.buttonOpenMenu.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonOpenMenu.setGeometry(0, 0, 115, 75)
        self.buttonOpenMenu.setStyleSheet(buttonStyleSettings)
        self.buttonOpenMenu.clicked.connect(self.displayDropdownMenu)

        self.buttonEmployeeTable = QPushButton("View Employees")
        self.buttonEmployeeTable.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonEmployeeTable.setGeometry(0, 0, 115, 75)
        self.buttonEmployeeTable.setStyleSheet(buttonStyleSettings)
        self.buttonEmployeeTable.clicked.connect(self.openEmployeeSpreadsheet)

        self.buttonPingSB = QPushButton("Ping Status Bar")
        self.buttonPingSB.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.buttonPingSB.setGeometry(0, 0, 115, 75)
        self.buttonPingSB.setStyleSheet(buttonStyleSettings)
        self.buttonPingSB.clicked.connect(self.pingStatusBar)


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
        self.employeeTable.show()

    def pingStatusBar(self):
        """Displays a temporary status bar message."""
        self.status_bar.showMessage("Pinging status bar...")
        QTimer.singleShot(2000, lambda: self.status_bar.showMessage("No status"))

    def countEmployees(self):   # opens DB to fetch # of employees without closing the connection.
        """Fetch the number of employees based on their primary keys."""
        self.DBManager.connectToDB("employeeSchedule.db")
        self.DBManager.cursor.execute("SELECT COUNT(employeeID) FROM employees")
        employee_count = self.DBManager.cursor.fetchone()[0]  # Get the number of employees

        #self.conn.close()
        return employee_count

    def setupScheduleTable(self):   # To-Do: displaying schedule data from DB and implementing a dynamic update if not already
        """Configure the QTableWidget based on employee count."""
        self.employeeCount = self.countEmployees()  # Connects to DB and displays a dynamic column count

        # Remove old table if it exists
        if hasattr(self, 'scheduleTable'):
            self.scheduleTable.setParent(None)  # Remove from the layout


        # First parameter is # of rows. Might connect to variable for future flexibility.
        self.scheduleTable = QTableWidget(25, self.employeeCount)

        # Connected to DB without closing in countEmployees(), no need to reconnect
        self.DBManager.cursor.execute("SELECT employeeName FROM employees")
        employee_names = [row[0] for row in self.DBManager.cursor.fetchall()]

        self.scheduleTable.setHorizontalHeaderLabels(employee_names)  # Set column and row headers
        self.scheduleTable.setVerticalHeaderLabels([
            f"{12 if (hour // 2) == 12 else (hour // 2) % 12}:"
            f"{'30' if hour % 2 else '00'} "
            f"{'AM' if hour < 24 else 'PM'}"
            for hour in range(16, 41)  # Covers 8:00 AM to 8:00 PM in 30-minute increments
        ])
        self.DBManager.conn.close()

        # Re-add the updated table to the layout at the bottom.
        self.main_layout.addWidget(self.scheduleTable)
