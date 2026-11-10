from sqlalchemy import text
from db import db_session
def get_prices(ts_code,start,end):
    sql=text("""
            SELECT trade_date,open,high,low,close,vol
            FROM daily_price
            WHERE ts_code=:ts_code
            AND trade_date<=:end
            AND trade_date>=:start
            ORDER BY trade_date
            
""")
    result=db_session.execute(sql,{
        "ts_code":ts_code,
        "start":start,
        "end":end
    })
    return[dict(row._mapping) for row in result.fetchall()]