from PySide6 import QtCore, QtWidgets
import sys

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        label_1 = QtWidgets.QLabel("라벨1 입니다.", self)
        label_1.setAlignment(QtCore.Qt.AlignCenter)
        label_1.setStyleSheet("color:blue; font-size:20px;")
        label_1.resize(60, 25)

        label_2 = QtWidgets.QLabel("라벨2 입니다.", self)
        label_2.setAlignment(QtCore.Qt.AlignRight)
        label_2.setStyleSheet("color:red; font-size:25px;")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_1)
        layout.addWidget(label_2)

        self.setLayout(layout)
        self.setWindowTitle("파이사이드 예제")
        self.resize(400, 300)
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    sys.exit(app.exec_())
