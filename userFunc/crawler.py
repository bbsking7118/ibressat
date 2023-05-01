from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import pyautogui

from time import sleep
import datetime
import os, re
import json

from .meta import apts, officetels, sangaetcs

class Crawler:
    def __init__(self,parent,logger):
        self.parent = parent
        self.logger = logger

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
                start = datetime.datetime.now()
                end = start + datetime.timedelta(seconds=10)
                while True:
                    ActionChains(driver) \
                        .scroll_from_origin(scroll_origin, 0, 10000) \
                        .perform()
                    if datetime.datetime.now() > end:
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

        ########################################################################################
        # for oftel in oftels:
        #     url = oftels[oftel]['http']
        #     driver.get(url)
        #
        #     sleep(2)
        #
        #     methods = driver.find_elements(By.CSS_SELECTOR, 'button.list_filter_btn')
        #     print(len(methods))
        #     methods[0].click()
        #
        #     total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'ul.select_list_wrap--detail>li.select_item')
        #     print(len(total_chkbox))
        #     total_chkbox[0].click()
        #
        #     total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.btn_close_panel')
        #     print(len(total_chkbox))
        #     total_chkbox[0].click()
        #
        #     # # sleep(2)
        #     # pyautogui.moveTo(100, 750)
        #     sleep(2)
        #
        #     iframe = driver.find_element(By.CSS_SELECTOR, 'div.item_title > span.text')
        #     scroll_origin = ScrollOrigin.from_element(iframe)
        #     start = datetime.datetime.now()
        #     end = start + datetime.timedelta(seconds=10)
        #     while True:
        #         ActionChains(driver) \
        #             .scroll_from_origin(scroll_origin, 0, 100) \
        #             .perform()
        #         if datetime.datetime.now() > end:
        #             break
        #
        #     sleep(2)
        #
        #     res = driver.page_source  # 페이지 소스 가져오기
        #     soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다
        #
        #     sleep(1)
        #
        #     print("next ############################################### \n")
        #
        #     titles = driver.find_elements(By.CSS_SELECTOR, 'div.item_title > span.text')
        #     types = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.type')
        #     prices = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.price')
        #     types1 = driver.find_elements(By.CSS_SELECTOR, 'p.line > strong.type')
        #     specs = driver.find_elements(By.CSS_SELECTOR, 'p.line > span.spec')
        #     agents = driver.find_elements(By.CSS_SELECTOR, 'span.agent_info')
        #     rdates = driver.find_elements(By.CSS_SELECTOR, 'em.data')
        #
        #     dbs = []
        #     cnt = 0
        #
        #     for title in titles:
        #         db = []
        #         db.append(title.text.strip())
        #         db.append(types[cnt].text.strip())
        #         db.append(prices[cnt].text.strip())
        #         db.append(types1[cnt].text.strip())
        #         db.append(specs[cnt * 2].text.strip())
        #         db.append(specs[cnt * 2 + 1].text.strip())
        #         db.append(agents[cnt * 2 + 1].text.strip())
        #         db.append(rdates[cnt].text.strip())
        #         dbs.append(db)
        #         ofisteldf.loc[cnt1] = db
        #         cnt += 1
        #         cnt1 += 1
        #
        # ofisteldf.to_excel("c:/temp/officetel.xlsx")
        #
        ########################################################################################
        # for sangetc in sangetcs:
        #     url = apts[sangetc]['http']
        #     driver.get(url)
        #
        #     iframe = driver.find_element(By.CSS_SELECTOR, 'div.list_contents')
        #     scroll_origin = ScrollOrigin.from_element(iframe)
        #     start = datetime.datetime.now()
        #     end = start + datetime.timedelta(seconds=10)
        #     while True:
        #         ActionChains(driver) \
        #             .scroll_from_origin(scroll_origin, 0, 10000) \
        #             .perform()
        #         if datetime.datetime.now() > end:
        #             break
        #
        #     sleep(3)
        #
        #     res = driver.page_source  # 페이지 소스 가져오기
        #     soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다
        #
        #     sleep(1)
        #
        #     print("next ############################################### \n")
        #
        #     titles = driver.find_elements(By.CSS_SELECTOR, 'div.item_title > span.text')
        #     types = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.type')
        #     prices = driver.find_elements(By.CSS_SELECTOR, 'div.price_line > span.price')
        #     types1 = driver.find_elements(By.CSS_SELECTOR, 'p.line > strong.type')
        #     specs = driver.find_elements(By.CSS_SELECTOR, 'p.line > span.spec')
        #     agents = driver.find_elements(By.CSS_SELECTOR, 'span.agent_info')
        #     rdates = driver.find_elements(By.CSS_SELECTOR, 'em.data')
        #
        #     dbs = []
        #     cnt = 0
        #     cnt1 = 0
        #     for title in titles:
        #         db = []
        #         db.append(title.text.strip())
        #         db.append(types[cnt].text.strip())
        #         db.append(prices[cnt].text.strip())
        #         db.append(types1[cnt].text.strip())
        #         db.append(specs[cnt * 2].text.strip())
        #         db.append(specs[cnt * 2 + 1].text.strip())
        #         db.append(agents[cnt * 2 + 1].text.strip())
        #         db.append(rdates[cnt].text.strip())
        #         dbs.append(db)
        #         sanggaetcdf.loc[cnt1] = db
        #         cnt += 1
        #         cnt1 += 1
        # sanggaetcdf.to_excel("c:/temp/sanggaetc.xlsx")