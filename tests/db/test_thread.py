import sys
from PySide6 import QtWidgets, QtCore
import time

class MyThread(QtCore.QThread):
    signal_thread = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.isRun = False
        self.parent = parent

    def run(self):
        while self.isRun:
            str_time = "{}".format(time.time())
            self.signal_thread.emit(str_time)
            print(str_time)
            time.sleep(0.5)

class MyWindows(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("남박사의 파이썬 강좌")
        self.button = QtWidgets.QPushButton(self)
        self.textbox = QtWidgets.QTextEdit(self)

        self.button.setText("동작테스트")
        self.button.clicked.connect(self.button_click)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.textbox)

        self.th = MyThread(self)
        self.th.signal_thread.connect(self.slot_thread)

        self.resize(400, 200)
        self.setLayout(layout)
        self.show()
    def slot_thread(self, text):
        self.textbox.append(text)

    
    def button_click(self):
        if not self.th.isRun:
            self.th.isRun = True
            self.th.start()


app = QtWidgets.QApplication(sys.argv)
win = MyWindows()
sys.exit(app.exec_())
