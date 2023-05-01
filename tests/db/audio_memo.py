import sys
from PySide6 import QtCore, QtGui, QtWidgets
import os
import sqlite3 as sql
import speech_recognition as sr

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio, language="ko-KR")
            print("오디오인식: {}".format(said))
        except sr.UnknownValueError:
            print("구글 인식 불가")
        except sr.RequestError as e:
            print("구글 오류: {}".format(e))
        except sr.WaitTimeoutError as e:
            print("타임 아웃: {}".format(e))
    return said

class Worker(QtCore.QThread):
    sig_make_memo = QtCore.Signal()         # 메모 생성 
    sig_update_memo = QtCore.Signal(str)    # 메모 내용 업데이트 
    sig_delete_memo = QtCore.Signal()       # 메모 삭제
    sig_close_memo = QtCore.Signal()        # 메모 위젯 닫기
    sig_exit_thread = QtCore.Signal()       # 오디오 입력 자체를 종료
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
    
    def run(self):
        while True:
            txt = get_audio().strip()
            if txt == "메모":
                self.sig_make_memo.emit()
                while True:
                    memo = get_audio().strip()
                    if memo == "저장":
                        break
                    self.sig_update_memo.emit(memo)
            elif txt == "메모 삭제":
                self.sig_delete_memo.emit()
            elif txt == "메모 닫기":
                self.sig_close_memo.emit()
            elif txt == "종료":
                break
        self.sig_exit_thread.emit()

