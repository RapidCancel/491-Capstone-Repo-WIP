from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QMenu, QWidget, QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Button Dropdown Example")

        # Create a main widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create a button
        self.button = QPushButton("Open Menu")
        layout.addWidget(self.button)

        # Create a dropdown menu
        self.menu = QMenu()
        self.menu.addAction("Option 1")
        self.menu.addAction("Option 2")
        self.menu.addAction("Option 3")

        # Connect button click to show the menu
        self.button.clicked.connect(self.show_menu)

    def show_menu(self):
        self.menu.exec(self.button.mapToGlobal(self.button.rect().bottomLeft()))

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
