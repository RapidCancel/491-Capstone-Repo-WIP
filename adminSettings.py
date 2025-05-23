from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QShortcut, QIcon
from DBManager import DatabaseManager

class AdminSettingsWindow(QWidget):
    credentialsChanged = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Change Admin Credentials")
        self.setGeometry(200, 200, 300, 150)

        # UI elements
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("New username...")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("New password...")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.revealButton = QPushButton()    # Replace text with a picture of an eye or smthin
        self.revealButton.setFixedSize(30, 30)     # width, height
        # Apply stylesheet with an image
        self.revealButton.setStyleSheet("""
            QPushButton {
                border: none;
            }
        """)
        self.revealButton.setIcon(QIcon("ui_elements/white_eye_graphic_transparent.png"))  # Replace with the image path
        self.revealButton.setIconSize(self.revealButton.size())  # Scale image to match button size

        self.revealButton.pressed.connect(self.revealPassword)
        self.revealButton.released.connect(self.concealPassword)

        self.confirmButton = QPushButton("Confirm")
        self.confirmButton.clicked.connect(self.saveCredentials)

        self.confirmShortcut = QShortcut(Qt.Key_Return, self)      # Return key shortcut for login
        self.confirmShortcut.activated.connect(self.confirmButton.clicked)

        vLayout = QVBoxLayout()     # Primary vertical layout
        vLayout.addWidget(QLabel("Placeholder password suggestions here"))
        vLayout.addWidget(self.username_input)

        hLayout = QHBoxLayout()     # Secondary horizontal layout
        hLayout.addWidget(self.password_input)
        hLayout.addWidget(self.revealButton)

        vLayout.addLayout(hLayout) # Horizontal layer added to primary layout

        vLayout.addWidget(self.confirmButton)
        self.setLayout(vLayout)

        self.DBManager = DatabaseManager("hashedCredentials.db")


    def saveCredentials(self):
        usernameInput = self.username_input.text()
        passwordInputHashed = self.DBManager.hashString(self.password_input.text())
        self.username_input.clear()
        self.password_input.clear()

        if not usernameInput or not passwordInputHashed:
            self.confirmButton.setText("Please enter a new username and password.")
            self.confirmButton.setStyleSheet("background-color: #F26A6D;")
            QTimer.singleShot(1250, lambda: self.confirmButton.setText("Confirm")) #Timer on 1.25 seconds
            QTimer.singleShot(1250, lambda: self.confirmButton.setStyleSheet("background-color: #3C3C3C;"))

        else:
            renameQuery = "INSERT INTO users (username, hashedPassword) VALUES (?, ?);" #In the future, increment id value for new users if not admin
            self.DBManager.connectToDB("hashedCredentials.db")
            self.DBManager.cursor.execute("DELETE FROM users")  # Clear previous credentials
            self.DBManager.cursor.execute(renameQuery, (usernameInput, passwordInputHashed))
            self.DBManager.conn.commit()
            self.DBManager.conn.close()

            self.confirmButton.setText("Changes Saved!")
            self.confirmButton.setStyleSheet("background-color: #49CF5A;")
            QTimer.singleShot(1500, lambda: self.confirmButton.setText("Confirm")) #Timer on 1.25 seconds
            QTimer.singleShot(1500, lambda: self.confirmButton.setStyleSheet("background-color: #3C3C3C;"))


    def revealPassword(self):
        self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)

    def concealPassword(self):
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)


# if __name__ == "__main__":
#     pass
