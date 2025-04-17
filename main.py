from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QMainWindow, QStatusBar
from PySide6.QtCore import Qt, QTimer, Signal
import sys, sqlite3

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 400)

        self.setStyleSheet("background-color: #1D2430;")

        # Central widget
        label = QLabel("Welcome to QMainWindow!")
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

        # Status bar
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("No status message.")

        # Button to open the table window
        self.buttonAccessDB = QPushButton("Access Database", self)
        self.buttonAccessDB.setStyleSheet("background-color: #2A3345;")
        self.buttonAccessDB.setGeometry(100, 80, 200, 40)
        self.buttonAccessDB.clicked.connect(self.show_table_window)

        # Button to activate status bar message
        self.buttonPingSB = QPushButton("Ping status bar", self)
        self.buttonPingSB.setStyleSheet("background-color: #2A3345;")
        self.buttonPingSB.setGeometry(200, 160, 200, 40) #parameters for setGeometry?
        self.buttonPingSB.clicked.connect(self.pingStatusBar)


    def show_table_window(self):
        self.table_window = TableWindow()
        self.table_window.show()

    def pingStatusBar(self):
        self.status_bar.showMessage("Pinging status bar")
        QTimer.singleShot(2000, lambda: self.status_bar.showMessage("I've been pinged"))




class TableWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Table Window")
        self.setGeometry(150, 150, 600, 400)
        self.setStyleSheet("background-color: #2A3345;")

        # Set up layout and table widget
        layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        layout.addWidget(self.table)
        self.table.setStyleSheet("background-color: #1D2430;")

        # Load data from database
        self.load_data()


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
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        connection.close()



class LoginScreen(QWidget):
    loginSuccess = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)
        self.setStyleSheet("background-color: #2A3345;")

        # Layout and widgets
        layout = QVBoxLayout(self)

        #self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username...")
        #layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        self.username_input.setStyleSheet("background-color: #1D2430;")

        #self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password...")
        self.password_input.setEchoMode(QLineEdit.Password)  # Hides password input
        #layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        self.password_input.setStyleSheet("background-color: #1D2430;")

        self.login_button = QPushButton("Login")
        layout.addWidget(self.login_button)
        self.login_button.setStyleSheet("background-color: #49CF5A;")
        self.login_button.clicked.connect(lambda: self.loginCheck("admin", "123")) #retrieve parameters from DB file


    def loginCheck(self, userName, passwordHash):
        usernameInputCheck = self.username_input.text()
        passwordInputCheck = self.password_input.text()
        if (usernameInputCheck == userName) and (passwordInputCheck == passwordHash):
            self.uponLogin()

        else:
            #provide error pop up "invalid username or password"
            self.login_button.setText("Invalid username or password. Please try again.")
            self.login_button.setStyleSheet("background-color: #EB3324;")
            self.password_input.clear()
            QTimer.singleShot(1250, lambda: self.login_button.setText("Login")) #Timer on 2 seconds
            QTimer.singleShot(1250, lambda: self.login_button.setStyleSheet("background-color: #49CF5A;"))

    def uponLogin(self):
        self.loginSuccess.emit()



if __name__ == "__main__":
    app = QApplication([])
    loginScreen = LoginScreen()
    mainWindow = MainWindow()
    loginScreen.loginSuccess.connect(lambda: (mainWindow.show(), loginScreen.close()))
    loginScreen.show()

    app.exec()
