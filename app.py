from flask import Flask, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_NAME = "database_v2.db" 

# 网页大表模板（加入了斑马纹和美化的排版）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>股票数据看板</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; background-color: #f9f9f9; color: #333; }
        h2 { text-align: center; color: #2c3e50; }
        .table-container { width: 80%; margin: 0 auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        table { border-collapse: collapse; width: 100%; background-color: white; }
        th, td { border: 1px solid #e0e0e0; padding: 12px 15px; text-align: center; }
        th { background-color: #34495e; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f8f9fa; } /* 斑马纹 */
        tr:hover { background-color: #e8f4fd; } /* 鼠标悬浮变色 */
    </style>
</head>
<body>
    <h2>{{ title }}</h2>
    <div class="table-container">
        <table>
            <tr>
                <th>股票代码</th>
                <th>交易日期</th>
                <th>收盘价 (前复权)</th>
                <th>成交量</th>
            </tr>
            {% for row in data %}
            <tr>
                <td><strong>{{ row.ts_code }}</strong></td>
                <td>{{ row.trade_date }}</td>
                <td>{{ row.close }}</td>
                <td>{{ row.vol }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

# 接口 1：全市场大表（按股票代码分组排列）
@app.route('/', methods=['GET'])
def get_all_stocks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 🌟 关键改动：先按 ts_code 排序（让同一只股票在一起），再按 trade_date 排序（最新的在前面）
    cursor.execute("""
        SELECT ts_code, trade_date, close, vol 
        FROM daily_price 
        ORDER BY ts_code ASC, trade_date DESC 
        LIMIT 200
    """)
    results = cursor.fetchall()
    conn.close()
    
    data_list = [{"ts_code": r[0], "trade_date": r[1], "close": r[2], "vol": r[3]} for r in results]
    return render_template_string(HTML_TEMPLATE, title="全市场数据（按股票分组展示）", data=data_list)

# 接口 2：单只股票数据
@app.route('/api/stock/<string:ts_code>', methods=['GET'])
def get_stock_data(ts_code):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT ts_code, trade_date, close, vol FROM daily_price WHERE ts_code = ? ORDER BY trade_date DESC", (ts_code,))
    results = cursor.fetchall()
    conn.close()
    
    data_list = [{"ts_code": r[0], "trade_date": r[1], "close": r[2], "vol": r[3]} for r in results]
    return render_template_string(HTML_TEMPLATE, title=f"单只股票详情: {ts_code}", data=data_list)

if __name__ == '__main__':
    app.run(debug=True)