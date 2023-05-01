import sys
import os
from PySide6 import QtCore, QtGui, QtWidgets
import sqlite3 as sql
from audio_memo import Worker

class MyBar(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.title = QtWidgets.QLabel()

        btn_size = 30

        self.btn_new = QtWidgets.QPushButton("+")
        self.btn_new.setFixedSize(btn_size, btn_size)
        self.btn_new.setStyleSheet("border:0px; background-color: {}".format(parent.color_bg))

        self.btn_close = QtWidgets.QPushButton("X")
        self.btn_close.setFixedSize(btn_size, btn_size)
        self.btn_close.setStyleSheet("border:0px; background-color: {}".format(parent.color_bg))

        self.btn_color = QtWidgets.QPushButton("C")
        self.btn_color.setFixedSize(btn_size, btn_size)
        self.btn_color.setStyleSheet("border:0px; background-color: {}".format(parent.color_bg))

        self.btn_new.clicked.connect(self.btn_new_clicked)
        self.btn_color.clicked.connect(self.btn_color_clicked)
        self.btn_close.clicked.connect(self.btn_delete_clicked)

        self.title.setFixedHeight(30)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        
        self.layout.addWidget(self.btn_new)
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.btn_color)
        self.layout.addWidget(self.btn_close)
        self.title.setStyleSheet("""
        background-color: {};
        color: {};
        """.format(parent.color_bg, parent.color_text))
        self.setLayout(self.layout)

    def btn_new_clicked(self):
        self.parent.on_create()

    def btn_color_clicked(self):
        print("color clicked")
        self.parent.changeBgColor()

    def btn_delete_clicked(self):
        print("delete clicked")
        buttonReply = QtWidgets.QMessageBox.question(self, 
                                    "파이메모", 
                                    "현재 메모를 삭제 하시겠습니까?", 
                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                    QtWidgets.QMessageBox.No)
        if buttonReply == QtWidgets.QMessageBox.Yes:
            print("Yes click!!!")
            self.parent.delete_window()
        else:
            print("No Click!!")
            self.parent.close()

    def setColor(self, color):
        self.title.setStyleSheet("background-color:{}".format(color))
        self.btn_new.setStyleSheet("border:0px; background-color:{}".format(color))
        self.btn_color.setStyleSheet("border:0px; background-color:{}".format(color))
        self.btn_close.setStyleSheet("border:0px; background-color:{}".format(color))
        

