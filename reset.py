from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from DBManager import DatabaseManager
import sqlite3
# When removing, remove from app.py

class EZResetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(1050, 50, 200, 200)
        self.DBManager = DatabaseManager("hashedLogin.db")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EZ Reset")

        layout = QVBoxLayout()

        button = QPushButton("Reset Login")
        button.clicked.connect(self.resetDatabase)
        layout.addWidget(button)

        button2 = QPushButton("Reset EmployeeCommissionDB")
        button2.clicked.connect(self.resetEmployeesDB)
        layout.addWidget(button2)

        button3 = QPushButton("Print LoginDB")
        button3.clicked.connect(lambda: self.DBManager.printDBTable("users"))
        layout.addWidget(button3)

        button4 = QPushButton("Print Employees")
        button4.clicked.connect(lambda: self.DBManager.printDBTable("employees", db_file = "employeeCommissions.db"))
        layout.addWidget(button4)

        button5 = QPushButton("Print Job Roles")
        button5.clicked.connect(lambda: self.DBManager.printDBTable("jobRoles", db_file = "employeeCommissions.db"))
        layout.addWidget(button5)

        button6 = QPushButton("Print Commissions")
        button6.clicked.connect(lambda: self.DBManager.printDBTable("commissions", db_file = "employeeCommissions.db"))
        layout.addWidget(button6)

        self.setLayout(layout)



    def resetDatabase(self):
        # SQL script to reset the table, input sample login
        resetScript = """
        DROP TABLE IF EXISTS users;

        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            hashedPassword TEXT NOT NULL
        );

        INSERT INTO users (id, username, hashedPassword)
        VALUES (0, 'admin', 'd74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1');
        """ #username: admin, hashedPassword: SHA-256 unsalted hash of 'pass' == 'd74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1'

        self.DBManager.editDB(resetScript, script = True)
        print("Reset database triggered!")

    def resetEmployeesDB(self):
        # SQL script to reset the table, input sample login
        resetScript = """
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS clients;
        DROP TABLE IF EXISTS jobRoles;
        DROP TABLE IF EXISTS employeeRoles;
        DROP TABLE IF EXISTS commissions;
        DROP TABLE IF EXISTS rolesForCommissions;

        CREATE TABLE employees (
            employeeID INTEGER PRIMARY KEY AUTOINCREMENT,
            employeeName TEXT NOT NULL,
            employeeAddress TEXT,
            employeePhoneNum TEXT,
            employeeEmail TEXT,
            employeeRoles TEXT,
            employeeNotes TEXT
        );

        CREATE TABLE clients(
            clientNumber TEXT PRIMARY KEY NOT NULL,
            clientName TEXT NOT NULL
        );

        CREATE TABLE jobRoles (
            roleID INTEGER PRIMARY KEY AUTOINCREMENT,
            roleName TEXT UNIQUE NOT NULL
        );

        CREATE TABLE employeeRoles (
            employeeID INTEGER,
            roleID INTEGER,
            PRIMARY KEY (employeeID, roleID),
            FOREIGN KEY (employeeID) REFERENCES employees(employeeID),
            FOREIGN KEY (roleID) REFERENCES jobRoles(roleID)
        );

        CREATE TABLE commissions (
            commissionID INTEGER PRIMARY KEY AUTOINCREMENT,
            employeeID INTEGER,
            date DATE NOT NULL,
            clientNumber TEXT,
            clientName TEXT,
            startTime TIME NOT NULL,
            endTime TIME NOT NULL,
            service TEXT,
            price NUMERIC(6,2),
            FOREIGN KEY (employeeID) REFERENCES employees(employeeID),
            FOREIGN KEY (clientNumber) REFERENCES clients(clientNumber)
        );

        CREATE TABLE rolesForCommissions (
            commissionID INTEGER,
            roleID INTEGER,
            PRIMARY KEY (commissionID, roleID),
            FOREIGN KEY (commissionID) REFERENCES commissions(commissionID),
            FOREIGN KEY (roleID) REFERENCES jobRoles(roleID)
        );


        INSERT INTO employees (employeeID, employeeName, employeeAddress, employeePhoneNum, employeeEmail, employeeRoles, employeeNotes)
        VALUES
            (1, 'Alice', '1234 N Address Ave', '6261234567', 'alice1@gmail.com', 'Manicure Pedicure Acrylic Gelx', 'Misc. Notes'),
            (2, 'Bob', '4321 S Address Ave', '6267654321', 'bob2@yahoo.com', 'Manicure Acrylic Waxing', '');

        INSERT INTO clients (clientNumber, clientName)
        VALUES
            ('0000000000', 'Cindy'),
            ('1111111111', 'Danielle'),
            ('2222222222','Evelynn');


        INSERT INTO jobRoles(roleID, roleName)
        VALUES (0, 'Break');     -- "Break" roleID == 0
        INSERT INTO jobRoles (roleName)
        VALUES ('Manicure'), ('Pedicure'), ('Acrylic'), ('GelX'), ('Waxing');

        INSERT INTO employeeRoles (employeeID, roleID)
        VALUES (1,0), (1, 1), (1, 2), (1, 3), (1, 4), (2, 0), (2, 1), (2, 3), (2, 5);   -- Alice can take break, manicure, pedicure, acrylic, gelx

        INSERT INTO commissions (employeeID, date, clientNumber, clientName, startTime, endTime, service, price)
        VALUES
            (1, '2025-05-01', '0000000000', 'Cindy', '08:00 AM', '10:00 AM', 'Manicure', 50.00),
            (2, '2025-05-01', '1111111111', 'Danielle', '09:00 AM', '10:00 AM', 'Pedicure', 75.00),
            (1, '2025-05-01', '2222222222', 'Evelynn', '11:00 AM', '01:30 PM', 'Manicure, GelX', 65.00),
            (2, '2025-05-01', '', 'Lunch', '11:00 AM', '01:30 PM', 'Break', NULL);

        INSERT INTO rolesForCommissions (commissionID, roleID)
        VALUES (1, 1), (2, 2), (3, 1), (3, 4), (4, 0);  -- manicure, pedicure, then manicure and gelx, break

        """


        self.DBManager.editDB(resetScript, db_file = "employeeCommissions.db", script = True)
        print("Reset employeeCommission database triggered!")

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = EZResetWidget()
    window.show()
    sys.exit(app.exec())


