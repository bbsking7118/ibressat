from os import close
import requests
from bs4 import BeautifulSoup
import sqlite3 as sql


def get_exchange_info():
    url = "https://finance.naver.com/marketindex/exchangeList.nhn"
    r = requests.get(url)
    bs = BeautifulSoup(r.text, "lxml")
    EXCHANGE_LIST = []
    trs = bs.select("table.tbl_exchange > tbody > tr")
    for tr in trs:
        tds = tr.select("td")
        if len(tds) == 7:
            name = tds[0].text.strip()
            base_ratio = float(tds[1].text.strip().replace(",", ""))
            cache_buy_price = float(tds[2].text.strip().replace(",", ""))
            cache_sell_price = float(tds[3].text.strip().replace(",", ""))
            remittance_send = float(tds[4].text.strip().replace(",", ""))
            remittance_receive = float(tds[5].text.strip().replace(",", ""))
            us_exchange_info = float(tds[6].text.strip().replace(",", ""))
            EXCHANGE_LIST.append({
                "name": name,
                "base_ratio": base_ratio,
                "cache_buy_price": cache_buy_price,
                "cache_sell_price": cache_sell_price,
                "remittance_send": remittance_send,
                "remittance_receive": remittance_receive,
                "us_exchange_info": us_exchange_info
            })
    return EXCHANGE_LIST


def insert_data():
    exchange_list = get_exchange_info()

    con = sql.connect("currency.db")
    cursor = con.cursor()

    query = "DELETE FROM currency"
    cursor.execute(query)
    con.commit()

    for e in exchange_list:
        query = """
        INSERT INTO currency (name, base_ratio, cache_buy_price, cache_sell_price, remittance_send, remittance_receive, us_exchange_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (e.get("name"), e.get("base_ratio"), e.get("cache_buy_price"), e.get("cache_sell_price"), e.get("remittance_send"), e.get("remittance_receive"), e.get("us_exchange_info")))

    con.commit()
    con.close()

con = sql.connect("currency.db")
cursor = con.cursor()
query = "SELECT * FROM currency"
cursor.execute(query)
rows = cursor.fetchall()

for r in rows:
    print(r)
con.close()
