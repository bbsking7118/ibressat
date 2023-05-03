import sys, os
import configparser
import logging
import logging.handlers
from datetime import datetime, timedelta

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QAxContainer import *
import pandas as pd

# import stocklab.kiwoom.systr as systr
from db.db_handler import Sqlite3DBHandler
from userFunc.crawler import Crawler
from userFunc.tester import tester

sys.path.append(("D:\work_east\c_study\project\python\PyGUI"))
form_class = uic.loadUiType("prj1.ui")[0]  # ui 파일을 로드하여 form_class 생성

class MyWindow(QMainWindow, form_class):  # MyWindow 클래스 QMainWindow, form_class 클래스를 상속 받아 생성됨
    def __init__(self):  # MyWindow 클래스의 초기화 함수(생성자)
        super().__init__()  # 부모클래스 QMainWindow 클래스의 초기화 함수(생성자)를 호출

        # 환경 세팅 ###################################################################
        global logger  # 전체에서 로그를 사용하기 위해 global로 선언을 해줌(전역 변수)
        logger = logging.getLogger('upperLimitPriceTradingLogger')  # 로그 인스턴스를 만든다
        self.set_logger()  # 로그 인스턴스 환경 설정을 셋팅함

        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.dbfile = config['SYSTEM']['dbfile']
        logger.debug("dbfile : {}".format(self.dbfile))

        # GUI 세팅 ################################################################
        self.setupUi(self)
        # self.lePrice.setDisabled(True)  # 투입금 입력란을 비활성화 상태로 변경
        self.cbAcctNo.setDisabled(True)  # 계좌번호 선택란을 비활성화 상태로 변경
        self.leD2Price.setDisabled(True)  # D2예수금 입력란을 비활성화 상태로 변경
        self.cbCdtNm.setDisabled(True)  # 조건검색명 선택란을 비활성화 상태로 변경
        self.leTotalPrice.setDisabled(True)  # 총투입금 입력란을 비활성화 상태로 변경
        self.leProfits.setDisabled(True)  # 수익금 입력란을 비활성화 상태로 변경
        self.leProfitsPc.setDisabled(True)  # 수익률 입력란을 비활성화 상태로 변경
        self.pteBuyLog.setDisabled(True)  # 매도 종목 노출란을 비활성화 상태로 변경
        self.pteSellLog.setDisabled(True)  # 매수 종목 노출란을 비활성화 상태로 변경


        self.pteLog.setDisabled(False)  # 전체 내역 노출란을 비활성화 상태로 변경
        # 이벤트함수...
        self.btnTotal.clicked.connect(self.btnTotalClicked)
        self.btnApt.clicked.connect(self.btnAptClicked)
        self.btnOfficetel.clicked.connect(self.btnOfficetelClicked)
        self.btnSangaEtc.clicked.connect(self.btnSangaEtcClicked)
        self.btnProcessAll.clicked.connect(self.btnProcessAllClicked)

        self.btnTest.clicked.connect(self.btnTestClicked)

        # 전역변수 세팅 ################################################################

        # 변수 세팅 ###################################################################
        self.cur_dir = os.path.dirname(__file__)
        self.db_name = self.cur_dir + "\\memo.db"

        # 프로그램 시작 ###################################################################
        self.sqldb = Sqlite3DBHandler()
        self.con = self.sqldb.con
        # self.kiwoom = systr.sysTrading(self,"DEMO_STRADE") # 키움 클래스 실행

    # 함수 파트 : Logger ##########################################################################
    def set_logger(self):  # 로그 환경을 설정해주는 함수
        fomatter = logging.Formatter(
            '[%(levelname)s|%(lineno)s] %(asctime)s > %(message)s')  # 로그를 남길 방식으로 "[로그레벨|라인번호] 날짜 시간,밀리초 > 메시지" 형식의 포매터를 만든다

        logday = datetime.today().strftime("%Y%m%d")  # 로그 파일 네임에 들어갈 날짜를 만듬 (YYYYmmdd 형태)

        fileMaxByte = 1024 * 1024 * 100  # 파일 최대 용량인 100MB를 변수에 할당 (100MB, 102,400KB)
        fileHandler = logging.handlers.RotatingFileHandler('./log/stock_' + str(logday) + '.log', maxBytes=fileMaxByte,
                                                           backupCount=10)  # 파일에 로그를 출력하는 핸들러 (100MB가 넘으면 최대 10개까지 신규 생성)
        streamHandler = logging.StreamHandler()  # 콘솔에 로그를 출력하는 핸들러

        fileHandler.setFormatter(fomatter)  # 파일에 로그를 출력하는 핸들러에 포매터를 지정
        streamHandler.setFormatter(fomatter)  # 콘솔에 로그를 출력하는 핸들러에 포매터를 지정

        logger.addHandler(fileHandler)  # 로그 인스턴스에 파일에 로그를 출력하는 핸들러를 추가
        logger.addHandler(streamHandler)  # 로그 인스턴스에 콘솔에 로그를 출력하는 핸들러를 추가

        logger.setLevel(logging.DEBUG)  # 로그 레벨을 디버그로 만듬

    # 함수 파트 : GUI ##########################################################################

    # 함수 파트 : 이벤트 ##########################################################################
    def btnTestClicked(self):
        logger.debug("btnTestClicked Start ...")  # debug 레벨 로그를 남김
        # arg =[]
        # karg = {}
        # tester(self,logger)
        # msg = self.leTelMsg.currentText().strip()
        msg = self.leTelMsg.text().strip()
        Crawler(self, logger).telegram_msg(msg)

    def btnTotalClicked(self):
        logger.debug("btnTotalClicked Start ...")  # debug 레벨 로그를 남김
        # tempPrice = self.lePrice.text().strip().replace(',', '')  # 입력된 종목당 투입금을 가져옴
        # conditionName = self.cbCdtNm.currentText().strip()
        # index, name = conditionName.split('^')
        # QMessageBox.about(self, "message", "계좌번호를 선택해주세요.")  # 계좌번호가 없다면 안내 얼럿 노출
        # df = Crawler(self, logger).job_start(1)
        # df.to_excel(self.dbfile + "apt" + datetime.today().strftime("%Y%m%d") + ".xlsx")
        self.pteLog.clear()
        mdf = pd.DataFrame()
        isUpdated = False
        file = self.dbfile + "_apt_" + datetime.today().strftime("%Y%m%d") + ".xlsx"
        if os.path.exists(file):
            logger.debug("file(apt) exist ...")
            df = pd.read_excel(file)
            self.send_telegrammsg(df)
            mdf = pd.concat([mdf, df], ignore_index=True)
            isUpdated = True
            # df.to_excel(self.dbfile + "_all_" + datetime.today().strftime("%Y%m%d") + ".xlsx", index = True)
        file = self.dbfile + "_officetel_" + datetime.today().strftime("%Y%m%d") + ".xlsx"
        if os.path.exists(file):
            logger.debug("file(officetel) exist ...")
            df = pd.read_excel(file)
            self.send_telegrammsg(df)
            mdf = pd.concat([mdf, df], ignore_index=True)
            # print(mdf)

            isUpdated = True
            # df.to_excel(self.dbfile + "_all_" + datetime.today().strftime("%Y%m%d") + ".xlsx", index=False)
        file = self.dbfile + "_sangaetc_" + datetime.today().strftime("%Y%m%d") + ".xlsx"
        if os.path.exists(file):
            logger.debug("file(sangaetc) exist ...")
            df = pd.read_excel(file)
            self.send_telegrammsg(df)
            mdf = pd.concat([mdf, df], ignore_index=True)
            isUpdated = True

        if isUpdated == True:
            mdf.to_excel(self.dbfile + "_all_" + datetime.today().strftime("%Y%m%d") + ".xlsx", index=False)
            today = datetime.today()
            diffday = timedelta(days=2)
            msges = []
            for i in range(mdf.shape[0] - 1):
                rday = datetime.strptime(mdf.iloc[i]["등록일"], "%Y-%m-%d")
                if (today - rday) < diffday:
                    msg = "\n".join(str(x) for x in list(mdf.iloc[i]))
                    msges.append(msg)

    def send_telegrammsg(self,df):
        today = datetime.today()
        diffday = timedelta(days=1)
        msges = []
        for i in range(df.shape[0] - 1):
            rday = datetime.strptime(df.iloc[i]["등록일"], "%Y-%m-%d")
            #         print(today, rday, diffday)
            if (today - rday) < diffday:
                msg = "\n".join(str(x) for x in list(df.iloc[i]))
                # Crawler(self, logger).telegram_msg(msg)
                msges.append(msg)

        # print("\n=======\n".join(msges))
        Crawler(self, logger).telegram_msg("\n=======\n".join(msges))

    def btnAptClicked(self):
        logger.debug("btnAptClicked Start ...")  # debug 레벨 로그를 남김
        # tempPrice = self.lePrice.text().strip().replace(',', '')  # 입력된 종목당 투입금을 가져옴
        # conditionName = self.cbCdtNm.currentText().strip()
        # index, name = conditionName.split('^')
        # QMessageBox.about(self, "message", "계좌번호를 선택해주세요.")  # 계좌번호가 없다면 안내 얼럿 노출
        self.pteLog.clear()
        df = Crawler(self,logger).job_start_full(1)
        df.to_excel(self.dbfile+"_apt_"+datetime.today().strftime("%Y%m%d")+".xlsx", index=False)

    def btnOfficetelClicked(self):
        logger.debug("btnOffecetelClicked Start ...")  # debug 레벨 로그를 남김
        self.pteLog.clear()
        df = Crawler(self,logger).job_start_full(2)
        df.to_excel(self.dbfile+"_officetel_"+datetime.today().strftime("%Y%m%d")+".xlsx", index=False)

    def btnSangaEtcClicked(self):
        logger.debug("btnSangaEtcClicked Start ...")  # debug 레벨 로그를 남김
        self.pteLog.clear()
        df = Crawler(self, logger).job_start_full(3)
        df.to_excel(self.dbfile + "_sangaetc_" + datetime.today().strftime("%Y%m%d") + ".xlsx", index=False)

    def btnProcessAllClicked(self):
        logger.debug("btnProcessAllClicked Start ...")
        self.pteLog.clear()

        mdf = pd.DataFrame()
        cl = Crawler(self, logger)
        df = cl.job_start(1)
        mdf = pd.concat([mdf, df], ignore_index=True)
        df = cl.job_start(2)
        mdf = pd.concat([mdf, df], ignore_index=True)
        df = cl.job_start(3)
        mdf = pd.concat([mdf, df], ignore_index=True)

        mdf.to_excel(self.dbfile + "_all_" + datetime.today().strftime("%Y%m%d") + ".xlsx", index=False)

    # 함수 파트 : 시그널 이벤트 ##########################################################################

    # 함수 파트 : 함수 ##########################################################################
if __name__ == "__main__":
    print("Main() start")
    app = QApplication(sys.argv)  # PyQt5로 실행할 파일명을 자동 설정
    myWindow = MyWindow()  # MyWindow 클래스를 생성하여 myWondow 변수에 할당
    myWindow.show()  # MyWindow 클래스를 노출
    app.exec_()  # 이벤트 루프 실행
