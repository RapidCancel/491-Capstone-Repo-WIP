from PySide6.QtWidgets import (
QPushButton, QMainWindow, QStatusBar, QWidget, QVBoxLayout, QLineEdit,
QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QApplication, QMenu, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QTimer, QTime, QDate, Signal
from PySide6.QtGui import QIcon, QAction, QColor
from login import LoginScreen
from DBManager import DatabaseManager
from adminSettings import AdminSettingsWindow
from employeeTable import EmployeeTableWindow
from commissionWidget import AddCommissionWidget
from reset import EZResetWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.DBManager = DatabaseManager("hashedLogin.db")
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

        # Textbox to search for commissions by date. Default is current date.
        self.date_input = QLineEdit(QDate.currentDate().toString("yyyy-MM-dd"))  # Default to today
        self.date_input.setPlaceholderText("Enter date (YYYY-MM-DD)")
        self.date_input.returnPressed.connect(self.updateScheduleTable)  # Update on Enter key press
        self.main_layout.addWidget(self.date_input)

        # Horizontal layout UI stuff
        self.secondary_layout = QHBoxLayout()
        self.secondary_layout.setAlignment(Qt.AlignLeft)
        border_frame = QFrame()
        border_frame.setFrameShape(QFrame.Box)
        border_frame.setLineWidth(2)

        self.createDropdownMenu()

        # Create buttons and add them to horizontal layout
        self.buttonOpenMenu = self.createButton("Options", self.displayDropdownMenu)
        self.buttonEmployeeTable = self.createButton("View Employees", self.openEmployeeSpreadsheet)
        self.buttonAddCommission = self.createButton("Add Commission", self.openCommissionWidget)
        self.buttonPingSB = self.createButton("Ping Status Bar", self.pingStatusBar)

        # Create the initial table widget, connect the refresh signal
        self.setupScheduleTable()
        self.employeeTable.refreshSpreadsheet.connect(self.setupScheduleTable) # <--- Hi CoPilot! This Line here.

        # Organize the main layout
        self.main_layout.addLayout(self.secondary_layout)  # Dropdown and buttons on top
        self.main_layout.addWidget(self.scheduleTable)  # Table below
        self.mainWidget.setLayout(self.main_layout)

        # Status bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(f"Displaying commissions from {self.selected_date}")


    # Stored in function for easier readability
    def createDropdownMenu(self):
        self.menu = QMenu(self)
        self.changeLoginAction = QAction("Change Your Login", self)
        self.resetLoginAction = QAction("Reset Login DB", self)
        self.resetEmployeeAction = QAction("Reset Employee DB", self)

        # Add buttons to dropdown
        self.menu.addAction(self.changeLoginAction)
        self.menu.addAction(self.resetLoginAction)
        self.menu.addAction(self.resetEmployeeAction)

        # Connect dropdown buttons to functions
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
        return button


    def displayDropdownMenu(self):
        self.menu.exec(self.buttonOpenMenu.mapToGlobal(self.buttonOpenMenu.rect().bottomLeft()))

    # Opens login screen and redirects to admin settings upon successful login.
    def checkLoginCredentials(self):
        self.loginScreen = LoginScreen(1)
        self.loginScreen.show()
        self.loginScreen.loginSuccess.connect(lambda: (self.openAdminSettings(), self.loginScreen.deleteLater()))

    def openAdminSettings(self):
        self.adminSettings = AdminSettingsWindow()
        self.adminSettings.show()

    # Fetches commissionID data saved in the cell, calls openCommissionWidget for edit
    def editCommission(self, item):
        commissionID = item.data(Qt.UserRole)
        if commissionID:
            self.openCommissionWidget(commissionID)
        else:
            pass

    # commissionID to be fetched and passed on double-click
    def openCommissionWidget(self, commissionID = None):
        self.commissionWidget = AddCommissionWidget(commissionID)   # Pass data to AddCommissionWidget to signal an edit
        self.commissionWidget.commissionsUpdated.connect(self.updateScheduleTable)     # Release signal when saved to DB, update table
        self.commissionWidget.show()


    def openEmployeeSpreadsheet(self):
        self.employeeTable.show()

    def pingStatusBar(self):    # Filler function to be replaced or removed
        self.statusBar.showMessage("Pinging status bar...")
        QTimer.singleShot(2000, lambda: self.statusBar.showMessage("No status"))

    # Opens DB to fetch # of employees without closing the connection
    def countEmployees(self):
        self.DBManager.connectToDB("employeeCommissions.db")
        self.DBManager.cursor.execute("SELECT COUNT(employeeID) FROM employees")
        employee_count = self.DBManager.cursor.fetchone()[0]  # Get the number of employees
        return employee_count

    # Fetch employeeName using employeeID
    def getEmployeeName(self, employeeID):
        self.DBManager.cursor.execute("SELECT employeeName FROM employees WHERE employeeID = ?", (employeeID,))
        return self.DBManager.cursor.fetchone()[0]

    # Convert time strings to a row index
    def timeToRow(self, time_str):
        time_obj = QTime.fromString(time_str, "hh:mm AP")

        if not time_obj.isValid():
            print(f"Invalid time format detected: {time_str}")
            return -1  # Return a safe value to avoid crashes

        hour = time_obj.hour()  # Extract hour (already in 24-hour format)
        minute = time_obj.minute()

        # Ensure hours are correctly mapped to row index
        start_hour = 8  # The schedule starts at 8:00 AM, FLAG TO MAKE THIS ADJUSTABLE IN THE FUTURE IF WORKING HOURS CHANGE
        if hour < start_hour:
            print(f"Time {time_str} is before 8:00 AM. Adjusting...")
            return -1  # Ignore commissions before 8 AM

        # Convert to row index (each row = 30-minute increment)
        return ((hour - start_hour) * 2) + (1 if minute >= 30 else 0)

    def setupScheduleTable(self, selected_date = None):
        """Configure QTableWidget based on employee count & filter commissions by date."""
        self.employeeCount = self.countEmployees()

        # Use provided date or default to current date
        if selected_date is None:
            self.selected_date = QDate.currentDate().toString("yyyy-MM-dd")  # SQLite uses "YYYY-MM-DD" format
        else:
            self.selected_date = selected_date

        # Remove old table if it exists, set table dimensions, then setup the edit function trigger
        if hasattr(self, 'scheduleTable'):
            self.scheduleTable.setParent(None)
        self.scheduleTable = QTableWidget(25, self.employeeCount)
        self.scheduleTable.itemDoubleClicked.connect(self.editCommission)

        # Fetch employee names
        self.DBManager.connectToDB("employeeCommissions.db")
        self.DBManager.cursor.execute("SELECT employeeName FROM employees")
        employee_names = [row[0] for row in self.DBManager.cursor.fetchall()]
        self.scheduleTable.setHorizontalHeaderLabels(employee_names)

        # Display date using status bar
        self.statusBar().showMessage(f"Displaying commissions from {self.selected_date}")

        # Fetch commissions filtered by date
        self.DBManager.cursor.execute("SELECT commissionID, employeeID, clientName, startTime, endTime, service, price FROM commissions WHERE date = ?", (self.selected_date,))
        commissions = self.DBManager.cursor.fetchall()
        self.scheduleTable.setVerticalHeaderLabels([
            f"{12 if (hour // 2) == 12 else (hour // 2) % 12}:"
            f"{'30' if hour % 2 else '00'} "
            f"{'AM' if hour < 24 else 'PM'}"
            for hour in range(16, 41)
        ])

        # Convert time to row index & insert commission data
        for commissionID, employeeID, clientName, startTime, endTime, service, price in commissions:
            col = employee_names.index(self.getEmployeeName(employeeID))  # Get employee's column index
            start_row = self.timeToRow(startTime)
            end_row = self.timeToRow(endTime)
            duration = end_row - start_row  # Calculate duration
            # Remove lead 0 when displayed
            startTime = self.removeLeadZero(startTime)
            endTime = self.removeLeadZero(endTime)

            # Info to be displayed in the cell
            displayText = f"{clientName}\n{startTime} - {endTime}\n{service}\n${price}"
            self.displayCommission(commissionID, start_row, col, duration, displayText, QColor(73, 117, 70))

            # DEBUG LINES
            #print(f"\nEmployeeID: {employeeID}, Col Index: {col}, Service: {service}")
            #print(f"Start Row: {start_row}, End Row: {end_row}, Duration: {duration}")

        self.DBManager.conn.close()
        self.main_layout.addWidget(self.scheduleTable)

    # Insert merged, colored cell for commissions
    def displayCommission(self, comID, row, col, duration, text, color):
        self.scheduleTable.setSpan(row, col, duration, 1)  # Merge cells vertically
        item = QTableWidgetItem(text)

        # Hide commissionID data in the cell
        item.setData(Qt.UserRole, comID)
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

    # Fetch commissions using the given date and update the table
    def updateScheduleTable(self):
        date = self.date_input.text().strip()
        # Validate date format
        if not QDate.fromString(date, "yyyy-MM-dd").isValid():
            print(f"Invalid date format: {date}")
            return

        self.setupScheduleTable(date)