class MyMemo(QtWidgets.QWidget):
    def __init__(self, on_create, on_close, on_delete, idx=None, memo=None, rect=None, color_bg=None, color_text=None):
        super().__init__()
        self.on_create = on_create
        self.on_close = on_close
        self.on_delete = on_delete
        self.memo = memo
        self.idx = idx
        self.rect = rect
        self.color_bg = "#dce459" if color_bg is None else color_bg
        self.color_text = "#000000" if color_text is None else color_text
        self.oldPos = None
        self.deleted = False
        self.initUI()

    def initUI(self):
        self.note = QtWidgets.QTextEdit(self)
        color_text = "QTextEdit {border: 0; background-color:" + self.color_bg + "; color: " + self.color_text + "}"
        self.note.setStyleSheet(color_text)

        self.title_bar = MyBar(self)
        self.title_bar.setStyleSheet("top: -20px")

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        grip = QtWidgets.QSizeGrip(self)
        self.layout.addWidget(self.title_bar)
        self.layout.addWidget(self.note)
        self.layout.addWidget(grip, 0, QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)
        self.setLayout(self.layout)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        if self.memo:
            self.note.setText(self.memo)
        if self.rect:
            self.setGeometry(self.rect)
        self.show()

    def add_memo(self, text):
        cur_text = self.note.toPlainText()
        text = text.replace("엔터", "\n").replace("공백", " ").replace("느낌표", "!")
        cur_text += text
        self.note.setText(cur_text)
        self.note.moveCursor(QtGui.QTextCursor.End)

    def delete_window(self):
        self.deleted = True
        self.on_delete(self.idx)
        self.close()
    def closeEvent(self, e):
        if not self.deleted:
            self.on_close(self.idx, self.geometry().getRect(), self.get_current_memo(), self.color_bg, self.color_text)
    def get_current_memo(self):
        if not self.note.toPlainText():
            return ""
        return self.note.toHtml()
    def changeBgColor(self):
        selected_color = QtWidgets.QColorDialog.getColor().name()
        self.color_bg = selected_color
        self.note.setStyleSheet("border:0px; background-color:{}".format(selected_color))
        self.title_bar.setColor(selected_color)
    
    def resizeEvent(self, _):
        self.oldPos = None

    def mousePressEvent(self, e):
        self.oldPos = e.globalPos()

    def mouseMoveEvent(self, e):
        if self.oldPos is not None:
            delta = QtCore.QPoint(e.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = e.globalPos()

class MyApp():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.windows = []
        self.cur_dir = os.path.dirname(__file__)
        self.db_name = self.cur_dir + "\\memo.db"
        self.initDB()
        self.loadDB()
        self.current_memo = None

        self.th = Worker()
        self.th.sig_make_memo.connect(self.memo_make)
        self.th.sig_close_memo.connect(self.memo_close)
        self.th.sig_delete_memo.connect(self.memo_delete)
        self.th.sig_update_memo.connect(self.memo_update)
        self.th.sig_exit_thread.connect(self.exit_thread)
        self.th.start()
        return
    
    def memo_make(self):
        self.create_new_memo()

    def memo_update(self, text):
        if self.current_memo is not None:
            self.current_memo.add_memo(text)

    def memo_close(self):
        self.current_memo.close()

    def memo_delete(self):
        self.current_memo.delete_window()

    def exit_thread(self):
        sys.exit()
        
    def initDB(self):
        self.con = sql.connect(self.db_name)
        self.cursor = self.con.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS memo (
            '_idx' INTEGER PRIMARY KEY AUTOINCREMENT,
            '_title' VARCHAR(500),
            '_memo' TEXT,
            '_pubdate' TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            '_pos_x' INTEGER,
            '_pos_y' INTEGER,
            '_width' INTEGER,
            '_height' INTEGER,
            '_color_bg' VARCHAR(30),
            '_color_text' VARCHAR(30)
        )
        """
        self.con.execute(query)
        self.con.close()

    def close_memo(self, idx, rect, memo, color_bg, color_text):
        x, y, w, h = rect
        if memo == "" or memo is None:
            return
        if idx is None:
            query = """
            INSERT INTO memo (_memo, _pos_x, _pos_y, _width, _height, _color_bg, _color_text)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            with sql.connect(self.db_name) as con:
                cur = con.cursor()
                cur.execute(query, (memo, x, y, w, h, color_bg, color_text))
                con.commit()
                cur.close()
        else:
            query = """
            UPDATE memo 
                SET _memo=?,
                _pos_x=?,
                _pos_y=?,
                _width=?,
                _height=?,
                _color_bg=?,
                _color_text=?
            WHERE _idx=?
            """
            with sql.connect(self.db_name) as con:
                cur = con.cursor()
                cur.execute(query, (memo, x, y, w, h, color_bg, color_text, idx))
                con.commit()
                cur.close()
    def delete_memo(self, idx=None):
        if idx is not None:
            query = "DELETE FROM memo WHERE _idx=?"
            with sql.connect(self.db_name) as con:
                cur = con.cursor()
                cur.execute(query, (idx, ))
                con.commit()
                cur.close()
    def loadDB(self):
        memos = []
        query = "SELECT _idx, _title, _memo, _pos_x, _pos_y, _width, _height, _color_bg, _color_text FROM memo"
        with sql.connect(self.db_name) as con:
            cur = con.cursor()
            cur.execute(query)
            memos = cur.fetchall()
            cur.close()
        
        for m in memos:
            idx, memo, x, y, w, h, c_bg, c_text = m
            self.create_new_memo(idx, memo, QtCore.QRect(x, y, w, h), c_bg, c_text)


    def initMemo(self):
        self.create_new_memo()

    def create_new_memo(self, idx=None, memo=None, rect=None, color_bg=None, color_text=None):
        w = MyMemo(self.create_new_memo, self.close_memo, self.delete_memo, idx, memo, rect, color_bg, color_text)
        w.show()
        self.current_memo = w
        self.windows.append(w)



main = MyApp()
sys.exit(main.app.exec_())
