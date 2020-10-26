from UI.MainWindow import *
import sys

if __name__ == "__main__":
    app = QApplication()
    win = MainApp()
    win.show()
    sys.exit(app.exec_())
