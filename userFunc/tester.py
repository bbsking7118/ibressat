import os, re
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from time import sleep
import pandas as pd
import pyautogui

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
    #     # print(datetime.date(df.iloc[i]["등록일"][:-1]))
    #
    # sdate = "23.04.05."
    # sdates = [ int(x) for x in sdate[:-1].split(".") ]
    # sdates = sdate[:-1].split(".")
    # rdata = date(int("20"+sdates[0]),int(sdates[1]),int(sdates[2]))
    # today = date.today()
    # # rdata = date(2023,4,29)
    # ttime = timedelta(days=20)
    # ndate = today - rdata
    # print(today)
    # print(rdata)
    # print(today-rdata)
    # print(ndate)




if __name__ == "__main__":
    localtester()
    # test1()