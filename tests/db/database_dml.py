import sqlite3 as sql

con = sql.connect("currency.db")
cursor = con.cursor()

query = """
INSERT INTO currency (name, base_ratio, cache_buy_price, cache_sell_price, remittance_send, remittance_receive, us_exchange_ratio) 
VALUES ("미국 USD", 1107.0, 1234.0, 4567.0, 1118.9, 1230.0, 1.0)
"""
cursor.execute(query)
con.commit()


# query = """
# UPDATE currency SET base_ratio=9999.9 WHERE idx=1
# """

# query = "DELETE FROM currency WHERE name='미국 USD'"

query = """
SELECT idx, name
FROM currency WHERE idx=2
"""
cursor.execute(query)
rows = cursor.fetchall()

for row in rows:
    print(row)
# con.commit()