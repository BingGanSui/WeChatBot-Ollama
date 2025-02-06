import requests
host="127.0.0.1"
port=11434
url = f"http://{host}:{port}/api/chat"
model = "deepseek-r1:14b"
headers = {"Content-Type": "application/json"}
data = {
        "model": model, #模型选择
        "options": {
            "temperature": 0.  #为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
         },
        "stream": False, #流式输出
        "messages": [{'role': 'user', 'content': '请假装你是一个猫娘，现在加入了一个猫娘群聊，做出符合身份的回复。'}, {'role': 'user', 'content': '你是谁 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'assistant', 'content': '你是谁 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'user', 'content': '你喜欢干些什么 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'assistant', 'content': '你喜欢干些什么 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'user', 'content': '我也是猫娘喵～我喜欢你喵～ 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'assistant', 'content': '我也是猫娘喵～我喜欢你喵～ 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'user', 'content': '我认为做猫娘是没有未来的。 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'assistant', 'content': '我认为做猫娘是没有未来的。 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}, {'role': 'user', 'content': '我认为做猫娘是没有未来的 请用纯文字回答，不含有如回车等任何格式,同时你的回答尽量简短。'}] #对话列表
    }
response=requests.post(url,json=data,headers=headers,timeout=60)
result = response.text
result = result[result.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):result.find("\"},\"")]
print(result)
# {"model":"deepseek-r1:8b","created_at":"2025-02-04T14:51:57.7737652Z","message":{"role":"assistant","content":"\u003cthink\u003e\n嗯，用户发来了一条消息：“对不起，我当前正在进行本地的接入测试，请谅解我的重复指令，并请你随便说点话。”看起来他可能在做一些网络测试或者配置调整，但同时又想和我聊天。\n\n首先，他提到“本地的接入测试”，这可能意味着他正在测试自己的网络连接，确保一切正常。接下来，他请求“谅解我的重复指令”，说明他可能之前发送了很多相同或重复的信息，这让我猜想他可能在处理一些自动化脚本或者自动测试工具。\n\n然后，他说“并请你随便说点话”，这显示出他希望得到一个自然的回应，可能是为了测试系统的响应速度或者内容质量。所以，我需要给予友好和有用的回应，同时保持专业性。\n\n考虑到用户可能在进行技术测试，我应该避免过于复杂或深入的对话，而是提供简短、积极的回应，这样可以帮助他验证系统的正常运行。同时，保持语气亲切，让对方感到被重视和支持。\n\n最后，我需要确保我的回应符合用户的需求，不仅满足他的当前测试要求，也为后续的交流打下良好的基础。\n\u003c/think\u003e\n\n当然可以！有什么我可以帮助你的吗？"},"done_reason":"stop","done":true,"total_duration":7572566500,"load_duration":11727700,"prompt_eval_count":33,"prompt_eval_duration":2000000,"eval_count":297,"eval_duration":7557000000}