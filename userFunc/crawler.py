from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import pyautogui

import telegram
import asyncio

import configparser
from time import sleep
from datetime import date,datetime, timedelta
import os, re
import json

from .meta import apts, officetels, sangaetcs

class Crawler:
    def __init__(self,parent,logger):
        self.parent = parent
        self.logger = logger

        config = configparser.ConfigParser()
        config.read('config/secret.ini')
        self.BOT_TOKEN = config['TGRAM']['BOT_TOKEN']

    def set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        return driver

    def job_start(self, type=1):
        """
        type : 0 -> APT, apts+date().xlsx, 1 -> officetels+date().xlsx, 2 -> sangaetcs+date().xlsx
        return : df
        """
        driver = self.set_chrome_driver()
        df = pd.DataFrame(columns=['제목', '매전월', '금액', '종류', '타입/층/향', '설명', '부동산', '등록일'])
        ###########################################################################################################
        if type == 1:
            items = apts
        elif type == 2:
            items = officetels
        else:
            items = sangaetcs

        cnt1 = 0
        for item in items:
            url = items[item]['http']
            driver.get(url)

            sleep(2)

            if type == 3 :
                iframe = driver.find_element(By.CSS_SELECTOR, 'div.list_contents')
                scroll_origin = ScrollOrigin.from_element(iframe)
                start = datetime.now()
                end = start + timedelta(seconds=10)
                while True:
                    ActionChains(driver) \
                        .scroll_from_origin(scroll_origin, 0, 10000) \
                        .perform()
                    if datetime.now() > end:
                        break
            else:
                total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.list_filter_btn')
                self.logger.debug("전체체크박스 ${len(total_chkbox)}")
                total_chkbox[0].click()

                total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'ul.select_list_wrap--detail>li.select_item')
                self.logger.debug(len(total_chkbox))
                total_chkbox[0].click()

                total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.btn_close_panel')
                self.logger.debug(len(total_chkbox))
                total_chkbox[0].click()

            # 상가 토지 등을 전체로 하고 싶을때 밑에 5줄을 탭으로 한번 밀어넣으면됨 ###########################
            sleep(1)

            total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'a.sorting_type')
            self.logger.debug(len(total_chkbox))
            total_chkbox[1].click()
            #######################################################################################

            sleep(2)

            res = driver.page_source  # 페이지 소스 가져오기
            soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

            sleep(1)

            print("next ############################################### \n")

            titles = driver.find_elements(By.CSS_SELECTOR, 'div.item_title > span.text')
            self.logger.debug("대상 : ${titles[0].text}, 항목수 : ${len(titles)}")
            types = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.type')
            prices = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.price')
            types1 = driver.find_elements(By.CSS_SELECTOR, 'p.line > strong.type')
            specs = driver.find_elements(By.CSS_SELECTOR, 'p.line > span.spec')
            agents = driver.find_elements(By.CSS_SELECTOR, 'span.agent_info')
            rdates = driver.find_elements(By.CSS_SELECTOR, 'em.data')

            dbs = []
            cnt = 0

            for title in titles:
                db = []
                db.append(title.text.strip())
                db.append(types[cnt].text.strip())
                db.append(prices[cnt].text.strip())
                db.append(types1[cnt].text.strip())
                db.append(specs[cnt * 2].text.strip())
                db.append(specs[cnt * 2 + 1].text.strip())
                db.append(agents[cnt * 2 + 1].text.strip())
                db.append(rdates[cnt].text.strip())
                dbs.append(db)

                for cc in dbs:
                    self.parent.pteLog.appendPlainText(str(cc))

                df.loc[cnt1] = db
                cnt += 1
                cnt1 += 1
        return df

    def job_start_full(self, type=1):
        """
        type : 0 -> APT, apts+date().xlsx, 1 -> officetels+date().xlsx, 2 -> sangaetcs+date().xlsx
        return : df
        """
        driver = self.set_chrome_driver()
        # df = pd.DataFrame(columns=['제목', '매전월', '금액', '종류', '타입/층/향', '설명', '부동산', '등록일'])
        df = pd.DataFrame(columns=['제목', '매전월', '금액', '월세', '전환가', '종류', '타입/층/향', '설명', '부동산', '등록일'])
        df_new = pd.DataFrame(columns=['제목', '매전월', '금액', '월세', '전환가', '종류', '타입/층/향', '설명', '부동산', '등록일'])
        ###########################################################################################################
        today = date.today()  # 230503
        scroll_time = 3
        if type == 1:
            items = apts
        elif type == 2:
            items = officetels
        else:
            items = sangaetcs
            scroll_time = 10

        dbs = []
        cnt1 = 0
        cnt2 = 0
        for item in items:
            url = items[item]['http']
            driver.get(url)

            sleep(2)

            if type != 3 :
                total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.list_filter_btn')
                self.logger.debug("전체체크박스 ${len(total_chkbox)}")
                total_chkbox[0].click()

                total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'ul.select_list_wrap--detail>li.select_item')
                self.logger.debug(len(total_chkbox))
                total_chkbox[0].click()

                total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.btn_close_panel')
                self.logger.debug(len(total_chkbox))
                total_chkbox[0].click()

                sleep(1)

            total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'a.sorting_type')
            self.logger.debug(len(total_chkbox))
            total_chkbox[1].click()

            sleep(2)

            #######################################################################################
            iframe = driver.find_element(By.CSS_SELECTOR, 'div.item_area')
            scroll_origin = ScrollOrigin.from_element(iframe)
            start = datetime.now()
            end = start + timedelta(seconds=scroll_time)
            scroll_length = 10000
            while True:
                ActionChains(driver) \
                    .scroll_from_origin(scroll_origin, 0, scroll_length) \
                    .perform()
                if datetime.now() > end:
                    break
                else:
                    scroll_length += 10000
                    sleep(0.2)

            res = driver.page_source  # 페이지 소스 가져오기
            soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

            sleep(1)

            print("next ############################################### \n")

            titles = driver.find_elements(By.CSS_SELECTOR, 'div.item_title > span.text')
            self.logger.debug("대상 : ${titles[0].text}, 항목수 : ${len(titles)}")
            types = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.type')
            prices = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.price')
            types1 = driver.find_elements(By.CSS_SELECTOR, 'p.line > strong.type')
            specs = driver.find_elements(By.CSS_SELECTOR, 'p.line > span.spec')
            agents = driver.find_elements(By.CSS_SELECTOR, 'span.agent_info')
            rdates = driver.find_elements(By.CSS_SELECTOR, 'em.data')

            cnt = 0

            for title in titles:
                db = []
                db.append(title.text.strip())
                db.append(types[cnt].text.strip())

                price = ["0", "0"]
                ldatas = prices[cnt].text.strip().replace(" ", "").replace(",", "").split("/")
                # print(ldatas)
                if len(ldatas) != 2:
                    price[0] = ldatas[0]
                    price[1] = "0"
                else:
                    price[0] = ldatas[0]
                    price[1] = ldatas[1]
                # print("price1:{}, price2:{}".format(price[0], price[1]))
                ldatas = price[0].split("억")
                if len(ldatas) == 2:
                    if ldatas[1] == "":
                        price[0] = ldatas[0] + "0000"
                    else:
                        price[0] = ldatas[0] + ldatas[1]
                else:
                    price[0] = ldatas[0]
                print("price1:{}, price2:{}".format(price[0], price[1]))
                isdigit = True
                if price[0].isdigit():
                    db.append(price[0])
                else:
                    db.append(price[0])
                    isdigit = False
                if price[1].isdigit():
                    db.append(price[1])
                else:
                    db.append(price[1])
                    isdigit = False
                if isdigit:
                    db.append(str(int(price[1]) * 100 + int(price[0])))
                else:
                    db.append("None")

                db.append(types1[cnt].text.strip())
                db.append(specs[cnt * 2].text.strip())
                db.append(specs[cnt * 2 + 1].text.strip())
                db.append(agents[cnt * 2 + 1].text.strip())
                # db.append(rdates[cnt].text.strip())
                # 230503 kbs #####################################
                sdates = rdates[cnt].text.strip()[:-1].split('.')
                rdate = date(int("20" + sdates[0]), int(sdates[1]), int(sdates[2]))
                print(today, rdate)
                db.append(str(rdate))
                if today == rdate:
                    msg = "\n".join(db)
                    print("오늘 == 등록일 \n {}".format(msg))
                    # self.telegram_msg(msg)
                    dbs.append(msg)
                    cnt2 += 1
                ##################################################
                # dbs.append(db)

                for cc in dbs:
                    self.parent.pteLog.appendPlainText(str(cc))

                df.loc[cnt1] = db
                cnt += 1
                cnt1 += 1

        msg = "\n%%%%%\n".join(dbs)
        # print("오늘 == 등록일 \n {}".format(msg))
        self.telegram_msg(msg)

        return df

    async def botAsynMain(self,msg):
        bot = telegram.Bot(token=self.BOT_TOKEN)
        await bot.send_message(chat_id=-1001859218840, text=msg)
    def telegram_msg(self,msg):
        # self.logger.debug("telegram_msg : {}".format(msg))
        asyncio.run(self.botAsynMain('{} {}'.format("새로운물건", msg)))
        pass
    ###################################################################################################
