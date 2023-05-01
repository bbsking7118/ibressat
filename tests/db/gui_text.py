from PySide6 import QtCore, QtWidgets
import sys

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        textedit = QtWidgets.QTextEdit(self)
        textedit.setStyleSheet("color:blue; font-size:13px")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(textedit)
        self.setLayout(layout)
        
        self.setWindowTitle("파이사이드 예제")
        self.resize(400, 300)
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    sys.exit(app.exec_())
