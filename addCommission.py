from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QTimeEdit, QCheckBox, QPushButton
from PySide6.QtCore import QTime
from DBManager import DatabaseManager
import sqlite3

class AddCommissionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Commission")

        # Declare imported class(es) here
        self.DBManager = DatabaseManager("employeeSchedule.db")  # Assigns default database

        # Declare layout
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Fetch employeeNames from DB
        self.DBManager.connectToDB()    # Connects to default DB, creates self.cursor
        self.DBManager.cursor.execute("SELECT employeeName FROM employees")
        employees = [row[0] for row in self.DBManager.cursor.fetchall()]
        # Fetch jobRoles from DB
        self.DBManager.cursor.execute("SELECT roleName FROM jobRoles")
        jobRoles = [row[0] for row in self.DBManager.cursor.fetchall()]

        # Dropdown for selecting an employee
        self.employee_dropdown = QComboBox()
        self.employee_dropdown.addItems(employees)  # Populate dropdown with employee names
        form_layout.addRow("Employee:", self.employee_dropdown)

        # Input field for client name
        self.client_name_input = QLineEdit()
        form_layout.addRow("Client Name:", self.client_name_input)

        # Start and end time selection
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime(8, 0))  # Default start time

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.end_time_edit.setTime(QTime(10, 0))  # Default end time

        form_layout.addRow("Start Time:", self.start_time_edit)
        form_layout.addRow("End Time:", self.end_time_edit)

        layout.addLayout(form_layout)

        # Job role checkboxes
        self.roleCheckboxes = []
        for role in jobRoles:
            checkbox = QCheckBox(role)
            layout.addWidget(checkbox)
            self.roleCheckboxes.append(checkbox)

        # Confirm button
        self.confirm_button = QPushButton("Confirm")
        layout.addWidget(self.confirm_button)
        self.confirm_button.clicked.connect(self.saveCommission)
        self.setLayout(layout)

    def saveCommission(self):
        employeeName = self.employee_dropdown.currentText()
        clientName = self.client_name_input.text()
        startTime = self.start_time_edit.time().toString("HH:mm")
        endTime = self.end_time_edit.time().toString("HH:mm")

        # Issue with DBManager.connectToDB(), self.conn redeclared but not overwritten? Just connect manually
        conn = sqlite3.connect("employeeSchedule.db")
        saveCursor = conn.cursor()

        # Use employeeName to fetch employeeID
        saveCursor.execute("SELECT employeeID FROM employees WHERE employeeName = ?", (employeeName,))
        employeeID = saveCursor.fetchone()[0]


        # Fetch last commissionID
        commissionID = saveCursor.lastrowid
        # Fetch the required roles by matching values with the checkboxes
        requiredRoles = [checkbox.text() for checkbox in self.roleCheckboxes if checkbox.isChecked()]
        # Declare string to append role names, for service, to be displayed for description
        serviceString = ""
        # Match role names to roleIDs and append the roleNames to serviceString
        for role in requiredRoles:
            serviceString += (f"{role}, ")
            saveCursor.execute("SELECT roleID from jobRoles WHERE roleName = ?", (role,))
            roleID = saveCursor.fetchone()[0]
            saveCursor.execute("INSERT INTO rolesForCommissions (commissionID, roleID) VALUES (?, ?)", (commissionID, roleID))

        # Remove ", " from the end of serviceString, so it looks nice
        serviceString = serviceString[:-2]


        # Finally, insert all data into commissions table
        saveCursor.execute(
            "INSERT INTO commissions (employeeID, date, clientName, startTime, endTime, service) VALUES (?, DATE('now'), ?, ?, ?, ?)",
            (employeeID, clientName, startTime, endTime, serviceString)
        )


        conn.commit()

        # Debugging section
        print("saveCommission triggered!")
        self.DBManager.printDBTable("commissions")  # Prints the specified table in default DB

        conn.close()
        self.deleteLater()

    def closeEvent(self, event):
        if self.DBManager.conn:
            self.DBManager.conn.close()
            print("Database connection closed.")

        event.accept()  # Ensures the window closes properly

# Run the application only if executed directly
if __name__ == "__main__":
    app = QApplication([])
    window = AddCommissionWidget()
    window.show()
    app.exec()
