import sqlite3

conn = sqlite3.connect("test.db")
cursor = conn.cursor()

# 关键一步：把以前的表删了，防止报错
cursor.execute("DROP TABLE IF EXISTS stock_price")

cursor.execute("""
CREATE TABLE stock_price(
    code TEXT,
    price REAL)
""")

cursor.execute("INSERT INTO stock_price (code, price) VALUES ('000001', 11.5)")
cursor.execute("INSERT INTO stock_price (code, price) VALUES ('600519', 1335.0)")
conn.commit()

# 查价格最高的那 1 条
cursor.execute("SELECT code, price FROM stock_price ORDER BY price DESC LIMIT 1")
results = cursor.fetchall()

print("查询到的数据是：")
for row in results:
    print(row)