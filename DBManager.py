import sqlite3, hashlib

class DatabaseManager():

    def __init__(self, primaryDB):
        self.primaryDB = primaryDB

    def connectToDB(self, db_file):
        if not db_file:     # If db_file parameter not given, use default primaryDB
            db_file = self.primaryDB
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def editDB(self, query, queryValues = None, db_file = None, script = False):

        if not db_file:     # If db_file parameter not given, use default primaryDB
            db_file = self.primaryDB
        self.connectToDB(db_file)

        try:
            if script:      # Picks execute() or executescript()
                self.cursor.executescript(query)
            else:
                self.cursor.execute(query, queryValues)
            self.conn.commit()
            self.conn.close()

        except sqlite3.Error as e:
            print(f"Database Error: {e}")
            self.conn.close()


    def fetchOneValue(self, query, params=(), db_file = None):  # ex. query = "SELECT * FROM users WHERE id = ? AND name = ?", params = (1, "Alice"))
        if not db_file:
            db_file = self.primaryDB
        self.connectToDB(db_file)
        self.cursor.execute(query, params)
        result = self.cursor.fetchone()
        self.conn.close()
        return result if result else None #return None if not found

    # Fetches data to be displayed
    def fetchAllData(self, query, db_file = None):
        self.connectToDB(db_file)
        self.cursor.execute(query)
        data = self.cursor.fetchall()
        self.conn.close()
        return data

    def hashString(self, data: str) -> str:        #Example: hashed_value = hashString("text")
        return hashlib.sha256(data.encode()).hexdigest() # SHA-256 hash, unsalted.
