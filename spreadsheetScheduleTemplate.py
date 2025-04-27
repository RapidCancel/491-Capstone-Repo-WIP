from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import sys


class ScheduleApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Daily Schedule")
        self.setGeometry(100, 100, 800, 600)

        # Create main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Create main layout
        main_layout = QVBoxLayout()

        # Create horizontal layout for dropdown and buttons
        control_layout = QHBoxLayout()

        # Create dropdown menu
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Option 1", "Option 2", "Option 3"])

        # Create buttons
        self.button1 = QPushButton("Button 1")
        self.button2 = QPushButton("Button 2")

        # Add widgets to control layout
        control_layout.addWidget(self.dropdown)
        control_layout.addWidget(self.button1)
        control_layout.addWidget(self.button2)

        # Create the table widget
        self.table = QTableWidget(10, 4)  # 10 rows (hours) and 4 columns (people)
        self.table.setHorizontalHeaderLabels(["Alice", "Bob", "Charlie", "Dave"])
        self.table.setVerticalHeaderLabels([f"{hour}:00" for hour in range(8, 18)])

        # Add layouts to main layout
        main_layout.addLayout(control_layout)  # Dropdown and buttons on top
        main_layout.addWidget(self.table)  # Table below

        # Set main layout to central widget
        main_widget.setLayout(main_layout)

        # Insert a merged activity for "Charlie" from 9 AM to 11 AM #THIS ONE IS IMPORTANT FOR FORMATTING THE GOOD CELLS
        self.add_activity(row=1, col=2, duration=2, text="Team Meeting", color=QColor(255, 200, 100))

    def add_activity(self, row, col, duration, text, color):
        """Insert a merged, colored cell for an activity."""
        self.table.setSpan(row, col, duration, 1)  # Merge cells vertically
        item = QTableWidgetItem(text)

        # Apply style directly to the item
        item.setTextAlignment(Qt.AlignCenter)  # Center the text
        item.setBackground(color)

        self.table.setItem(row, col, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScheduleApp()
    window.show()
    sys.exit(app.exec())
