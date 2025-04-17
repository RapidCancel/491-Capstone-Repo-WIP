from PySide6.QtCore import Signal
import sqlite3, hashlib

class DatabaseManager():

    def __init__(self, db_path):
        self.db_path = db_path

    def connectToDB(self, db_file):
        if not db_file:     # If db_file parameter not given, use default db_path
            db_file = self.db_path
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def editDB(self, query, queryValues = None, db_file = None, script = False): #GOATED FUNCTION HELL TF YA
        if not db_file:     # If db_file parameter not given, use default db_path
            db_file = self.db_path
        self.connectToDB(db_file)
        if script == False:     # Picks execute() or executescript()
            self.cursor.execute(query, queryValues)
        else:
            self.cursor.executescript(query)
        self.conn.commit()
        self.conn.close()

    def fetchValue(self, query, params=()):
        self.connectToDB(self.db_path)
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        self.conn.close()
        return result if result else None #return None if not found

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

        self.editDB(resetScript, script = True)
        print("Reset database triggered!")


    def hashString(self, data: str) -> str:        #Example: hashed_value = hashString("text")
        return hashlib.sha256(data.encode()).hexdigest() # SHA-256 hash, unsalted.



    def load_data(self):
        connection = sqlite3.connect("example.db")  # Replace with your .db file path
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users")  # Replace with your table name
        data = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        # Set table dimensions
        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # Populate table with data
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                #self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
                pass

        connection.close()
