#==========STABLE VERSION OF employeeTableWindow=================

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from DBManager import DatabaseManager


class EmployeeTableWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Data Spreadsheet")
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.DBManager = DatabaseManager("employees.db")

        self.displayData()

        # Connect cell change signal to update function
        self.table.cellChanged.connect(lambda row, col: self.updateEmployeeDB("""
        UPDATE employees SET employeeName=?, employeeAddress=?, employeePhoneNum=?, \
        employeeEmail=?, employeeNotes=? WHERE employeeID=?
        """, row, col))

    def displayData(self):
        data = self.DBManager.fetchAllData("SELECT * from employees")
        self.table.setRowCount(len(data))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Address", "Phone #", "Email", "Notes"])

        for row_idx, row in enumerate(data):
            if len(row) < 6:
                row += ("",) * (6 - len(row))    # Prevent unpacking errors by filling in missing tuples with empty strings

            ID, name, address, phone, email, notes = row
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(address))
            self.table.setItem(row_idx, 2, QTableWidgetItem(phone))
            self.table.setItem(row_idx, 3, QTableWidgetItem(email))
            self.table.setItem(row_idx, 4, QTableWidgetItem(notes))


    def updateEmployeeDB(self, query, row, column):   # column is NOT used. Potentially remove this.
        self.employeeName = self.table.item(row, 0).text()
        self.employeeAddress = self.table.item(row, 1).text()
        self.employeePhoneNum = self.table.item(row, 2).text()
        self.employeeEmail = self.table.item(row, 3).text()
        self.employeeNotes = self.table.item(row, 4).text()
        self.employeeTuple = [self.employeeName, self.employeeAddress, self.employeePhoneNum, self.employeeEmail, self.employeeNotes]

        self.DBManager.editDB(query, queryValues = (self.employeeName, self.employeeAddress, self.employeePhoneNum, self.employeeEmail, self.employeeNotes, row))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmployeeTableWindow()
    window.show()
    sys.exit(app.exec())
