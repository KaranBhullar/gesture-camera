import sys
import App as interface
from PyQt5.QtWidgets import QApplication

if __name__=="__main__":
    app = QApplication(sys.argv)
    a = interface.App()
    a.show()
    sys.exit(app.exec_())