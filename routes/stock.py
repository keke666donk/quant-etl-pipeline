from flask import Blueprint, request
from services.stock_service import get_prices
from services.sync_service import sync_stock_data
import re
stock_bp=Blueprint("stock",__name__)
@stock_bp.route("/health")
def health():
    return{"status":"ok"}
@stock_bp.route("/stocks/<ts_code>/prices")
def prices(ts_code):
    start=request.args.get("start","20260101")
    end=request.args.get("end","20261231")
    if not re.match(r"^\d{6}\.[A-Z]{2}$",ts_code):
        return{"code":400,"data":[],"msg":"股票代码格式错误"}
    if not (re.match(r"^\d{8}$",start) and (re.match(r"^\d{8}$",end))):
        return{"code":400,"data":[],"msg":"日期格式错误，必须是 YYYYMMDD"}
    try:
        data=get_prices(ts_code,start,end)
        return{"code":0,"data":data,"msg":"success"}
    except Exception as e:
        print(f"查询出错: {e}")
        return{"code":500,"data":[],"msg":"服务器内部错误"}
@stock_bp.route("/sync", methods=["POST"])
def sync():
    data=request.get_json()
    if not data or "codes" not in data:
        return{"code": 400, "data": [], "msg": "请提供 codes 列表，例如 {'codes': ['sz000001']}"}
    codes=data["codes"]
    if not isinstance(codes, list):
        return {"code": 400, "data": [], "msg": "codes 必须是列表格式"}
    try:
        result = sync_stock_data(codes)
        return {"code": 0, "data": result, "msg": "同步任务执行完毕"}
    except Exception as e:
        print(f"同步出错: {e}")
        return {"code": 500, "data": [], "msg": "同步服务器内部错误"}