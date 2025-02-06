import requests

def respond(model,temperature,memory,host="127.0.0.1",port=11434):
    # print("[INFO] Model:{}\n[INFO] Temperature:{}\n[INFO] Host:{}\n[INFO] Port:{}".format(model,temperature,host,port))
    url = f"http://{host}:{port}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": temperature  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": memory  # 对话列表
    }
    print("[INFO] Requesting...")
    resp = requests.post(url, json=data, headers=headers, timeout=6000)
    if resp.status_code == 200:
        print("[INFO] \033[30;42m 200 \033[0m Succeed.")
    else:
        print("[ERROR] \033[30;42m {} \033[0m Failed".format(resp.status_code))
    result = resp.text
    thought = remove_markdown(result[result.find(r"\u003cthink\u003e")+len(r"\u003cthink\u003e"):result.find(r"\u003c/think\u003e")])
    result = result[result.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):result.find("\"},\"")]
    result = remove_markdown(result)
    return result,thought

def remove_markdown(text):
    check = text.replace(r"\n","")
    if len(check) == 0:
        return ""
    text = text.replace(r"\n", " ")
    text = text.replace("**","")
    text = text.replace("#","")
    text = text.replace("\\","")
    return text