import pandas as pd
from pykiwoom.kiwoom import *
import time

aPath = "E:/work/Python/pykiwoom/analysys/input/"
df = pd.read_excel(aPath+"memelist.xlsx")
df.columns = ["종목코드", "종목명", "기타1", "기타2"]

# 종목명 추가하기
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)
codes = df["종목코드"]
# names = [kiwoom.GetMasterCodeName(code[1:]) for code in codes]
# df['종목명'] = pd.Series(data=names)
# print(df['종목명'])

if 0 :
    # 매수하기
    accounts = kiwoom.GetLoginInfo('ACCNO')
    print(accounts)
    account = 8029900811 # accounts[1]

    for code in codes:
        ret = kiwoom.SendOrder("시장가매수", "0101", account, 1, code[1:], 100, 0, "03", "")
        time.sleep(0.2)
        print(code, "종목 시장가 주문 완료")
else :
    accounts = kiwoom.GetLoginInfo('ACCNO')
    print(accounts)
    account = 8029900811

    for code in codes:
        print(code[1:])

