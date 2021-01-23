from PySide2.QtWidgets import *
from PySide2.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.testWidget = QLabel("Hello!")
        self.testWidget.setStyleSheet("""background-color: red""")
        self.testWidget2 = QLabel("Hello2!")
        self.testWidget2.setStyleSheet("""background-color: blue""")
        self.testWidget3 = QLabel("Hello3!")
        self.testWidget3.setStyleSheet("""background-color: green""")

        showButton = QPushButton("Show2")
        showButton.clicked.connect(lambda: self.SetVisible(True))
        hideButton = QPushButton("Hide2")
        hideButton.clicked.connect(lambda: self.SetVisible(False))

        centralWidget = QFrame()
        self.setCentralWidget(centralWidget)

        layout = QVBoxLayout()
        layout.addWidget(self.testWidget, stretch=1)
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.testWidget2)
        hLayout.addWidget(self.testWidget3)
        layout.addLayout(hLayout, stretch=1)

        layout.addWidget(showButton)
        layout.addWidget(hideButton)

        centralWidget.setLayout(layout)

        timer = QTimer(self)
        timer.timeout.connect(self.Tick)
        timer.start(0)

    def Tick(self):
        i = 0

    def SetVisible(self, v):
        self.testWidget2.setVisible(v)
        self.testWidget3.setVisible(v)


if __name__ == "__main__":
    app = QApplication()
    win = MainWindow()
    win.show()
    app.exec_()
