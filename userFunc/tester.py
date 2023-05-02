import os, re
from datetime import date, datetime, timedelta
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
    prices = ["1억 8,000", "2억", "3억 2000/100", "1,000/85","","이상데이타"]
    print(prices)

    for item in prices:
        # price = item.replace(" ","").replace(",","").replace("억","").split("/")
        # print("size:{} price:{}".format(len(price), price))
        # if len(price) == 1:
        #     price.append("0")
        # print("price1:{}, price2:{}".format(price[0], price[1]))
        price = ["0","0"]
        ldatas = item.replace(" ", "").replace(",", "").split("/")
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
                price[0] = ldatas[0]+"0000"
            else:
                price[0] = ldatas[0] + ldatas[1]
        else:
            price[0] = ldatas[0]
        print("price1:{}, price2:{}".format(price[0], price[1]))

    # def test1():
    #     data = ["1억 8,000", "2억", "3억 2000", "1,000"]
    #     result = []
    #
    #     for d in data:
    #         d = d.replace(",", "")  # remove comma
    #         unit = 1  # default unit is 1 (for 1 digit)
    #         if "억" in d:
    #             unit = 100000000  # update unit for billion
    #         elif "만" in d:
    #             unit = 10000  # update unit for ten thousand
    #         num = int("".join(filter(str.isdigit, d)))  # extract digits
    #         result.append(str(num * unit))
    #
    #     print(result)


if __name__ == "__main__":
    localtester()
    # test1()