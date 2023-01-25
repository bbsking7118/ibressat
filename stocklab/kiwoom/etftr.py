import os
import sys
import time, calendar
import configparser
import logging
import logging.handlers
from datetime import datetime
import pandas as pd
import pymongo

from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from PyQt5.QtTest import *

from stocklab.kiwoom.config.errorCode import *
from stocklab.kiwoom.config.kiwoomType import *
from stocklab.kiwoom.config.slack import *
from stocklab.db_handler.mongodb_handler import MongoDBHandler

class sysTrading(QAxWidget):
    def __init__(self, mode=None):
        super().__init__()
        ## 환경세팅 #######################################################################################
        self.realType = RealType()
        global logger  # 전체에서 로그를 사용하기 위해 global로 선언을 해줌(전역 변수)
        logger = logging.getLogger('upperLimitPriceTradingLogger')  # 로그 인스턴스를 만든다
        self.set_logger()  # 로그 인스턴스 환경 설정을 셋팅함
        self.slack = MyMsg()  # 슬랙 동작
        self.slack.send_msg(msg="bsking 슬랙메시지 전송하기")
        logger.debug("Kiwoom() class start.")
        ## config.ini #######################################################################################
        if mode not in ["DEMO_STRADE", "REAL_STRADE", "DEMO_FTRADE", "REAL_FTRADE"]:
            raise Exception("Need to run_mode(DEMO_STRADE or REAL_STRADE or DEMO_FTRADE or REAL_FTRADE)")
        run_mode = mode
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        self.account = config[run_mode]['account']
        self.use_money = 500000000 #실제 투자에 사용할 금액
        self.use_money_percent = 0.7 #예수금에서 실제 사용할 비율
        self.unit_money = int(config[run_mode]['unit_money'])  # 실제 투자에 사용할 금액
        self.maxStockNum = int(config[run_mode]['maxStockNum'])  # 실제 투자에 사용할 금액
        logger.debug("account(config.ini) : %s"%self.account)

        ######### 초기 셋팅 func들 바로 실행
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1") # 레지스트리에 저장된 api 모듈 불러오기
        self.OnEventConnect.connect(self.login_slot)  # 로그인 관련 이벤트
        self.OnReceiveTrData.connect(self.trdata_slot)  # 트랜잭션 요청 관련 이벤트
        self.OnReceiveMsg.connect(self.msg_slot)
        self.OnReceiveRealData.connect(self.realdata_slot)  # 실시간 이벤트 연결
        self.OnReceiveChejanData.connect(self.chejan_slot)  # 종목 주문체결 관련한 이벤트

        ####### event loop를 실행하기 위한 변수모음
        self.login_event_loop = QEventLoop() #로그인 요청용 이벤트루프
        self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트루프
        self.calculator_event_loop = QEventLoop()
        #########################################

        ####### login
        self.block_signal_login_commConnect() #로그인 요청 시그널 포함

        ########### 전체 종목 관리
        self.all_stock_dict = {}
        ###########################
        ####### 계좌 관련된 변수
        self.account_num = ""
        self.account_stock_dict = {} # unit stock
        self.account1_stock_dict = {}
        self.account2_stock_dict = {}
        self.not_account_stock_dict = {}
        self.deposit = 0 #예수금
        self.output_deposit = 0 #출력가능 금액
        self.total_profit_loss_money = 0 #총평가손익금액
        self.total_profit_loss_rate = 0.0 #총수익률(%)
        ########################################
        ######## 종목 정보 가져오기
        self.portfolio_stock_dict = {}
        self.jango_dict = {}
        ########################
        ########### 종목 분석 용
        self.calcul_data = []
        ##########################################
        ####### 요청 스크린 번호
        self.screen_my_info = "2000" #계좌 관련한 스크린 번호
        self.screen_calculation_stock = "4000" #계산용 스크린 번호
        self.screen_real_stock = "5000" #종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용스크린 번호
        self.screen_start_stop_real = "1000" #장 시작/종료 실시간 스크린번호
        ########################################

        # trading loop ########################################
        if run_mode == "DEMO_STRADE" or run_mode == "REAL_STRADE":
            self.isTradingState = "None"
            self.setupSystemTrading()
            self.startSystemTrading()
        elif run_mode == "DEMO_ETF" or run_mode == "REAL_ETF":
            h1 = Thread1(self)
            h1.start()

        #########################################

    # 함수시작 ##############################################################################################
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

        logger.setLevel(logging.INFO)  # 로그 레벨을 디버그로 만듬

    def block_signal_login_commConnect(self):
        logger.debug("func : block_signal_login_commConnect")
        self.dynamicCall("CommConnect()") # 로그인 요청 시그널
        self.login_event_loop.exec_() # 이벤트루프 실행

    def login_slot(self, err_code):
        logger.debug("func : login_slot")
        logger.debug(errors(err_code)[1])
        #로그인 처리가 완료됐으면 이벤트 루프를 종료한다.
        self.login_event_loop.exit()

    def block_get_account_info(self):
        logger.debug("func : block_get_account_info")
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO") # 계좌번호 반환
        logger.info("account_list : %s" % account_list)
        account_num = account_list.split(';')[0]
        self.account_num = account_num
        self.account_num = self.account # config.ini 에서 읽어온계좌
        logger.info("accout_num : %s" % self.account_num)
        # exit()

    def block_detail_account_info(self, sPrevNext="0"):
        logger.debug("func: block_detail_account_info")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    def block_detail_account_mystock(self, sPrevNext="0"):
        logger.debug("func: block_detail_account_mystock")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def not_concluded_account(self, sPrevNext="0"):
        logger.debug("func : not_concluded_account")
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def stop_screen_cancel(self, sScrNo=None):
        logger.debug("func : stop_screen_cancel")
        self.dynamicCall("DisconnectRealData(QString)", sScrNo) # 스크린번호 연결 끊기

    def read_code_xls(self):
        logger.debug("func : read_code")
        aPath = "E:/work/Python/prj3/analysys/input/거래종목.xlsx"
        if os.path.exists(aPath): # 해당 경로에 파일이 있는지 체크한다.
            # df = pd.read_excel(aPath)
            # df.columns = ["종목코드", "종목명", "EV10", "EV3H", "EV3L", "EV40", "PVOLIC"]
            df = pd.read_excel(aPath, names=["종목코드", "종목명", "EV10", "EV3H", "EV3L", "EV40", "PVOLIC", "거래여부"])
            logger.debug(df)
            # codes = df["종목코드"]
            #
            for idx, row in df.iterrows(): #줄바꿈된 내용들이 한줄 씩 읽어와진다.
                stock_code = row[0][1:]
                stock_name = row[1]
                stock_EV10 = int(row[2])
                stock_EV3H = int(row[3])
                stock_EV3L = int(row[4])
                stock_EV40 = int(row[5])
                stock_PVOLIC = int(row[6])
                stock_decision = row[7]
                logger.debug(type(row[7]),stock_decision)
                if stock_decision == 1:
                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "EV10":stock_EV10, "EV3H":stock_EV3H, "EV3L":stock_EV3L,
                                                                  "EV40":stock_EV40, "PVOLIC":stock_PVOLIC, "매도": "가능", "매수": "가능"}})
                    # self.portfolio_stock_dict.update({stock_code: {"종목명": stock_name}})
                else :
                    self.portfolio_stock_dict.update({stock_code: {"종목명": stock_name, "EV10": stock_EV10, "EV3H": stock_EV3H, "EV3L": stock_EV3L,
                                                                    "EV40": stock_EV40, "PVOLIC": stock_PVOLIC, "매도": "가능", "매수": "불가능"}})
            logger.debug("self.portfolio_stock_dict")
            logger.debug(self.portfolio_stock_dict)

    def screen_number_setting(self):
        logger.debug("func : screen_number_setting")
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)


        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)


        #포트폴리로에 담겨있는 종목들
        for code in self.portfolio_stock_dict.keys():

            if code not in screen_overwrite:
                screen_overwrite.append(code)


        # 스크린번호 할당
        cnt = 0
        for code in screen_overwrite:

            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                # self.portfolio_stock_dict[code].update({"매도": "가능"})
                # self.portfolio_stock_dict[code].update({"매수": "가능"})
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock),
                                                 "매도": "가능","매수": "불가능"}})
            cnt += 1
        logger.info("Screen settion => self.portfolio_stock_dict")
        logger.info(self.portfolio_stock_dict)

    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        logger.debug("func : day_kiwoom_db")
        QTest.qWait(3600) #3.6초마다 딜레이를 준다.

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")

        if date != None:
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)  # Tr서버로 전송 -Transaction

        self.calculator_event_loop.exec_()

    ## 안쓰는 함수들 ######################################################################################
    def get_code_list_by_market(self, market_code):
        logger.debug("func : get_code_list_by_market")
        '''
        종목코드 리스트 받기
        #0:장내, 10:코스닥
        :param market_code: 시장코드 입력
        :return:
        '''
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(';')[:-1]
        return code_list
    def calculator_fnc(self):
        logger.debug("func : calculator_fnc")
        '''
        종목 분석관련 func 모음
        :return:
        '''

        code_list = self.get_code_list_by_market("10")
        logger.debug("코스닥 갯수 %s " % len(code_list))

        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기

            logger.debug("%s / %s :  KOSDAQ Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)
    def read_code(self):
        logger.debug("func : read_code")
        if os.path.exists("stocklab/kiwoom/files/condition_stock.txt"): # 해당 경로에 파일이 있는지 체크한다.
            f = open("stocklab/kiwoom/files/condition_stock.txt", "r", encoding="utf8") # "r"을 인자로 던져주면 파일 내용을 읽어 오겠다는 뜻이다.
            #f = open("files/condition_stock.txt", "r", encoding="utf-16")  # "r"을 인자로 던져주면 파일 내용을 읽어 오겠다는 뜻이다.

            lines = f.readlines() #파일에 있는 내용들이 모두 읽어와 진다.
            for line in lines: #줄바꿈된 내용들이 한줄 씩 읽어와진다.
                if line != "":
                    ls = line.strip().split("\t")

                    stock_code = ls[0]
                    stock_name = ls[1]
                    #stock_price = int(ls[2].split("\n")[0])
                    stock_price = int(ls[2])
                    stock_price = abs(stock_price)
                    stock_buyDecision = int(ls[3])
                    stock_buyDecision = abs(stock_buyDecision)
                    stock_sellDecision = int(ls[4])
                    stock_sellDecision = abs(stock_sellDecision)

                    self.portfolio_stock_dict.update({stock_code:{"종목명":stock_name, "현재가":stock_price, "매수기준":stock_buyDecision, "매도기준":stock_sellDecision}})
                    #self.portfolio_stock_dict.update({stock_code: {"종목명": stock_name}})
            f.close()
    def merge_dict(self):
        logger.debug("func : merge_dict")
        self.all_stock_dict.update({"계좌평가잔고내역": self.account_stock_dict})
        self.all_stock_dict.update({'미체결종목': self.not_account_stock_dict})
        self.all_stock_dict.update({'포트폴리오종목': self.portfolio_stock_dict})
    def file_delete(self):
        logger.debug("func : file_delete")
        if os.path.isfile("stocklab/kiwoom/files/condition_stock.txt"):
            os.remove("stocklab/kiwoom/files/condition_stock.txt")
            ############################################################################
    def make_ConditionFile(self):
        logger.debug("func : make_ConditionFile")
        if os.path.exists("stocklab/kiwoom/files/condition_stock0.txt"): # 해당 경로에 파일이 있는지 체크한다.
            f = open("stocklab/kiwoom/files/condition_stock0.txt", "r", encoding="utf-16") # "r"을 인자로 던져주면 파일 내용을 읽어 오겠다는 뜻이다.

            code_list = []
            lines = f.readlines() #파일에 있는 내용들이 모두 읽어와 진다.
            for line in lines: #줄바꿈된 내용들이 한줄 씩 읽어와진다.
                if line != "":
                    ls = line.strip().split("\t")
                    code_list.append(ls[0][1:])
            f.close()

        logger.debug("갯수 %s " % len(code_list))
        for idx, code in enumerate(code_list):
            self.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock)  # 스크린 연결 끊기

            logger.debug("%s / %s :  KOSDAQ Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)
    def sell_all(self):
        logger.debug("func : sell_all")
        for sCode in self.account_stock_dict.keys():
            asd = self.account_stock_dict[sCode]
            #meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
            if asd['매매가능수량'] > 0:
                order_success = self.dynamicCall(
                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                    ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['매매가능수량'], 0,
                     self.realType.SENDTYPE['거래구분']['시장가'], ""]
                )
                if order_success == 0:
                    logger.debug("매도주문 전달 성공")
                    del self.account_stock_dict[sCode]
                else:
                    logger.debug("매도주문 전달 실패")

        for sCode in self.jango_dict.keys():
            asd = self.jango_dict[sCode]
            #meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
            if asd['매매가능수량'] > 0:
                order_success = self.dynamicCall(
                    "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                    ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['보유수량'], 0,
                     self.realType.SENDTYPE['거래구분']['시장가'], ""]
                )
                if order_success == 0:
                    logger.debug("매도주문 전달 성공")
                    del self.account_stock_dict[sCode]
                else:
                    logger.debug("매도주문 전달 실패")
    ###################################################################################################################

    ## CallBack 함수들... ##############################################################################################
    #송수신 메세지 get
    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        logger.debug("func : msg_slot")
        logger.debug("")
        logger.debug("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        logger.debug("func : trdata_slot")
        if sRQName == "예수금상세현황요청":
            logger.debug("func : trdata_slot => 예수금상세현황요청")
            deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            # use_money = float(self.deposit) * self.use_money_percent
            # self.use_money = int(use_money)
            # self.use_money = self.use_money / 4

            output_deposit = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            logger.info("예수금 : %s" % self.output_deposit)

            self.stop_screen_cancel(self.screen_my_info)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            logger.debug("func : trdata_slot => 계좌평가잔고내역요청")
            total_buy_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
            self.total_buy_money = int(total_buy_money)
            total_profit_loss_money = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
            self.total_profit_loss_money = int(total_profit_loss_money)
            total_profit_loss_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
            self.total_profit_loss_rate = float(total_profit_loss_rate)

            logger.info("계좌평가잔고내역요청 싱글데이터 : %s - %s - %s" % (total_buy_money, total_profit_loss_money, total_profit_loss_rate))

            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")  # 출력 : A039423 // 알파벳 A는 장내주식, J는 ELW종목, Q는 ETN종목
                code = code.strip()[1:]

                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")  # 출럭 : 한국기업평가
                stock_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")  # 보유수량 : 000000000000010
                buy_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")  # 매입가 : 000000000054100
                learn_rate = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")  # 수익률 : -000000001.94
                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 현재가 : 000000003450
                total_chegual_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입금액")
                possible_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")
                today_buyquantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"금일매수수량")
                today_sellquantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,"금일매도수량")


                logger.debug("종목코드: %s - 종목명: %s - 보유수량: %s - 매매가능수량: %s - 금일매수수량: %s - 금일매도수량: %s - 매입가:%s - 수익률: %s - 현재가: %s" % (
                    code, code_nm, stock_quantity, possible_quantity, today_buyquantity, today_sellquantity, buy_price, learn_rate, current_price))

                if code in self.account_stock_dict:  # dictionary 에 해당 종목이 있나 확인
                    pass
                else:
                    self.account_stock_dict[code] = {}

                code_nm = code_nm.strip()
                stock_quantity = int(stock_quantity.strip())
                buy_price = int(buy_price.strip())
                learn_rate = float(learn_rate.strip())
                current_price = int(current_price.strip())
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = int(possible_quantity.strip())-int(today_buyquantity.strip())
                today_buyquantity = int(today_buyquantity.strip())
                today_sellquantity = int(today_sellquantity.strip())

                self.account_stock_dict[code].update({"종목명": code_nm})
                self.account_stock_dict[code].update({"보유수량": stock_quantity})
                self.account_stock_dict[code].update({"매입가": buy_price})
                self.account_stock_dict[code].update({"수익률(%)": learn_rate})
                self.account_stock_dict[code].update({"현재가": current_price})
                self.account_stock_dict[code].update({"매입금액": total_chegual_price})
                self.account_stock_dict[code].update({'매매가능수량' : possible_quantity})
                self.account_stock_dict[code].update({'금일매수수량': today_buyquantity})
                self.account_stock_dict[code].update({'금일매도수량': today_sellquantity})
                self.account_stock_dict[code].update({'매도': "가능"})

                tmp = int(float(total_chegual_price) / (float(self.unit_money) * 0.8))
                logger.debug("int(float(total_chegual_price) / (float(self.unit_money) * 0.8))"); logger.info(tmp)
                if tmp == 0:
                    logger.info("trdata_slot: Empty account")
                    self.account_stock_dict[code].update({'매수': "가능"})
                    logger.info(self.account_stock_dict[code])
                    pass
                elif tmp == 1:
                    logger.info("trdata_slot: 1unit account")
                    self.account_stock_dict[code].update({'매수': "불가능"})
                    logger.info(self.account_stock_dict[code])
                    pass
                elif tmp > 4:
                    logger.info("trdata_slot: 4unit account")
                    self.account_stock_dict[code].update({'매수': "불가능"})

                    self.account1_stock_dict[code] = {}
                    self.account1_stock_dict[code].update({"종목명": code_nm})
                    self.account1_stock_dict[code].update({"수익률(%)": learn_rate})
                    self.account1_stock_dict[code].update({'매매가능수량': int(stock_quantity/4)})
                    self.account1_stock_dict[code].update({'매도': "가능"})
                    self.account1_stock_dict[code].update({'매수': "불가능"})

                    self.account2_stock_dict[code] = {}
                    self.account2_stock_dict[code].update({"종목명": code_nm})
                    self.account2_stock_dict[code].update({"수익률(%)": learn_rate})
                    self.account2_stock_dict[code].update({'매매가능수량': int(stock_quantity*2/4)})
                    self.account2_stock_dict[code].update({'매도': "가능"})
                    self.account2_stock_dict[code].update({'매수': "불가능"})

                    logger.info(self.account_stock_dict[code])
                    logger.info(self.account1_stock_dict[code])
                    logger.info(self.account2_stock_dict[code])
                    pass
                else: # 2 or 3
                    logger.info("trdata_slot: 2unit account")
                    self.account_stock_dict[code].update({'매수': "불가능"})

                    #self.account_stock_dict[code].update({'매매가능수량': self.unit_money})
                    self.account1_stock_dict[code] = {}
                    self.account1_stock_dict[code].update({"종목명": code_nm})
                    # self.account1_stock_dict[code].update({"보유수량": stock_quantity})
                    # self.account1_stock_dict[code].update({"매입가": buy_price})
                    self.account1_stock_dict[code].update({"수익률(%)": learn_rate})
                    # self.account1_stock_dict[code].update({"현재가": current_price})
                    # self.account1_stock_dict[code].update({"매입금액": total_chegual_price})
                    self.account1_stock_dict[code].update({'매매가능수량': int(stock_quantity/2)})
                    # self.account1_stock_dict[code].update({'금일매수수량': today_buyquantity})
                    # self.account1_stock_dict[code].update({'금일매도수량': today_sellquantity})
                    self.account1_stock_dict[code].update({'매도': "가능"})
                    self.account1_stock_dict[code].update({'매수': "불가능"})

                    logger.info(self.account_stock_dict[code])
                    logger.info(self.account1_stock_dict[code])
                    pass

                # if float(self.unit_money) * 1.1 < total_chegual_price :
                #     self.account_stock_dict[code].update({'매수': "가능"})
                # else :
                #     self.account_stock_dict[code].update({'매수': "불가능"})
                #
                # if today_buyquantity > 0:  #
                #     self.jango_dict[code] = {}
                #     self.jango_dict[code].update({"현재가": current_price})
                #     self.jango_dict[code].update({"종목코드": code})
                #     self.jango_dict[code].update({"종목명": code_nm})
                #     self.jango_dict[code].update({"보유수량": today_buyquantity})
                #     self.jango_dict[code].update({"주문가능수량": today_buyquantity})
                #     self.jango_dict[code].update({"매입단가": buy_price})
                #     self.jango_dict[code].update({"총매입가": today_buyquantity*buy_price})
                #     self.jango_dict[code].update({"매도매수구분": "1"})
                #     # self.jango_dict[code].update({"(최우선)매도호가": first_sell_price})
                #     # self.jango_dict[code].update({"(최우선)매수호가": first_buy_price})
                #     self.jango_dict[code].update({"매도": "가능"})
                #     self.jango_dict[code].update({"매수": "불가능"})
                #     logger.debug("today_buyquantity !=0")
                #     logger.debug(self.jango_dict)

            logger.info("sPreNext : %s" % sPrevNext)

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")
            else:
                logger.info("계좌에 가지고 있는 종목은 %s " % rows)
                self.detail_account_info_event_loop.exit()


        elif sRQName == "실시간미체결요청":
            logger.debug("func : trdata_slot => 실시간미체결요청")
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            for i in range(rows):
                code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                code_nm = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                order_no = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                order_status = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "주문상태")  # 접수,확인,체결
                order_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                  "주문수량")
                order_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문가격")
                order_gubun = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "주문구분")  # -매도, +매수, -매도정정, +매수정정
                not_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                                "미체결수량")
                ok_quantity = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i,
                                               "체결량")


                code = code.strip()
                code_nm = code_nm.strip()
                order_no = int(order_no.strip())
                order_status = order_status.strip()
                order_quantity = int(order_quantity.strip())
                order_price = int(order_price.strip())
                order_gubun = order_gubun.strip().lstrip('+').lstrip('-')
                not_quantity = int(not_quantity.strip())
                ok_quantity = int(ok_quantity.strip())

                if order_no in self.not_account_stock_dict:
                    pass
                else:
                    self.not_account_stock_dict[order_no] = {}

                self.not_account_stock_dict[order_no].update({'종목코드': code})
                self.not_account_stock_dict[order_no].update({'종목명': code_nm})
                self.not_account_stock_dict[order_no].update({'주문번호': order_no})
                self.not_account_stock_dict[order_no].update({'주문상태': order_status})
                self.not_account_stock_dict[order_no].update({'주문수량': order_quantity})
                self.not_account_stock_dict[order_no].update({'주문가격': order_price})
                self.not_account_stock_dict[order_no].update({'주문구분': order_gubun})
                self.not_account_stock_dict[order_no].update({'미체결수량': not_quantity})
                self.not_account_stock_dict[order_no].update({'체결량': ok_quantity})

                logger.info("미체결 종목 : %s "  % self.not_account_stock_dict[order_no])

            self.detail_account_info_event_loop.exit()


        elif sRQName == "주식일봉차트조회":
            logger.info("func : trdata_slot => 주식일봉차트조회")
            code = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            code = code.strip()
            # data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)
            # [[‘’, ‘현재가’, ‘거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’. ‘’], [‘’, ‘현재가’, ’거래량’, ‘거래대금’, ‘날짜’, ‘시가’, ‘고가’, ‘저가’, ‘’]. […]]

            cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            logger.info("남은 일자 수 %s" % cnt)
            for i in range(cnt):
                data = []

                current_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")  # 출력 : 000070
                value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")  # 출력 : 000070
                trading_value = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")  # 출력 : 000070
                date = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")  # 출력 : 000070
                start_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")  # 출력 : 000070
                high_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")  # 출력 : 000070
                low_price = self.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")  # 출력 : 000070

                data.append("")
                data.append(current_price.strip())
                data.append(value.strip())
                data.append(trading_value.strip())
                data.append(date.strip())
                data.append(start_price.strip())
                data.append(high_price.strip())
                data.append(low_price.strip())
                data.append("")
                self.calcul_data.append(data.copy())

            if sPrevNext == "2":
                self.day_kiwoom_db(code=code, sPrevNext=sPrevNext)
            else:
                logger.debug("총 일수 %s" % len(self.calcul_data))
                # if self.isTradingState == "MakeFile":
                #     logger.debug("func : trdata_slot => 주식일봉차트조회 => MakeFile")
                #     pass_success = False
                #     pass_success = True
                #     if pass_success == True:
                #         logger.debug("조건부 통과됨")
                #         code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                #
                #         f = open("stocklab/kiwoom/files/condition_stock.txt", "a", encoding="utf8")
                #         #f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                #         f.write("%s\t%s\t%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1]),
                #                                           str(int(self.calcul_data[0][6]) - int(self.calcul_data[0][7])),
                #                                           str(min([int(self.calcul_data[0][7]), int(self.calcul_data[1][7])]))))
                #         f.close()
                #     elif pass_success == False:
                #         logger.debug("조건부 통과 못함")
                # elif self.isTradingState == "OnTrading":
                #     logger.debug("func : trdata_slot => 주식일봉차트조회 => OnTrading")
                #     sCode = code; b = int(self.calcul_data[0][1]); j = int(self.calcul_data[0][5]); e = int(b * 1.1)
                #     x=int(int(self.calcul_data[0][6]) - int(self.calcul_data[0][7])*0.5)
                #     logger.debug("코드명 %s 현재가 %s 시가 %s 전고 %s 전저 %s 매수기준 %s"
                #                               %(sCode,b,j,int(self.calcul_data[0][6]),int(self.calcul_data[0][7]),x))
                #     if sCode in self.account_stock_dict.keys() and sCode not in self.jango_dict.keys():
                #         asd = self.account_stock_dict[sCode]
                #         meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
                #
                #         if asd['매매가능수량'] > 0 and (meme_rate > 20 or meme_rate < -7):
                #             logger.debug("func : trdata_slot => 주식일봉차트조회 => OnTrading => account_stock_dict 매도진입")
                #             order_success = self.dynamicCall(
                #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #                 ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode,
                #                  asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                #             )
                #
                #             if order_success == 0:
                #                 logger.debug("매도주문 전달 성공")
                #                 del self.account_stock_dict[sCode]
                #             else:
                #                 logger.debug("매도주문 전달 실패")
                #
                #     elif sCode in self.jango_dict.keys():
                #         jd = self.jango_dict[sCode]
                #         meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100
                #
                #         if jd['주문가능수량'] > 0 and (meme_rate > 20 or meme_rate < -7):
                #             logger.debug("func : trdata_slot => 주식일봉차트조회 => OnTrading => jango_dict 매도진입")
                #             order_success = self.dynamicCall(
                #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #                 ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode,
                #                  jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                #             )
                #
                #             if order_success == 0:
                #                 logger.debug("매도주문 전달 성공")
                #             else:
                #                 logger.debug("매도주문 전달 실패")
                #
                #
                #     elif sCode not in self.jango_dict:
                #         # elif d > 2.0 and sCode not in self.jango_dict:
                #         #if b > (j + self.portfolio_stock_dict[sCode]["매수기준"] * 0.5):
                #         if b > (j + x * 0.5):
                #             logger.debug("func : trdata_slot => 주식일봉차트조회 => OnTrading => 매수콜백진입")
                #             logger.debug("매수조건 통과 %s (현재가)%s (j)%s (고-저)%s (기준)%s" % (
                #             sCode, b, j, self.portfolio_stock_dict[sCode]["매수기준"],
                #             j + self.portfolio_stock_dict[sCode]["매수기준"] * 0.5))
                #
                #             # result = (self.use_money * 0.1) / e
                #             result = (5000000) / b
                #             quantity = int(result)
                #
                #             order_success = self.dynamicCall(
                #                 "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #                 ["신규매수", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 1, sCode, quantity,
                #                  e, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                #             )
                #
                #             if order_success == 0:
                #                 logger.debug("매수주문 전달 성공")
                #             else:
                #                 logger.debug("매수주문 전달 실패")
                #
                #     # not_meme_list = list(self.not_account_stock_dict)
                #     # for order_num in not_meme_list:
                #     #     code = self.not_account_stock_dict[order_num]["종목코드"]
                #     #     meme_price = self.not_account_stock_dict[order_num]['주문가격']
                #     #     not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
                #     #     order_gubun = self.not_account_stock_dict[order_num]['주문구분']
                #     #
                #     #     if order_gubun == "매수" and not_quantity > 0 and e > meme_price:
                #     #         order_success = self.dynamicCall(
                #     #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #     #             ["매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0,
                #     #              self.realType.SENDTYPE['거래구분']['지정가'], order_num]
                #     #         )
                #     #
                #     #         if order_success == 0:
                #     #             logger.debug("매수취소 전달 성공")
                #     #         else:
                #     #             logger.debug("매수취소 전달 실패")
                #     #
                #     #     elif not_quantity == 0:
                #     #         del self.not_account_stock_dict[order_num]
                # # 120일 이평선을 그릴만큼의 데이터가 있는지 체크
                # if self.calcul_data == None or len(self.calcul_data) < 120:
                #     pass_success = False
                #
                # else:
                #
                #     # 120일 이평선의 최근 가격 구함
                #     total_price = 0
                #     for value in self.calcul_data[:120]:
                #         total_price += int(value[1])
                #     moving_average_price = total_price / 120
                #
                #     # 오늘자 주가가 120일 이평선에 걸쳐있는지 확인
                #     bottom_stock_price = False
                #     check_price = None
                #     if int(self.calcul_data[0][7]) <= moving_average_price and moving_average_price <= int(self.calcul_data[0][6]):
                #         self.logging.logger.info("오늘 주가 120이평선 아래에 걸쳐있는 것 확인")
                #         bottom_stock_price = True
                #         check_price = int(self.calcul_data[0][6])
                #
                #
                #     # 과거 일봉 데이터를 조회하면서 120일 이평선보다 주가가 계속 밑에 존재하는지 확인
                #     prev_price = None
                #     if bottom_stock_price == True:
                #
                #         moving_average_price_prev = 0
                #         price_top_moving = False
                #         idx = 1
                #         while True:
                #
                #             if len(self.calcul_data[idx:]) < 120:  # 120일치가 있는지 계속 확인
                #                 self.logging.logger.info("120일치가 없음")
                #                 break
                #
                #             total_price = 0
                #             for value in self.calcul_data[idx:120+idx]:
                #                 total_price += int(value[1])
                #             moving_average_price_prev = total_price / 120
                #
                #             if moving_average_price_prev <= int(self.calcul_data[idx][6]) and idx <= 20:
                #                 self.logging.logger.info("20일 동안 주가가 120일 이평선과 같거나 위에 있으면 조건 통과 못함")
                #                 price_top_moving = False
                #                 break
                #
                #             elif int(self.calcul_data[idx][7]) > moving_average_price_prev and idx > 20:  # 120일 이평선 위에 있는 구간 존재
                #                 self.logging.logger.info("120일치 이평선 위에 있는 구간 확인됨")
                #                 price_top_moving = True
                #                 prev_price = int(self.calcul_data[idx][7])
                #                 break
                #
                #             idx += 1
                #
                #         # 해당부분 이평선이 가장 최근의 이평선 가격보다 낮은지 확인
                #         if price_top_moving == True:
                #             if moving_average_price > moving_average_price_prev and check_price > prev_price:
                #                 self.logging.logger.info("포착된 이평선의 가격이 오늘자 이평선 가격보다 낮은 것 확인")
                #                 self.logging.logger.info("포착된 부분의 저가가 오늘자 주가의 고가보다 낮은지 확인")
                #                 pass_success = True

                # pass_success = True
                # if pass_success == True:
                #     self.logging.logger.info("조건부 통과됨")
                #     code_nm = self.dynamicCall("GetMasterCodeName(QString)", code)
                #     f = open("stocklab/kiwoom/files/condition_stock.txt", "a", encoding="utf8")
                #     #f.write("%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1])))
                #     f.write("%s\t%s\t%s\t%s\t%s\n" % (code, code_nm, str(self.calcul_data[0][1]),
                #                                       str(int(self.calcul_data[0][6]) - int(self.calcul_data[0][7])),
                #                                       str(min([int(self.calcul_data[0][7]), int(self.calcul_data[1][7])]))))
                #     f.close()
                # elif pass_success == False:
                #     self.logging.logger.info("조건부 통과 못함")

                self.calcul_data.clear()
                self.calculator_event_loop.exit()

    # 실시간 데이터 얻어오기
    def realdata_slot(self, sCode, sRealType, sRealData):
        logger.debug("func : realdata_slot")
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분']  # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감)
            value = self.dynamicCall("GetCommRealData(QString, int)", sCode, fid)

            if value == '0':
                logger.info("장 시작 전")
            elif value == '3':
                logger.info("장 시작")
            elif value == "2":
                logger.info("장 종료, 동시호가로 넘어감")
            elif value == "4":
                logger.info("3시30분 장 종료")
                for code in self.portfolio_stock_dict.keys():
                    self.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)
                QTest.qWait(5000)
                # self.file_delete()
                # self.make_ConditionFile()
                exit()

        elif sRealType == "주식체결":

            a = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['체결시간'])  # 출력 HHMMSS
            b = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가'])  # 출력 : +(-)2520
            b = abs(int(b))

            c = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['전일대비'])  # 출력 : +(-)2520
            c = abs(int(c))

            d = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['등락율'])  # 출력 : +(-)12.98
            d = float(d)

            e = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매도호가'])  # 출력 : +(-)2520
            e = abs(int(e))

            f = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['(최우선)매수호가'])  # 출력 : +(-)2515
            f = abs(int(f))

            g = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['거래량'])  # 출력 : +240124  매수일때, -2034 매도일 때
            g = abs(int(g))

            h = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['누적거래량'])  # 출력 : 240124
            h = abs(int(h))

            i = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['고가'])  # 출력 : +(-)2530
            i = abs(int(i))

            j = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['시가'])  # 출력 : +(-)2530
            j = abs(int(j))

            k = self.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['저가'])  # 출력 : +(-)2530
            k = abs(int(k))

            if sCode not in self.portfolio_stock_dict:
                logging.error(" 포트폴리오에 없는종목 %s" % sCode)
                return
                # self.portfolio_stock_dict.update({sCode:{}})

            self.portfolio_stock_dict[sCode].update({"체결시간": a})
            self.portfolio_stock_dict[sCode].update({"현재가": b})
            self.portfolio_stock_dict[sCode].update({"전일대비": c})
            self.portfolio_stock_dict[sCode].update({"등락율": d})
            self.portfolio_stock_dict[sCode].update({"(최우선)매도호가": e})
            self.portfolio_stock_dict[sCode].update({"(최우선)매수호가": f})
            self.portfolio_stock_dict[sCode].update({"거래량": g})
            self.portfolio_stock_dict[sCode].update({"누적거래량": h})
            self.portfolio_stock_dict[sCode].update({"고가": i})
            self.portfolio_stock_dict[sCode].update({"시가": j})
            self.portfolio_stock_dict[sCode].update({"저가": k})

            if sCode in self.account_stock_dict.keys(): # and sCode not in self.jango_dict.keys():
                asd = self.account_stock_dict[sCode]
                psd = self.portfolio_stock_dict[sCode]
                logger.debug("매도콜백")
                logger.debug(asd)

                if asd['매도'] == "가능" and asd['매매가능수량'] > 0 and asd['수익률(%)'] > 30 : # 손익절 매도

                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, int(asd['매매가능수량']/2), 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                    )
                    if order_success == 0:
                        logger.info("매도주문 전달 성공")
                        asd.update({'매도': "불가능"})
                        del self.account_stock_dict[sCode]
                        if sCode not in self.jango_dict :
                            del self.portfolio_stock_dict[sCode]
                    else:
                        logger.info("매도주문 전달 실패")

                if asd['매도'] == "가능" and asd['매매가능수량'] > 0 and (psd['PVOLIC'] < psd['EV3L'] and psd['PVOLIC'] > b) : # 손익절 전액매도

                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                    )
                    if order_success == 0:
                        logger.info("매도주문 전달 성공")
                        asd.update({'매도': "불가능"})
                        del self.account_stock_dict[sCode]
                        if sCode not in self.jango_dict :
                            del self.portfolio_stock_dict[sCode]
                    else:
                        logger.info("매도주문 전달 실패")

                meme_rate = (b - asd['매입가']) / asd['매입가'] * 100
                if asd['매도'] == "가능" and asd['매매가능수량'] > 0 and meme_rate < -15 : # 손절 전액매도
                    order_success = self.dynamicCall(
                        "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                        ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, asd['매매가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                    )
                    if order_success == 0:
                        logger.info("매도주문 전달 성공")
                        asd.update({'매도': "불가능"})
                        del self.account_stock_dict[sCode]
                        if sCode not in self.jango_dict :
                            del self.portfolio_stock_dict[sCode]
                    else:
                        logger.info("매도주문 전달 실패")

                # if asd['매도'] == "가능" and asd['매매가능수량'] > 0 and (asd['EV40'] < b): # 차익실현 => 데이터베이스 활용해야함...
                #     asd.update({'매도': "불가능"})
                #     order_success = self.dynamicCall(
                #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #         ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, int(asd['매매가능수량']/2), 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                #     )
                #     if order_success == 0:
                #         logger.info("매도주문 전달 성공")
                #         del self.account_stock_dict[sCode]
                #     else:
                #         logger.info("매도주문 전달 실패")

            elif sCode in self.jango_dict.keys():
                # jd = self.jango_dict[sCode]
                # meme_rate = (b - jd['매입단가']) / jd['매입단가'] * 100
                #
                # if jd['주문가능수량'] > 0 and (meme_rate > 5 or meme_rate < -5):
                #
                #     order_success = self.dynamicCall(
                #         "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                #         ["신규매도", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 2, sCode, jd['주문가능수량'], 0, self.realType.SENDTYPE['거래구분']['시장가'], ""]
                #     )
                #
                #     if order_success == 0:
                #         logger.info("매도주문 전달 성공")
                #     else:
                #         logger.info("매도주문 전달 실패")
                pass


            elif sCode not in self.jango_dict:
                logger.debug("매수콜백진입: %s" % self.portfolio_stock_dict[sCode]["종목명"])
                #elif d > 2.0 and sCode not in self.jango_dict:
                if sCode not in self.account2_stock_dict:
                    logger.debug("매수콜백진입 %s (현재가)%s (EV10)%s" % (self.portfolio_stock_dict[sCode]["종목명"], b, self.portfolio_stock_dict[sCode]["EV10"]))
                    if self.portfolio_stock_dict[sCode]["매수"] == "가능" and b <  self.portfolio_stock_dict[sCode]["EV10"]:
                        logger.debug("매수조건 통과 %s (현재가)%s (EV10)%s" % (self.portfolio_stock_dict[sCode]["종목명"], b, self.portfolio_stock_dict[sCode]["EV10"]))

                        if sCode not in self.account_stock_dict:
                            result = (self.unit_money * 2) / e
                        else :
                            result = (self.unit_money) / e

                        quantity = int(result)

                        order_success = self.dynamicCall(
                            "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                            ["신규매수", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 1, sCode, quantity, e, self.realType.SENDTYPE['거래구분']['지정가'], ""]
                        )

                        if order_success == 0:
                            logger.info("매수주문 전달 성공")
                            self.portfolio_stock_dict[sCode].update({'매수': "불가능"})
                            logger.info(self.portfolio_stock_dict[sCode])
                        else:
                            logger.info("매수주문 전달 실패")

            # not_meme_list = list(self.not_account_stock_dict)
            # for order_num in not_meme_list:
            #     code = self.not_account_stock_dict[order_num]["종목코드"]
            #     meme_price = self.not_account_stock_dict[order_num]['주문가격']
            #     not_quantity = self.not_account_stock_dict[order_num]['미체결수량']
            #     order_gubun = self.not_account_stock_dict[order_num]['주문구분']
            #
            #
            #     if order_gubun == "매수" and not_quantity > 0 and e > meme_price:
            #         order_success = self.dynamicCall(
            #             "SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
            #             ["매수취소", self.portfolio_stock_dict[sCode]["주문용스크린번호"], self.account_num, 3, code, 0, 0, self.realType.SENDTYPE['거래구분']['지정가'], order_num]
            #         )
            #
            #         if order_success == 0:
            #             logger.debug("매수취소 전달 성공")
            #         else:
            #             logger.debug("매수취소 전달 실패")
            #
            #     elif not_quantity == 0:
            #         del self.not_account_stock_dict[order_num]

    # 실시간 체결 정보
    def chejan_slot(self, sGubun, nItemCnt, sFidList):
        logger.debug("func : chejan_slot")
        if int(sGubun) == 0: #주문체결
            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드'])[1:]
            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명'])
            stock_name = stock_name.strip()

            origin_order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['원주문번호'])  # 출력 : defaluse : "000000"
            order_number = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문번호'])  # 출럭: 0115061 마지막 주문번호

            order_status = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문상태'])  # 출력: 접수, 확인, 체결
            order_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문수량'])  # 출력 : 3
            order_quan = int(order_quan)

            order_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문가격'])  # 출력: 21000
            order_price = int(order_price)

            not_chegual_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['미체결수량'])  # 출력: 15, default: 0
            not_chegual_quan = int(not_chegual_quan)

            order_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문구분'])  # 출력: -매도, +매수
            order_gubun = order_gubun.strip().lstrip('+').lstrip('-')

            chegual_time_str = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간'])  # 출력: '151028'

            chegual_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가'])  # 출력: 2110  default : ''
            if chegual_price == '':
                chegual_price = 0
            else:
                chegual_price = int(chegual_price)

            chegual_quantity = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량'])  # 출력: 5  default : ''
            if chegual_quantity == '':
                chegual_quantity = 0
            else:
                chegual_quantity = int(chegual_quantity)

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['현재가'])  # 출력: -6000
            current_price = abs(int(current_price))

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매도호가'])  # 출력: -6010
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['(최우선)매수호가'])  # 출력: -6000
            first_buy_price = abs(int(first_buy_price))

            ######## 새로 들어온 주문이면 주문번호 할당
            if order_number not in self.not_account_stock_dict.keys():
                self.not_account_stock_dict.update({order_number: {}})

            self.not_account_stock_dict[order_number].update({"종목코드": sCode})
            self.not_account_stock_dict[order_number].update({"주문번호": order_number})
            self.not_account_stock_dict[order_number].update({"종목명": stock_name})
            self.not_account_stock_dict[order_number].update({"주문상태": order_status})
            self.not_account_stock_dict[order_number].update({"주문수량": order_quan})
            self.not_account_stock_dict[order_number].update({"주문가격": order_price})
            self.not_account_stock_dict[order_number].update({"미체결수량": not_chegual_quan})
            self.not_account_stock_dict[order_number].update({"원주문번호": origin_order_number})
            self.not_account_stock_dict[order_number].update({"주문구분": order_gubun})
            self.not_account_stock_dict[order_number].update({"주문/체결시간": chegual_time_str})
            self.not_account_stock_dict[order_number].update({"체결가": chegual_price})
            self.not_account_stock_dict[order_number].update({"체결량": chegual_quantity})
            self.not_account_stock_dict[order_number].update({"현재가": current_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매도호가": first_sell_price})
            self.not_account_stock_dict[order_number].update({"(최우선)매수호가": first_buy_price})

        elif int(sGubun) == 1: #잔고

            account_num = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['계좌번호'])
            sCode = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목코드'])[1:]

            stock_name = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['종목명'])
            stock_name = stock_name.strip()

            current_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['현재가'])
            current_price = abs(int(current_price))

            stock_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['보유수량'])
            stock_quan = int(stock_quan)

            like_quan = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['주문가능수량'])
            like_quan = int(like_quan)

            buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매입단가'])
            buy_price = abs(int(buy_price))

            total_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['총매입가']) # 계좌에 있는 종목의 총매입가
            total_buy_price = int(total_buy_price)

            meme_gubun = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['매도매수구분'])
            meme_gubun = self.realType.REALTYPE['매도수구분'][meme_gubun] # 1: 매수, 0: 매도(?)

            first_sell_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매도호가'])
            first_sell_price = abs(int(first_sell_price))

            first_buy_price = self.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['잔고']['(최우선)매수호가'])
            first_buy_price = abs(int(first_buy_price))

            if sCode not in self.jango_dict.keys():
                self.jango_dict.update({sCode:{}})

            self.jango_dict[sCode].update({"현재가": current_price})
            self.jango_dict[sCode].update({"종목코드": sCode})
            self.jango_dict[sCode].update({"종목명": stock_name})
            self.jango_dict[sCode].update({"보유수량": stock_quan})
            self.jango_dict[sCode].update({"주문가능수량": like_quan})
            self.jango_dict[sCode].update({"매입단가": buy_price})
            self.jango_dict[sCode].update({"총매입가": total_buy_price})
            self.jango_dict[sCode].update({"매도매수구분": meme_gubun})
            self.jango_dict[sCode].update({"(최우선)매도호가": first_sell_price})
            self.jango_dict[sCode].update({"(최우선)매수호가": first_buy_price})

            if stock_quan == 0:
                del self.jango_dict[sCode]
                #self.slack.send_msg(msg=("%s 매도완료"%self.jango_dict[sCode]["종목명"]))
                logger.debug("매도완료")
            else :
                #self.slack.send_msg(msg=("%s 체결 %s주" %(self.jango_dict[sCode]["종목명"],stock_quan)))
                #logger.debug("%s 체결 %s주" %(self.jango_dict[sCode]["종목명"],stock_quan))
                logger.debug("매매체결")

    ##########################################################################################################
    def setupSystemTrading(self):
        try:
            logger.info("setupSystemTrading 시작")
            # self.account_num
            self.block_get_account_info()  # 계좌번호 가져오기
            # self.deposit : 예수금, self.output_deposit :출금가능금액 // self.use_money?
            self.block_detail_account_info()  # 예수금 요청 시그널 포함
            #self.total_buy_money :총매입금액, self.total_profit_loss_money :총평가손익금액, self.total_profit_loss_rate : 총수익률(%)
            # account_stock_dict[종목코드] : 종목명: %s - 보유수량: %s - 매입가:%s - 수익률: %s - 현재가: %s
            self.block_detail_account_mystock()  # 계좌평가잔고내역 요청 시그널 포함
            # not_account_stock_dict[order_no] : 종목코드 종목명 주문번호 주문상태 주문수량 주문가격 주문구분 미체결수량 체결량
            QTimer.singleShot(5000, self.not_concluded_account)  # 5초 뒤에 미체결 종목들 가져오기 실행
            QTest.qWait(10000)
            self.isTradingState = "OnTrading"
            # portfolio_stock_dict[종목명] : 현재가 매수기준 매도기준
            # self.read_code()
            self.read_code_xls()
             # 번호할당 portfolio_stock_dict <- portfolio_stock_dict + account_stock_dict + not_account_stock_dict
            self.screen_number_setting()
            QTest.qWait(5000)

            # soldout = False
            # # while True:
            # t_now = datetime.now()
            # t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            # t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            # t_sell = t_now.replace(hour=15, minute=00, second=0, microsecond=0)
            # t_exit = t_now.replace(hour=15, minute=20, second=0, microsecond=0)
            # today = datetime.today().weekday()
            # if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            #     logger.info("Today is Saturday or Sunday.")
            #     exit()
            # if t_9 < t_now < t_start and soldout == False:
            #     logger.debug("AM 09:00 ~ AM 09:05!")
            #     # logger.debug("Account : %s 체결잔고 : %s 미체결잔고 : %s 포트폴리오 %s"
            #     #                           % (len(self.account_stock_dict), len(self.jango_dict),
            #     #                              len(self.not_account_stock_dict), len(self.portfolio_stock_dict)))
            #     # self.isTradingState = "OnSell"
            #     # soldout = True
            #     # self.sell_all()
            #     pass
            # if t_start < t_now < t_sell:  # AM 09:05 ~ PM 03:00 : 시스템트레이딩
            #     logger.info("AM 09:05 ~ AM 03:00!")
            #     logger.debug("Account : %s 체결잔고 : %s 미체결잔고 : %s 포트폴리오 %s"
            #                               % (len(self.account_stock_dict), len(self.jango_dict),
            #                                  len(self.not_account_stock_dict), len(self.portfolio_stock_dict)))
            #
            #     pass
            # if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            #     logger.info("AM 09:00 ~ AM 09:05!")
            #     # logger.debug("Account : %s 체결잔고 : %s 미체결잔고 : %s 포트폴리오 %s"
            #     #                           % (len(self.account_stock_dict), len(self.jango_dict),
            #     #                              len(self.not_account_stock_dict), len(self.portfolio_stock_dict)))
            #     # self.isTradingState = "OnSell"
            #     # soldout = True
            #     # self.sell_all()
            #     pass
            # if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            #     logger.info("PM 03:20 ~ :프로그램 종료!")
            #     if 0 :
            #         self.isTradingState = "MakeFile"
            #         self.file_delete()
            #         self.make_ConditionFile()
            #     exit()
            # time.sleep(3)

            logger.info('실시간 수신 관련 함수')
            logger.debug(self.portfolio_stock_dict)
            # 실시간 수신 관련 함수
            self.dynamicCall("SetRealReg(QString, QString, QString, QString)", self.screen_start_stop_real, '',
                             self.realType.REALTYPE['장시작시간']['장운영구분'], "0")

            # exit()

            for code in self.portfolio_stock_dict.keys():
                screen_num = self.portfolio_stock_dict[code]['스크린번호']
                fids = self.realType.REALTYPE['주식체결']['체결시간']
                self.dynamicCall("SetRealReg(QString, QString, QString, QString)", screen_num, code, fids, "1")

        except Exception as ex:
            logger.debug('`main -> exception! ' + str(ex) + '`')

    def startSystemTrading(self):
        pass
    ############################################################################################################
