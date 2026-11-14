from openai import OpenAI
from config import ZHIPU_API_KEY
client = OpenAI(
    api_key=ZHIPU_API_KEY,
    base_url="https://open.bigmodel.cn/api/paas/v4"
)
print("正在连接大模型，请稍候...")
try:
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=[
            {"role": "user", "content": "你好，请用一句话介绍你自己"}
        ]
    )
    print("\n大模型回复：")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"\n连接失败，报错信息: {e}")