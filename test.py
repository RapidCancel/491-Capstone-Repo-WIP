import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QIcon

class ImageButtonLineEdit(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QLineEdit with Image Button")

        layout = QHBoxLayout()

        # Create the QLineEdit
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Search...")

        # Create the QPushButton with an icon
        self.button = QPushButton()
        self.button.setFixedSize(30, 30)  # Set button size
        self.button.setIcon(QIcon("search_icon.png"))  # Replace with the image path
        self.button.setIconSize(self.button.size())  # Scale image to match button size

        # Connect button action
        self.button.clicked.connect(self.search_action)

        # Add widgets to the layout
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def search_action(self):
        """Handle button click (for example, print the search query)."""
        print(f"Searching for: {self.line_edit.text()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageButtonLineEdit()
    window.show()
    sys.exit(app.exec())
