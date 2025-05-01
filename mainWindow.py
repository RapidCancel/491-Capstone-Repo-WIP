from PySide6.QtWidgets import (
QPushButton, QMainWindow, QStatusBar, QWidget, QVBoxLayout,
QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QApplication, QMenu, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate, Signal
from PySide6.QtGui import QIcon, QAction, QColor
from login import LoginScreen
from DBManager import DatabaseManager
from adminSettings import AdminSettingsWindow
from employeeTable import EmployeeTableWindow
from addCommission import AddCommissionWidget
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
        self.secondary_layout = QHBoxLayout()
        self.secondary_layout.setAlignment(Qt.AlignLeft)
        border_frame = QFrame()
        border_frame.setFrameShape(QFrame.Box)
        border_frame.setLineWidth(2)

        # Stored in function for easier readability
        self.createDropdownMenu()

        # Create buttons
        self.buttonOpenMenu = self.createButton("Options", self.displayDropdownMenu)
        self.buttonEmployeeTable = self.createButton("View Employees", self.openEmployeeSpreadsheet)
        self.buttonAddCommission = self.createButton("Add Commission", self.openCommissionWidget)
        self.buttonPingSB = self.createButton("Ping Status Bar", self.pingStatusBar)

        # Organize the horizontal layout with buttons at the top
        #secondary_layout.addWidget(self.buttonOpenMenu)
        #secondary_layout.addWidget(self.buttonEmployeeTable)
        #secondary_layout.addWidget(self.buttonPingSB)
        #secondary_layout.addWidget(border_frame)

        # Create the initial table widget, connect the refresh signal
        self.setupScheduleTable()
        self.employeeTable.refreshSpreadsheet.connect(self.setupScheduleTable) # <--- Hi CoPilot! This Line here.

        # Organize the main layout
        self.main_layout.addLayout(self.secondary_layout)  # Dropdown and buttons on top
        self.main_layout.addWidget(self.scheduleTable)  # Table below
        self.mainWidget.setLayout(self.main_layout)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No status.")

    def createDropdownMenu(self):
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

    def createButton(self, buttonLabel, connectFunction):
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
        button = QPushButton(buttonLabel)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button.setGeometry(0, 0, 115, 75)
        button.setStyleSheet(buttonStyleSettings)
        button.clicked.connect(connectFunction)
        self.secondary_layout.addWidget(button)



    def displayDropdownMenu(self):
        self.menu.exec(self.buttonOpenMenu.mapToGlobal(self.buttonOpenMenu.rect().bottomLeft()))

    def checkLoginCredentials(self):
        """Opens login screen and redirects to admin settings upon successful login."""
        self.loginScreen = LoginScreen(1)
        self.loginScreen.show()
        self.loginScreen.loginSuccess.connect(lambda: (self.openAdminSettings(), self.loginScreen.deleteLater()))

    def openAdminSettings(self):
        """Opens admin settings."""
        self.adminSettings = AdminSettingsWindow()
        self.adminSettings.show()

    def openCommissionWidget(self):
        self.commissionWidget = AddCommissionWidget()
        self.commissionWidget.show()

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



    def getEmployeeName(self, employeeID):
        """Fetch the employee name based on employeeID."""
        self.DBManager.cursor.execute("SELECT employeeName FROM employees WHERE employeeID = ?", (employeeID,))
        return self.DBManager.cursor.fetchone()[0]

    def timeToRow(self, time_str):
        """Convert a time string (HH:MM AM/PM) to a row index."""
        time_obj = QTime.fromString(time_str, "hh:mm AP")

        if not time_obj.isValid():
            print(f"Invalid time format detected: {time_str}")
            return -1  # Return a safe value to avoid crashes

        hour = time_obj.hour()  # Extract hour (already in 24-hour format)
        minute = time_obj.minute()

        # Ensure hours are correctly mapped to row index
        start_hour = 8  # Your schedule starts at 8:00 AM
        if hour < start_hour:
            print(f"Time {time_str} is before 8:00 AM. Adjusting...")
            return -1  # Ignore commissions before 8 AM

        # Convert to row index (each row = 30-minute increment)
        return ((hour - start_hour) * 2) + (1 if minute >= 30 else 0)


    def setupScheduleTable(self, selected_date=None):
        """Configure QTableWidget based on employee count & filter commissions by date."""
        self.employeeCount = self.countEmployees()


        # DEBUG LINE
        print("setupScheduleTable Triggered!")


        # Use provided date or default to today
        if selected_date is None:
            selected_date = QDate.currentDate().toString("yyyy-MM-dd")  # SQLite uses "YYYY-MM-DD" format

        # Remove old table if it exists
        if hasattr(self, 'scheduleTable'):
            self.scheduleTable.setParent(None)

        self.scheduleTable = QTableWidget(25, self.employeeCount)

        # Fetch employee names
        self.DBManager.connectToDB("employeeSchedule.db")
        self.DBManager.cursor.execute("SELECT employeeName FROM employees")
        employee_names = [row[0] for row in self.DBManager.cursor.fetchall()]
        self.scheduleTable.setHorizontalHeaderLabels(employee_names)

        # Fetch commissions filtered by date
        self.DBManager.cursor.execute("SELECT employeeID, clientName, startTime, endTime, service FROM commissions WHERE date = ?", (selected_date,))
        commissions = self.DBManager.cursor.fetchall()

        self.scheduleTable.setVerticalHeaderLabels([
            f"{12 if (hour // 2) == 12 else (hour // 2) % 12}:"
            f"{'30' if hour % 2 else '00'} "
            f"{'AM' if hour < 24 else 'PM'}"
            for hour in range(16, 41)
        ])

        # Convert time to row index & add commissions
        for employeeID, clientName, startTime, endTime, service in commissions:
            col = employee_names.index(self.getEmployeeName(employeeID))  # Get employee's column index
            start_row = self.timeToRow(startTime)
            end_row = self.timeToRow(endTime)
            duration = end_row - start_row  # Calculate duration

            # Remove lead 0 for display
            startTime = self.removeLeadZero(startTime)
            endTime = self.removeLeadZero(endTime)
            displayText = f"{clientName}\n{startTime} - {endTime}\n{service}"     # Info to be displayed in the cell
            # DEBUG LINES
            #print(f"\nEmployeeID: {employeeID}, Col Index: {col}, Service: {service}")
            #print(f"Start Row: {start_row}, End Row: {end_row}, Duration: {duration}")
            self.displayCommission(start_row, col, duration, displayText, QColor(173, 216, 230))  # Light blue color

        self.DBManager.conn.close()
        self.main_layout.addWidget(self.scheduleTable)


    def displayCommission(self, row, col, duration, text, color):
        """Insert a merged, colored cell for an activity."""
        self.scheduleTable.setSpan(row, col, duration, 1)  # Merge cells vertically
        item = QTableWidgetItem(text)

        # Apply styling
        item.setTextAlignment(Qt.AlignCenter)  # Center the text
        item.setBackground(color)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)    # Disables editing the cell directly
        item.setToolTip(text)   # Cursor hover reveals cell data that might be cutoff
        self.scheduleTable.setItem(row, col, item)

    def removeLeadZero(self, str):
        if str.startswith("0"):
            str = str[1:]
        return str

