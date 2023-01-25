from pykiwoom.kiwoom import *
import datetime
import time

# 로그인
kiwoom = Kiwoom()
kiwoom.CommConnect()

# 전종목 종목코드
kospi = kiwoom.GetCodeListByMarket('0')
kosdaq = kiwoom.GetCodeListByMarket('10')
codes = kospi + kosdaq

# 문자열로 오늘 날짜 얻기
now = datetime.datetime.now()
today = now.strftime("%Y%m%d")
aPath = "E:/work/Python/pykiwoom/analysys/xls/"

if 1 :
    # 전 종목의 일봉 데이터
    for i, code in enumerate(codes):
        print(f"{i}/{len(codes)} {code}")
        df = kiwoom.block_request("opt10083",
                                  종목코드=code,
                                  기준일자=today,
                                  끝일자="",
                                  수정주가구분=1,
                                  output="주식월봉차트조회",
                                  next=0)

        out_name = f"{aPath}{code}.xlsx"
        df.to_excel(out_name)
        time.sleep(3.6)
else :
    code = "005930"
    df = kiwoom.block_request("opt10083",
                              종목코드=code,
                              기준일자=today,
                              끝일자="",
                              수정주가구분=1,
                              output="주식월봉차트조회",
                              next=0)

    out_name = f"{aPath}{code}.xlsx"
    df.to_excel(out_name)
    time.sleep(3.6)
