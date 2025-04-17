import sys
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from DBManager import DatabaseManager

# When removing, remove from app.py

class EZResetWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.DBManager = DatabaseManager("hashedCredentials.db")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("EZ Admin Reset")

        layout = QVBoxLayout()

        button = QPushButton("Click Me to Reset Admin")
        button.clicked.connect(self.DBManager.resetDatabase)

        layout.addWidget(button)
        self.setLayout(layout)

    def on_button_click(self):
        print("Button clicked!")
