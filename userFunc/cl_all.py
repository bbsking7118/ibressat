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


# from .meta import apts, oftels, sangetcs
apts = {
    '아미현대7차': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/10581?ms=37.2570329,127.4938572,17&a=PRE:APT&b=A1&e=RETAIL',
    },
    '현대성우오스타1단지': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/100598?ms=37.2551799,127.4935461,17&a=PRE:APT&b=A1&e=RETAIL',
    },
    '현대성우오스타2단지': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/100599?ms=37.2539075,127.4948336,17&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천신일해피트리트리빌1단지(주상복합)': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/106934?ms=37.2541759,127.4928541,18&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천신일해피트리트리빌2단지(주상복합)': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/106935?ms=37.2538172,127.492621,18&a=PRE:APT&b=A1&e=RETAIL',
    },
    '현대성우오스타3단지': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/100600?ms=37.2495959,127.49467,18&a=PRE:APT&b=A1&e=RETAIL',
    },
    '현대성우오스타4단지': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/100601?ms=37.2495959,127.49467,18&a=PRE:APT&b=A1&e=RETAIL',
    },
    '사동현대5차': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/10747?ms=37.248302,127.495598,17&a=PRE:APT&b=A1&e=RETAIL',
    },
    '사동현대6차': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/11816?ms=37.248302,127.495598,17&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천현대3차': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/11818?ms=37.248302,127.495598,17&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천사동신원아침도시': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/114117?ms=37.2461242,127.4962632,16&a=PRE:APT&b=A1&e=RETAIL',
    },
    '현대전자사원(아이파크)': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/11817?ms=37.2461071,127.4894397,16&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이화1,2차': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/25105?ms=37.2397527,127.5172703,16&a=PRE:APT&b=A1&e=RETAIL',
    },
    '다솜마을주은': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/101757?ms=37.2397527,127.5172703,16&a=PRE:APT&b=A1&e=RETAIL',
    },
    # }
    #
    # oftels = {
    # 오피스텔 시작
    '이천클래시아테라스파크': {
        'code': 'o3101',
        'http': 'https://new.land.naver.com/complexes/123254?ms=37.252349,127.4930259,18&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '이천삼성홈프레스티지':{
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/133614?ms=37.252349,127.4930259,18&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '이천아미리슈빌S':{
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/112487?ms=37.2527162,127.4931225,18&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '리치타운': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/119755?ms=37.2527162,127.4928599,18&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '리치타운(주상복합)': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/119756?ms=37.2530373,127.4911698,19&a=PRE:APT&b=A1&e=RETAIL',
    },
    '지평더웰아이': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/119764?ms=37.2529634,127.4918995,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '지평더웰아이(도시형)': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/119763?ms=37.2530373,127.4911698,19&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천하이클래스': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/117334?ms=37.2531734,127.4918995,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '이천하이클래스(주상복합)': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/117333?ms=37.2537525,127.490982,19&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천신일해피트리앤': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/104688?ms=37.2531734,127.491403,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '이천신일해피트리앤(주상복합)': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/104689?ms=37.2537525,127.490982,19&a=PRE:APT&b=A1&e=RETAIL',
    },
    '이천신일해피트리트리빌2단지': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/106937?ms=37.2535024,127.492036,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '이천신일해피트리트리빌1단지': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/106936?ms=37.2541576,127.4913923,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '미지프라자': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/132814?ms=37.2536772,127.4909953,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
    '쁘띠안': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/complexes/113424?ms=37.2534403,127.4916686,19&a=PRE:OPST&b=A1&e=RETAIL',
    },
}

sangetcs = {
    '전부': {
        'code': 'o3105',
        'http': 'https://new.land.naver.com/offices?ms=37.2397527,127.5172703,16&a=SG:SMS:GJCG:APTHGJ:GM:TJ&e=RETAIL',
    },
}

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


driver = set_chrome_driver()
aptdf = pd.DataFrame(columns=['제목', '매전월', '금액', '종류', '타입/층/향', '설명', '부동산', '등록일'])
ofisteldf = pd.DataFrame(columns=['제목', '매전월', '금액', '종류', '타입/층/향', '설명', '부동산', '등록일'])
sanggaetcdf = pd.DataFrame(columns=['제목', '매전월', '금액', '종류', '타입/층/향', '설명', '부동산', '등록일'])
cnt1 = 0
###########################################################################################################
for apt in apts:
    url = apts[apt]['http']
    driver.get(url)

    sleep(2)

    total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.list_filter_btn')
    print(len(total_chkbox))
    total_chkbox[0].click()

    total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'ul.select_list_wrap--detail>li.select_item')
    print(len(total_chkbox))
    total_chkbox[0].click()

    total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'button.btn_close_panel')
    print(len(total_chkbox))
    total_chkbox[0].click()

    sleep(1)

    total_chkbox = driver.find_elements(By.CSS_SELECTOR, 'a.sorting_type')
    print(len(total_chkbox))
    total_chkbox[1].click()

    sleep(2)

    res = driver.page_source  # 페이지 소스 가져오기
    soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

    sleep(1)

    print("next ############################################### \n")

    titles = driver.find_elements(By.CSS_SELECTOR, 'div.item_title > span.text')
    print(len(titles))
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
        aptdf.loc[cnt1] = db
        cnt += 1
        cnt1 += 1

aptdf.to_excel("c:/temp/apt.xlsx")

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