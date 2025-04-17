import sys
from PySide6.QtWidgets import QApplication
from login import LoginScreen
from mainWindow import MainWindow
from reset import EZResetWidget

def onLogin():
    mainWindow.show()
    loginScreen.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginScreen = LoginScreen(0)
    mainWindow = MainWindow()
    eZReset = EZResetWidget()
    eZReset.show()

    loginScreen.loginSuccess.connect(onLogin)
    loginScreen.show()

    app.exec()
