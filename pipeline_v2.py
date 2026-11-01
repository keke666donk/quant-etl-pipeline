import akshare as ak
import pandas as pd
import time
import random
from datetime import datetime,timedelta,date
from sqlalchemy import create_engine,text,inspect
codes=["sz000001","sh600519","sz300750"]
all_df=[]
today_date=date.today().strftime("%Y%m%d")
engine=create_engine("sqlite:///database_v2.db")
inspector=inspect(engine)
if not inspector.has_table("daily_price"):
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE daily_price(
        ts_code TEXT,
        trade_date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        vol INTEGER,
        PRIMARY KEY(ts_code,trade_date)
        )
        """))
    print("数据表创建成功")
else:
    print("数据表已存在，准备增量拉取...")
print("\n--- 开始处理股票数据 ---")
for code in codes:
    exchange=code[:2].upper()
    stock_num=code[2:]
    ts_code=stock_num+"."+exchange
    with engine.connect() as conn:
        result=conn.execute(
            text("SELECT MAX(trade_date) FROM daily_price WHERE ts_code=:ts_code"),{"ts_code":ts_code}
        )
        max_date=result.fetchone()[0]
    if max_date:
        start_date_obj=datetime.strptime(max_date,"%Y%m%d")+timedelta(days=1)
        start_date_str=start_date_obj.strftime("%Y%m%d")
        print(f"  库里最新日期是 {max_date}，从 {start_date_str} 开始增量拉取...")
    else:
        start_date_str="20260101"
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
        df["trade_date"]=pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
        df["ts_code"]=ts_code
        df=df[df["vol"]>0]
        all_df.append(df)
        print(f"  拉取并清洗成功！")
        sleep_time=random.uniform(2,4)
        print(f"  防封禁休息 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)
    except Exception as e:
        print(f"  {code} 拉取失败: {e}")
if all_df:
    final_df=pd.concat(all_df,ignore_index=True)
    print(f"\n准备入库，总共 {len(final_df)} 行新数据...")
    final_df.to_sql("daily_price",engine,if_exists="append",index=False)
    print("企业级增量更新入库成功！")
else:
    print("\n没有需要更新的新数据。")
