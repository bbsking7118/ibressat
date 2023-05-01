import sys
from PySide6 import QtWidgets

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("이벤트 체크")
        self.status_bar = self.statusBar()
        self.setMouseTracking(True)
        self.setGeometry(300, 300, 300, 200)
        self.show()
    
    def keyPressEvent(self, event):
        output = "Press key <key : {}>".format(event.key())
        self.status_bar.showMessage(output)

    def keyReleaseEvent(self, event):
        output = "Release key <key : {}>".format(event.key())
        self.status_bar.showMessage(output)
    
    def mouseDoubleClickEvent(self, event):
        button = event.button()
        x = event.x()
        y = event.y()
        gx = event.globalX()
        gy = event.globalY()
        output = "마우스 더블클릭 <버튼: {}, x: {}, y: {}, gx: {}, gy: {}>".format(button, x, y, gx, gy)
        self.status_bar.showMessage(output)
    def mouseMoveEvent(self, e):
        x = e.x()
        y = e.y()
        gx = e.globalX()
        gy = e.globalY()
        output = "마우스 이동 <x: {}, y: {}, gx: {}, gy: {}>".format(x, y, gx, gy)
        self.status_bar.showMessage(output)
    def mousePressEvent(self, event):
        button = event.button()
        x = event.x()
        y = event.y()
        gx = event.globalX()
        gy = event.globalY()
        output = "마우스 클릭 <버튼: {}, x: {}, y: {}, gx: {}, gy: {}>".format(button, x, y, gx, gy)
        self.status_bar.showMessage(output)
    def mouseReleaseEvent(self, event):
        button = event.button()
        x = event.x()
        y = event.y()
        gx = event.globalX()
        gy = event.globalY()
        output = "마우스 릴리즈 <버튼: {}, x: {}, y: {}, gx: {}, gy: {}>".format(button, x, y, gx, gy)
        self.status_bar.showMessage(output)
    def resizeEvent(self, e):
        current_pos = e.size().width(), e.size().height()
        old_pos = e.oldSize().width(), e.oldSize().height()
        output = "윈도우 리사이즈 <현재: {}, 이전: {}>".format(current_pos, old_pos)
        self.status_bar.showMessage(output)
    def moveEvent(self, e):
        current_pos = e.pos().x(), e.pos().y()
        old_pos = e.oldPos().x(), e.oldPos().y()
        output = "윈도우 이동 <현재: {}, 이전: {}>".format(current_pos, old_pos)
        self.status_bar.showMessage(output)
    def closeEvent(self, event):
        print("메인윈도우 종료")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    my = MyApp()
    sys.exit(app.exec_())
