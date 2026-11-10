import pandas as pd
import akshare as ak
from datetime import datetime,timedelta,date
import random
import time
from db import engine,db_session
from sqlalchemy import text,create_engine,inspect
def sync_stock_data(codes):
    if len(codes)>10:
        return{
            "success":[],
            "failed":[{"error":"一次性最多只能同步 10 只股票，请分批请求"}]
        }
    success_list=[]
    failed_list=[]
    today_date=date.today().strftime("%Y%m%d")
    for code in codes:
        exchange=code[:2].upper()
        stock_num=code[2:]
        ts_code=stock_num+"."+exchange
        sql=text("SELECT MAX(trade_date) FROM daily_price WHERE ts_code=:ts_code")
        result=db_session.execute(sql,{"ts_code":ts_code}).fetchone()
        max_date=result[0] if result else None
        if max_date:
            start_date_obj=datetime.strptime(max_date,"%Y%m%d")+timedelta(days=1)
            start_date_str=start_date_obj.strftime("%Y%m%d")
            print(f"库里最新日期为{max_date},从{start_date_str}出发开始更新数据")
        else:
            start_date_str="20260101"
            print(f"数据库里面没有数据直接从{start_date_str}开始全量读取")
        if start_date_str>today_date:
            print("已经全量更新完数据库已经不用再更新了")
            continue
        try:
            df=ak.stock_zh_a_daily(symbol=code,start_date=start_date_str,end_date=today_date) 
            if df.empty:
                print("没有新数据")
                continue
            df=df[["date","open","high","low","close","volume"]]
            df.columns=["trade_date","open","high","low","close","vol"]
            df["trade_date"]=pd.to_datetime(df["trade_date"]).dt.strftime("%Y%m%d")
            df=df[df["vol"]>0]
            df["ts_code"]=ts_code
            df.to_sql("daily_price",engine,if_exists="append",index=False)
            success_list.append({'code':code,"msg":f"成功拉取 {len(df)} 行"})
            sleep_time=random.uniform(2,4)
            print(f"为防止封禁随机休息{sleep_time:.2f}秒")
            time.sleep(sleep_time)
        except Exception as e:
            failed_list.append({"code":code,"error":str(e)})
    return {"success":success_list,"failed":failed_list}
        