class Thread1(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def get_stock_balance(self,code=None):
        return None
    def get_current_cash(self):
        return 0
        pass
    def sell_all(self):
        pass
    def buy_etf(self,code=None):
        pass

    def run(self):
        # self.parent.plain_text_edit.appendPlainText("경주마1이 출발하였습니다.")
        try:
            symbol_list = ['229200']
            bought_list = []  # 매수 완료된 종목 리스트
            target_buy_count = 5  # 매수할 종목 수
            buy_percent = 0.19
            #print('check_creon_system() :', check_creon_system())  # 크레온 접속 점검
            stocks = self.get_stock_balance('ALL')  # 보유한 모든 종목 조회
            # total_cash = int(self.get_current_cash())  # 100% 증거금 주문 가능 금액 조회
            # buy_amount = total_cash * buy_percent  # 종목별 주문 금액 계산
            # print('100% 증거금 주문 가능 금액 :', total_cash)
            # print('종목별 주문 비율 :', buy_percent)
            # print('종목별 주문 금액 :', buy_amount)
            # print('시작 시간 :', datetime.now().strftime('%m/%d %H:%M:%S'))
            # soldout = False
            #
            # while True:
            #     t_now = datetime.now()
            #     t_9 = t_now.replace(hour=9, minute=0, second=0, microsecond=0)
            #     t_start = t_now.replace(hour=9, minute=5, second=0, microsecond=0)
            #     t_sell = t_now.replace(hour=15, minute=15, second=0, microsecond=0)
            #     t_exit = t_now.replace(hour=15, minute=20, second=0, microsecond=0)
            #     today = datetime.today().weekday()
            #     if today == 5 or today == 6:  # 토요일이나 일요일이면 자동 종료
            #         print('Today is', 'Saturday.' if today == 5 else 'Sunday.')
            #         sys.exit(0)
            #     if t_9 < t_now < t_start and soldout == False:
            #         soldout = True
            #         self.sell_all()
            #     if t_start < t_now < t_sell:  # AM 09:05 ~ PM 03:15 : 매수
            #         for sym in symbol_list:
            #             if len(bought_list) < target_buy_count:
            #                 self.buy_etf(sym)
            #                 time.sleep(1)
            #         if t_now.minute == 30 and 0 <= t_now.second <= 5:
            #             self.get_stock_balance('ALL')
            #             time.sleep(5)
            #     if t_sell < t_now < t_exit:  # PM 03:15 ~ PM 03:20 : 일괄 매도
            #         if self.sell_all() == True:
            #             print('`sell_all() returned True -> self-destructed!`')
            #             sys.exit(0)
            #     if t_exit < t_now:  # PM 03:20 ~ :프로그램 종료
            #         print('`self-destructed!`')
            #         sys.exit(0)
            # time.sleep(3)
            while True:
                for i in range(20) :
                    print(i,"test!!!")
                    QTest.qWait(1000)
        except Exception as ex:
            print('`main -> exception! ' + str(ex) + '`')


