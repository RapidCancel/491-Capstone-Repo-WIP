import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QInputDialog
from DBManager import DatabaseManager
from PySide6.QtCore import Signal

class EmployeeTableWindow(QWidget):
    refreshSpreadsheet = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Data Spreadsheet")
        self.setGeometry(700, 50, 540, 300)
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Add "New Employee" Button
        self.newEmployeeButton = QPushButton("Add New Employee")
        self.newEmployeeButton.clicked.connect(self.confirmNewEmployee)
        self.layout.addWidget(self.newEmployeeButton)

        self.setLayout(self.layout)

        self.DBManager = DatabaseManager("employeeSchedule.db")

        self.displayData()

        # Connect cell change signal to update function
        self.table.cellChanged.connect(lambda row, col: self.updateEmployeeDB(row, col))

    def displayData(self):
        data = self.DBManager.fetchAllData("SELECT * FROM employees")
        self.table.setRowCount(len(data))  # Do not pre-add a new row
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Address", "Phone #", "Email", "Job Roles", "Notes"])

        for row_idx, row in enumerate(data):
            if len(row) < 7:
                row += ("",) * (7 - len(row))  # Prevent unpacking errors by filling in missing tuples with empty strings

            ID, name, address, phone, email, roles, notes = row
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(address))
            self.table.setItem(row_idx, 2, QTableWidgetItem(phone))
            self.table.setItem(row_idx, 3, QTableWidgetItem(email))
            self.table.setItem(row_idx, 4, QTableWidgetItem(roles))
            self.table.setItem(row_idx, 5, QTableWidgetItem(notes))


    def confirmNewEmployee(self):
        """ Opens confirmation pop-up before adding a new employee """
        reply = QMessageBox.question(self, "Confirm Action", "Do you want to add a new employee?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.addNewEmployee()

    def addNewEmployee(self):
        """ Prompts for name input, then adds new row with the entered name and empty fields """
        name, ok = QInputDialog.getText(self, "Employee Name", "Enter the name of the new employee:")
        if ok and name:  # Check if name input was successful
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)  # Add new row at the end
            self.table.setItem(row_count, 0, QTableWidgetItem(name))  # Set name in first column, parameters = (row, col, item)

            self.updateEmployeeDB(row_count, 0, addEmployee=True)



    def updateEmployeeDB(self, row, column, addEmployee = False):
        """ Updates existing employee or inserts new employee """
        employee_name_item = self.table.item(row, 0)
        employee_name = employee_name_item.text() if employee_name_item else None

        # Stores table data to be passed to queryValues
        self.employeeAddress = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
        self.employeePhoneNum = self.table.item(row, 2).text() if self.table.item(row, 2) else ""
        self.employeeEmail = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
        self.employeeRoles = self.table.item(row, 4).text() if self.table.item(row, 4) else ""
        self.employeeNotes = self.table.item(row, 5).text() if self.table.item(row, 5) else ""


        if addEmployee == True:  # Insert employee when new name is entered
            query = """INSERT INTO employees (employeeName, employeeAddress, employeePhoneNum, employeeEmail, employeeRoles, employeeNotes) VALUES (?, ?, ?, ?, ?, ?)"""
            queryValues = (employee_name, self.employeeAddress, self.employeePhoneNum, self.employeeEmail, self.employeeRoles, self.employeeNotes)
            self.DBManager.editDB(query, queryValues)

            self.refreshSpreadsheet.emit()  # Signal to update the schedule view with a new column.
            print("addEmployee query triggered!")

        else:  # If updating an existing employee
            query = """UPDATE employees SET employeeAddress=?, employeePhoneNum=?, employeeEmail=?, employeeRoles=?, employeeNotes=? WHERE employeeName=?"""
            queryValues = (self.employeeAddress, self.employeePhoneNum, self.employeeEmail, self.employeeRoles, self.employeeNotes, employee_name)
            self.DBManager.editDB(query, queryValues)
            print("Update query triggered!")

if __name__ == "__main__":
    app = QApplication
