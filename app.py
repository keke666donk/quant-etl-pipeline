# from flask import Flask, request
# import sqlite3
# from datetime import date
# app=Flask(__name__)
# @app.route("/health")
# def health():
#     return{"status":"ok"}
# @app.route("/stocks/<ts_code>/prices")
# def prices(ts_code):
#     start=request.args.get("start","20260101")
#     today_date=date.today().strftime("%Y%m%d")
#     end=request.args.get("end","today_date")
#     conn=sqlite3.connect("database_v2.db")
#     cursor=conn.cursor()
#     cursor.execute("SELECT trade_date,open,high,low,close,vol FROM daily_price "  
#     "WHERE ts_code=? AND trade_date>=? AND trade_date<=? ORDER BY trade_date",(ts_code,start,end),)
#     rows=cursor.fetchall()
#     conn.close()
#     return{"code":0,"data":rows,"msg":""}
# if __name__=="__main__":
#     app.run(debug=True)
from flask import Flask,jsonify
from routes.stock import stock_bp
def create_app():
    app=Flask(__name__)
    from flask.json.provider import DefaultJSONProvider
    class CustomJSONProvider(DefaultJSONProvider):
        ensure_ascii = False
    app.json = CustomJSONProvider(app)
    app.json.ensure_ascli=False
    app.register_blueprint(stock_bp)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"code":404,"data":[],"msg":"接口不存在，请检查 URL"}),404
    @app.errorhandler(Exception)
    def internal_error(error):
        return jsonify({"code":500,"data":[],"msg": "服务器内部错误"}),500
    return app
app=create_app()
if __name__=="__main__":
    app.run(debug=True)