from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from DBManager import DatabaseManager
import sqlite3
# When removing, remove from app.py

class EZResetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(1050, 50, 200, 200)
        self.DBManager = DatabaseManager("hashedCredentials.db")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EZ Reset")

        layout = QVBoxLayout()

        button = QPushButton("Click Me to Reset Login")
        button.clicked.connect(self.resetDatabase)
        layout.addWidget(button)

        button2 = QPushButton("Click Me to Reset Employees")
        button2.clicked.connect(self.resetEmployeesDB)
        layout.addWidget(button2)

        button3 = QPushButton("Print LoginDB")
        button3.clicked.connect(lambda: self.printDB("hashedCredentials.db", "users"))
        layout.addWidget(button3)

        button4 = QPushButton("Print EmployeesDB")
        button4.clicked.connect(lambda: self.printDB("employees.db", "employees"))
        layout.addWidget(button4)

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

        CREATE TABLE employees (
            employeeID INTEGER PRIMARY KEY,
            employeeName TEXT NOT NULL,
            employeeAddress TEXT NOT NULL,
            employeePhoneNum TEXT NOT NULL,
            employeeEmail TEXT,
            employeeNotes TEXT
        );

        INSERT INTO employees (employeeID, employeeName, employeeAddress, employeePhoneNum, employeeEmail, employeeNotes)
        VALUES (0, 'Andrew', '5111 N Dyman Ave', '6265593457', 'andrewh872@gmail.com', 'Notes');
        """


        self.DBManager.editDB(resetScript, db_file = "employees.db", script = True)
        print("Reset employee database triggered!")

    def printDB(self, db_file, table_name):
        self.DBManager.connectToDB(db_file)

        self.DBManager.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.DBManager.cursor.fetchall()

        for row in rows:
            print(row)  # Simple row-by-row printing

        self.DBManager.conn.close()
