import requests
url = "http://127.0.0.1:5000/sync"
payload = {"codes": ["sz000002"]}
print("发送 POST 请求，正在拉取数据请稍候...")
response = requests.post(url, json=payload)
print("返回结果:", response.json())