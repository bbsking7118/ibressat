import sqlite3 as sql
from sqlite3.dbapi2 import SQLITE_SELECT, connect

con = sql.connect("currency.db")

query = """
CREATE TABLE IF NOT EXISTS currency (
    "idx" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
    "base_ratio" FLOAT DEFAULT 0.0,
    "cache_buy_price" FLOAT,
    "cache_sell_price" FLOAT,
    "remittance_send" FLOAT,
    "remittance_receive" FLOAT,
    "us_exchange_ratio" FLOAT
)
"""
con.execute(query)
con.close()
