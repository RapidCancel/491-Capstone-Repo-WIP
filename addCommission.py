from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QTimeEdit, QCheckBox, QPushButton, QLabel
from PySide6.QtCore import QTime, Signal
from DBManager import DatabaseManager
import sqlite3

class AddCommissionWidget(QWidget):
    commissionAdded = Signal()

    def __init__(self, commissionID = None):    # Pre-fill data for edits, if given existing commissionID
        super().__init__()
        self.setWindowTitle("Edit Commission" if commissionID else "Add Commission")

        # Declare imported class(es) and variables
        self.DBManager = DatabaseManager("employeeSchedule.db")  # Assigns default database
        self.commissionID = commissionID    # Stores commissionID for editing

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

        # Display Recommendations from FIFO queue
        self.recommendation_label = QLabel("Recommended Employee: ")
        layout.addWidget(self.recommendation_label)


        # Dropdown for selecting an employee
        self.employee_dropdown = QComboBox()
        self.employee_dropdown.addItems(employees)  # Populate dropdown with employee names
        form_layout.addRow("Employee:", self.employee_dropdown)

        # Input fields for client number and name, check if number recognized
        self.client_number_input = QLineEdit()
        self.client_number_input.textChanged.connect(self.fetchClientByNumber)  # Trigger phone # lookup on change
        form_layout.addRow("Client Number:", self.client_number_input)
        self.client_name_input = QLineEdit()
        form_layout.addRow("Client Name:", self.client_name_input)

        # Input field for price
        self.price_input = QLineEdit()
        form_layout.addRow("Price:", self.price_input)

        # Start and end time selection
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("hh:mm AP")
        self.start_time_edit.setTime(QTime(8, 0))  # Default start time

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("hh:mm AP")
        self.end_time_edit.setTime(QTime(10, 0))  # Default end time

        form_layout.addRow("Start Time:", self.start_time_edit)
        form_layout.addRow("End Time:", self.end_time_edit)

        layout.addLayout(form_layout)

        # Job role checkboxes
        self.roleCheckboxes = []
        for role in jobRoles:
            checkbox = QCheckBox(role)
            checkbox.stateChanged.connect(self.updateEmployeeRec)  # Update when checkbox changes
            layout.addWidget(checkbox)
            self.roleCheckboxes.append(checkbox)

        # Confirm button
        self.confirm_button = QPushButton("Save Changes" if self.commissionID else "Confirm")
        layout.addWidget(self.confirm_button)
        self.confirm_button.clicked.connect(self.saveCommission)
        self.setLayout(layout)

        # If editing: Load saved data first
        if self.commissionID:
            self.loadCommissionData(self.commissionID)


    def fetch_recommended_employee(self, selected_roles):
        """Find the best available employee who matches ALL selected roles and has waited longest since a non-break commission."""
        if not selected_roles:
            return "Select at least one role."

        conn = sqlite3.connect("employeeSchedule.db")
        cursor = conn.cursor()

        # Fetch employees who match ALL selected roles
        cursor.execute("""
            SELECT e.employeeID, e.employeeName,
                   COALESCE(
                       (SELECT MAX(c.date || ' ' || c.endTime)
                        FROM commissions c
                        JOIN rolesForCommissions rc ON c.commissionID = rc.commissionID
                        WHERE c.employeeID = e.employeeID AND rc.roleID != 0),  -- Exclude break commissions
                       '2000-01-01 00:00') AS lastCommissionTime
            FROM employees e
            JOIN employeeRoles er ON e.employeeID = er.employeeID
            WHERE e.employeeID IN (
                SELECT employeeID FROM employeeRoles WHERE roleID IN ({})
                GROUP BY employeeID
                HAVING COUNT(DISTINCT roleID) = ?
            )
            GROUP BY e.employeeID
            ORDER BY lastCommissionTime ASC;
        """.format(",".join("?" * len(selected_roles))), tuple(selected_roles) + (len(selected_roles),))

        recommended = cursor.fetchone()
        conn.close()

        return f"Recommended Employee: {recommended[1]}" if recommended else "No available match."


    def updateEmployeeRec(self):
        """Fetch recommended employee based on checked roles."""
        selected_roles = [
            checkbox.text() for checkbox in self.roleCheckboxes if checkbox.isChecked()
        ]

        # Convert role names to roleIDs
        conn = sqlite3.connect("employeeSchedule.db")
        cursor = conn.cursor()
        roleIDs = [
            cursor.execute("SELECT roleID FROM jobRoles WHERE roleName = ?", (role,)).fetchone()[0]
            for role in selected_roles
        ]
        conn.close()

        recommendation_text = self.fetch_recommended_employee(roleIDs)
        self.recommendation_label.setText(recommendation_text)


    def fetchClientByNumber(self):
        """Fetch client name if a known clientNumber is entered."""
        client_number = self.client_number_input.text().strip()

        # Skip empty inputs
        if not client_number:
            self.client_name_input.clear()
            return

        # Query the database
        conn = sqlite3.connect("employeeSchedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT clientName FROM clients WHERE clientNumber = ?", (client_number,))
        result = cursor.fetchone()
        conn.close()

        # Auto-fill if found, otherwise keep field empty
        if result:
            self.client_name_input.setText(result[0])
        else:
            self.client_name_input.clear()  # Allow manual entry if new client


    def saveCommission(self):
        employeeName = self.employee_dropdown.currentText()
        clientNumber = self.client_number_input.text()
        clientName = self.client_name_input.text()
        startTime = self.start_time_edit.time().toString("hh:mm AP")
        endTime = self.end_time_edit.time().toString("hh:mm AP")
        price = self.price_input.text().strip()

        # Issue with DBManager.connectToDB(), self.conn redeclared but not overwritten? Just connect manually
        conn = sqlite3.connect("employeeSchedule.db")
        saveCursor = conn.cursor()

        # Use employeeName to fetch employeeID
        saveCursor.execute("SELECT employeeID FROM employees WHERE employeeName = ?", (employeeName,))
        employeeID = saveCursor.fetchone()[0]

        # Fetch the required roles by matching values with the checkboxes
        requiredRoles = [checkbox.text() for checkbox in self.roleCheckboxes if checkbox.isChecked()]

        if self.commissionID:   # If saving edits...
            saveCursor.execute("""
                UPDATE commissions SET
                employeeID = ?, clientNumber = ?, clientName = ?, startTime = ?, endTime = ?, service = ?, price = ?
                WHERE commissionID = ?
            """, (employeeID, clientNumber, clientName, startTime, endTime, ', '.join(requiredRoles), price, self.commissionID))

            # Clear previous roles and reinsert
            saveCursor.execute("DELETE FROM rolesForCommissions WHERE commissionID = ?", (self.commissionID,))
            for role in requiredRoles:
                saveCursor.execute("INSERT INTO rolesForCommissions (commissionID, roleID) SELECT ?, roleID FROM jobRoles WHERE roleName = ?", (self.commissionID, role))

        else:   # If saving new commission...
            saveCursor.execute("""
                INSERT INTO commissions (employeeID, date, clientNumber, clientName, startTime, endTime, service, price)
                VALUES (?, DATE('now'), ?, ?, ?, ?, ?, ?)
            """, (employeeID, clientNumber, clientName, startTime, endTime, ', '.join(requiredRoles), price))

            # Assign the new commission an ID
            self.commissionID = saveCursor.lastrowid
            for role in requiredRoles:
                saveCursor.execute("INSERT INTO rolesForCommissions (commissionID, roleID) SELECT ?, roleID FROM jobRoles WHERE roleName = ?", (self.commissionID, role))

        conn.commit()
        self.commissionAdded.emit() # Emits signal for mainWindow to reupdate table

        # Debugging section
        print("saveCommission triggered!")
        self.DBManager.printDBTable("commissions")  # Prints the specified table in default DB

        conn.close()
        self.deleteLater()


    # Fetches data from commissionID
    def loadCommissionData(self, commissionID):
        conn = sqlite3.connect("employeeSchedule.db")
        cursor = conn.cursor()

        # Fetch commission details
        cursor.execute("SELECT employeeID, clientNumber, clientName, startTime, endTime, service, price FROM commissions WHERE commissionID = ?", (commissionID,))
        commission = cursor.fetchone()

        if commission:
            employeeID, clientNumber, clientName, startTime, endTime, service, price = commission

            # Fetch employeeName from employeeID, then populate fields
            cursor.execute("SELECT employeeName FROM employees WHERE employeeID = ?", (employeeID,))
            assignedEmployee = cursor.fetchone()
            self.employee_dropdown.setCurrentText(assignedEmployee[0])
            self.client_number_input.setText(clientNumber if clientNumber else "")
            self.client_name_input.setText(clientName if clientName else "")
            self.start_time_edit.setTime(QTime.fromString(startTime, "hh:mm AP"))
            self.end_time_edit.setTime(QTime.fromString(endTime, "hh:mm AP"))
            self.price_input.setText(str(price) if price is not None else "")

            # Check relevant job roles
            cursor.execute("SELECT roleID FROM rolesForCommissions WHERE commissionID = ?", (self.commissionID,))
            roleIDs = {row[0] for row in cursor.fetchall()}

            for checkbox in self.roleCheckboxes:
                role_name = checkbox.text()
                cursor.execute("SELECT roleID FROM jobRoles WHERE roleName = ?", (role_name,))
                roleID = cursor.fetchone()[0]

                if roleID in roleIDs:
                    checkbox.setChecked(True)

        conn.close()


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
