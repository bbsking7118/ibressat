import os, re
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from time import sleep
import pandas as pd
import pyautogui
import requests
import json

def tester(pt, logger, *args,**kwargs):
    logger.debug("bsFunc(test_function) start...")

    pt.pteLog.clear()
    file = pt.dbfile + "_apt_" + datetime.today().strftime("%Y%m%d") + ".xlsx"
    logger.debug("file({}) exist ...".format(file))
    mdf = pd.DataFrame()
    if os.path.exists(file):
        logger.debug("file({}) exist ...".format(file))
        df = pd.read_excel(file)
        mdf = pd.concat([mdf, df], ignore_index=True)
    else :
        logger.error("file({}) not exist !!! ...".format(file))
    print(mdf)


def localtester():
    file = "c:/temp/dbfile" + "_apt_" + datetime.today().strftime("%Y%m%d") + ".xlsx"
    mdf = pd.DataFrame()
    if os.path.exists(file):
        print("file({}) exist ...".format(file))
        df = pd.read_excel(file)
        mdf = pd.concat([mdf, df], ignore_index=True)
    else:
        print("file({}) not exist !!! ...".format(file))
    # print(mdf)

    df = mdf[:100]
    for i in range(df["등록일"].size):
        sdates = df.iloc[i]["등록일"][:-1].split(".")
        rdata = date(int("20" + sdates[0]), int(sdates[1]), int(sdates[2]))
        if (date.today() - rdata)>timedelta(days=20):
            print("i:{} val:{}".format(i,rdata))

def test_requests():
    url = "http://www.naver.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    timeout = 5
    res = requests.post(url, headers=headers, timeout=timeout)

    # data = {'key1': val1 'key2': val2'}
    # files = [('image', (image.png, open(image.png, 'rb'), 'image/png', {'Expires': '0'}))]
    # headers = {'Authorization': token}
    # res = requests.post(url, headers=headers, files=files, data=data)

    # res = requests.get(url)
    # res = requests.post(url)
    # res = requests.delete(url, data={'key': 'value'})
    # res = requests.head(url)
    # res = requests.options(url)

headers = {'User-Agent': 'Mozilla/5.0'}
timeout = 5

def get_stock(symbol):
      url = 'https://ac.finance.naver.com/ac?q=%s&q_enc=euc-kr&t_koreng=1&st=111&r_lt=111' % symbol
      return requests.post(url,headers=headers, timeout=timeout)

if __name__ == "__main__":
    r = get_stock("ACTC")
    print(r.status_code)
    print(r.headers)
    print("\n==========TEXT")
    print("text - %s " % r.text[:100])  # UTF-8로 인코딩된 문자열
    print("type - %s " % type(r.text))
    print("\n==========CONTENT")
    print("type - %s" % type(r.content))
    print("content -  %s" % r.content[:100])
    print("\n==========JSON")
    print("type - %s" % type(r.json()))
    print("text - %s " % r.json()['query'])
    print("\n==========EnCoding")
    print("encoding - %s" % r.encoding)
    r.encoding = 'ISO-8859-1'
    print("\nencoding - %s" % r.encoding)