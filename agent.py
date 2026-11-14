from openai import OpenAI
from config import ZHIPU_API_KEY
import json
import requests
import time
client=OpenAI(
    api_key=ZHIPU_API_KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
tools=[
    {
        "type":"function",
        "function":{
            "name":"get_stock_prices",
            "description":"查询指定股票在某个时间段的历史价格（K线数据）",
            "parameters":{
                "type":"object",
                "properties":{
                    "ts_code":{
                        "type":"string",
                        "description":"股票代码，必须带后缀，例如 000001.SZ 或 600519.SH"
                    },
                    "start_date":{
                        "type":"string",
                        "description":"开始日期，格式为 YYYYMMDD，默认 20260101"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期，格式为 YYYYMMDD，默认 20261231"
                    }
                },
                "required":["ts_code"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"sync_stock_data",
            "description":"触发数据更新任务，将最新的股票数据拉取并保存到数据库中",
            "parameters":{
                "type":"object",
                "properties":{
                    "codes":{
                        "type":"array",
                        "items":{"type":"string"},
                        "description":"股票代码列表，例如 ['sz000001']"
                    }
                },
                "required":["codes"]
            }
        }
    }
]
def call_get_stock_prices(ts_code,start_date="20260101",end_date="20261231"):
    url=f"http://127.0.0.1:5000/stocks/{ts_code}/prices"
    params={"start":start_date,"end":end_date}
    return requests.get(url,params=params).json()
def call_sync_stock_data(codes):
    url="http://127.0.0.1:5000/sync"
    payload={"codes":codes}
    return requests.post(url,json=payload).json()
def run_agent():
    print("🤖 AI 助手已启动！(输入 '退出' 结束对话)")
    messages=[{"role":"system","content":"你是一个专业的股票数据助手。你可以调用工具来查询价格或同步最新数据。请务必用流畅的纯中文自然语言进行总结，绝对不要输出任何 XML 标签或代码！"}]
    while True:
        user_input=input("\n👨 你: ")
        if user_input=="退出":
            break
        if not user_input:  
            continue
        messages.append({"role":"user","content":user_input})
                # 第一次请求：大模型思考是否调工具（带重试机制）
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="glm-4.7-flash",
                    messages=messages,
                    tools=tools,          
                    tool_choice="auto"    
                )
                success = True
                break 
            except Exception as e:
                if attempt == max_retries - 1: 
                    print(f"❌ 请求失败，网络或服务器异常: {e}")
                    break
                print(f"⚠️ 服务器繁忙(429)，正在进行第 {attempt + 1} 次重试...")
                time.sleep(3) 
                
        if not success: 
            continue
            
        response_message = response.choices[0].message  # 只保留这一行
        messages.append(response_message)
        
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"\n[系统] 大模型决定调用工具: {function_name}")
                print(f"[系统] 传入参数: {function_args}")
                
                try:
                    if function_name == "get_stock_prices":
                        function_response = call_get_stock_prices(**function_args)
                    elif function_name == "sync_stock_data":
                        function_response = call_sync_stock_data(**function_args)
                    else:
                        function_response = {"error": "找不到该工具"}
                except Exception as e:
                    function_response = {"error": f"工具执行失败: {str(e)}"}

                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response, ensure_ascii=False),
                })
                
            second_response = client.chat.completions.create(
                model="glm-4.7-flash",
                messages=messages
            )
            print(f"🤖 AI: {second_response.choices[0].message.content}")
            
        else:
            print(f"🤖 AI: {response_message.content}")
if __name__ == "__main__":
    run_agent()