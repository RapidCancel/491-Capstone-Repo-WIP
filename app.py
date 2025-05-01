import sys
from PySide6.QtWidgets import QApplication
from login import LoginScreen
from mainWindow import MainWindow

from addCommission import AddCommissionWidget

from reset import EZResetWidget     # Remove EZReset after

def onLogin():
    mainWindow.show()
    loginScreen.deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginScreen = LoginScreen(0)
    mainWindow = MainWindow()

    #addCommission = AddCommissionWidget()
    #addCommission.show()

    eZReset = EZResetWidget()
    eZReset.show()

    loginScreen.loginSuccess.connect(onLogin)
    loginScreen.show()

    app.exec()
