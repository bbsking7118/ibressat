from PySide6 import QtCore, QtWidgets
import sys

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        buton = QtWidgets.QPushButton(self)
        buton.setText("일반버튼")

        disable_button = QtWidgets.QPushButton(self)
        disable_button.setText("비활성버튼")
        disable_button.setEnabled(False)

        check_button = QtWidgets.QPushButton(self)
        check_button.setText("체크버튼")
        check_button.setCheckable(True)
        check_button.toggle()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(buton)
        layout.addWidget(disable_button)
        layout.addWidget(check_button)

        buton.clicked.connect(self.btn_clicked)
        check_button.clicked.connect(self.btn_clicked)

        self.setLayout(layout)
        self.setWindowTitle("파이사이드 예제")
        self.resize(400, 300)
        self.show()
    def btn_clicked(self):
        sender = self.sender()
        QtWidgets.QMessageBox.about(self, "메세지박스", sender.text())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MyWindow()
    sys.exit(app.exec_())
