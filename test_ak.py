# import akshare as ak
# import pandas as pd
# df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260901", end_date="20261023", adjust="qfq")
# print("--- 数据长这样 ---")
# print(df.head())
# print("--- 列名长这样 ---")
# print(df.columns)
# import akshare as ak
# import pandas as pd
# import time
# import random 
# max_retries = 3
# df = None
# for i in range(max_retries):
#     try:
#         print(f"正在尝试第 {i+1} 次拉取数据...")
#         df = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20260901", end_date="20261023", adjust="qfq")
#         print("拉取成功！")
#         sleep_time = random.uniform(3, 5)
#         print(f"为了防封 IP，程序随机休息 {sleep_time:.2f} 秒...")
#         time.sleep(sleep_time)
#         break 
#     except Exception as e:
#         print(f"第 {i+1} 次拉取失败，报错: {e}")
#         if i < max_retries - 1:
#             print("等待 3 秒后重试...")
#             time.sleep(3)
#         else:
#             print("重试次数用完，彻底失败。")
# if df is not None:
#     df = df[["日期", "股票代码", "开盘", "收盘", "最高", "最低", "成交量"]]
#     df.columns = ["trade_date", "ts_code", "open", "close", "high", "low", "vol"]
#     df["ts_code"] = df["ts_code"] + ".SZ"
#     df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
#     df = df[df["vol"] > 0]
#     print("--- 清洗后的数据长这样 ---")
#     print(df.head())
# import efinance as ef
# import pandas as pd
# import time
# print("正在从新浪/腾讯拉取数据...")
# df = ef.stock.get_quote_history("000001", klt=101)
# time.sleep(2) 
# print("--- 原始数据长这样 ---")
# print(df.head())
# print("--- 列名长这样 ---")
# print(df.columns)
# import akshare as ak
# import pandas as pd
# import time
# print("正在从腾讯财经拉取数据...")
# # 换成新浪/腾讯接口的日线数据 (qfq 表示前复权)
# # 注意，akshare 腾讯接口的 symbol 参数格式通常是 "sz000001" (带交易所前缀)
# df = ak.stock_zh_a_daily(symbol="sz000001", start_date="20260901", end_date="20261023", adjust="qfq")
# print("--- 拉取成功，原始数据长这样 ---")
# print(df.head())
# print("--- 列名长这样 ---")
# print(df.columns)
# import akshare as ak
# import pandas as pd
# import sqlite3
# import time
# print("正在从腾讯财经拉取数据...")
# df = ak.stock_zh_a_daily(symbol="sz000001", start_date="20260901", end_date="20261023", adjust="qfq")
# time.sleep(2)
# df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
# df.columns = ['trade_date', 'open', 'high', 'low', 'close', 'vol']
# df['ts_code'] = '000001.SZ'
# df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
# df = df[df['vol'] > 0]
# print("--- 清洗完毕的数据 ---")
# print(df.head())
# print("\n准备存入数据库...")
# conn = sqlite3.connect("quant.db")
# cursor = conn.cursor()
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS daily_price (
#     ts_code TEXT,
#     trade_date TEXT,
#     open REAL,
#     high REAL,
#     low REAL,
#     close REAL,
#     vol REAL
# )
# """)
# df.to_sql('daily_price', conn, if_exists='append', index=False)
# conn.commit()
# conn.close()
# print("数据入库成功！你终于写出真正的数据管道了！")
# import akshare as ak
# import pandas as pd
# import sqlite3
# import time
# import random
# codes=["sz000001","sh600519","sz300750"]
# all_df=[]
# for code in codes:
#     print(f"正在拉取{code}")
#     try:
#         df=ak.stock_zh_a_daily(symbol=code,start_date="20260901",end_date="20261023",adjust="qfq")
#         df=df[["date","open","high","low","close","volume"]]
#         df.columns=["trade_date","open","high","low","close","vol"]
#         exchange=code[:2].upper()
#         stock_num=code[2:]
#         df["ts_code"]=stock_num+"."+exchange
#         df["trade_date"]=pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
#         df=df[df["vol"]>0]
#         all_df.append(df)
#         sleep_time=random.uniform(2,4)
#         print(f"  拉取成功，休息 {sleep_time:.2f} 秒...")
#         time.sleep(sleep_time)
#     except Exception as e:
#         print(f"  {code} 拉取失败: {e}")
# if all_df:
#     final_df=pd.concat(all_df,ignore_index=True)
#     print(f"\n准备入库，总共 {len(final_df)} 行数据...")
#     conn=sqlite3.connect("quant.db")
#     final_df.to_sql("daily_price",conn,if_exists="append",index=False)
#     conn.close()
#     print("三只股票全部入库成功！")
import akshare as ak
import pandas as pd
import time
import sqlite3
import random
from datetime import datetime,timedelta,date
codes=["sz000001","sh600519","sz300750"]
all_df=[]
today_date=date.today().strftime("%Y%m%d")
conn=sqlite3.connect("quant.db")
cursor=conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_price(
    ts_code TEXT,
    trade_date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    vol REAL
)""")
conn.commit()
for code in codes:
    print(f"正在处理:{code}...")
    exchange=code[:2].upper()
    stock_num=code[2:]
    ts_code=stock_num+"."+exchange
    cursor.execute("SELECT MAX(trade_date) FROM daily_price WHERE ts_code=?",(ts_code,))
    result=cursor.fetchone()
    max_date=result[0]
    if max_date:
        start_date_obj=datetime.strptime(max_date,"%Y%m%d")+timedelta(days=1)
        start_date_str=start_date_obj.strftime("%Y%m%d")
        print(f"  库里最新日期是 {max_date}，从 {start_date_str} 开始增量拉取...")
    else:
        start_date_str="20260901"
        print(f"  库里没数据，从 {start_date_str} 开始全量拉取...")
    if start_date_str>today_date:
        print(f"  已是最新，无需拉取。")
        continue
    try:
        df=ak.stock_zh_a_daily(symbol=code,start_date=start_date_str,end_date=today_date,adjust="qfq")
        if df.empty:
            print(f"  没有新数据，跳过。")
            continue
        df=df[["date","open","high","low","close","volume"]]
        df.columns=["trade_date","open","high","low","close","vol"]
        df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
        df["ts_code"]=ts_code
        df=df[df["vol"]>0]
        all_df.append(df)
        sleep_time = random.uniform(2, 4)
        print(f"  拉取成功，休息 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)
    except Exception as e:
        print(f"  {code} 拉取失败: {e}")
if all_df:
    final_df=pd.concat(all_df,ignore_index=True)
    print(f"\n准备入库，总共 {len(final_df)} 行新数据...")
    final_df.to_sql("daily_price",conn,if_exists="append",index=False)
    print("增量更新入库成功！")
else:
    print("\n没有需要更新的新数据。")
conn.close()