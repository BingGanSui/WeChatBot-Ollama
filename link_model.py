import copy
import requests
from fetch_html import get_fetch



def respond_with_internet(model,temperature,memory,host="127.0.0.1",port=11434):
    print("[NET] Requesting Searxng...")
    prompt = " 假设你获得了联网的功能，为了给用户满意的答复，请分析刚才这段消息并输出需要进行联网搜索的关键词。只能输出关键词，使用空格分隔，不包含其余任何内容。"
    memory_copy = [copy.deepcopy(memory)[-1],{"role":"system","content":prompt}]
    # memory_copy[-1]["content"] = memory_copy[-1]["content"].replace("*","") + prompt
    # memory_copy[-1]["role"] = "system"
    url = f"http://{host}:{port}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "options": {
            "temperature": temperature
        },
        "stream": False,
        "messages": memory_copy
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        print("[INFO] \033[30;42m 200 \033[0m Succeed.")
    else:
        print("[ERROR] \033[30;41m {} \033[0m Failed when first request in func::respond_with_internet.".format(response.status_code))
        return None, None
    result = response.text
    if "deepseek" in model:
        result = result[result.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):result.find("\"},\"")]
        result = remove_markdown(result).split(" ")
        result = [remove_markdown(s).replace(" ","") for s in result]
    else:
        result = remove_markdown(result[result.find("\"content\":\"") + len("\"content\":\""):].split("\"")[0]).split(" ")
        result = [remove_markdown(s).replace(" ", "") for s in result]
    search_ans = get_fetch(result)
    if search_ans == {}:
        return respond(model,temperature,memory,host=host,port=port)
    memory_copy[-1] = {"role":"system","content":f"对用户发送的上一条信息进行了联网查询，你需要结合搜索结果用文字做出回复，搜索结果为JSON格式，搜索结果如下：{search_ans}"}
    data = {
        "model": model,
        "options": {
            "temperature": temperature
        },
        "stream": False,
        "messages": memory_copy
    }
    second_response = requests.post(url, json=data, headers=headers)
    if second_response.status_code == 200:
        print("[INFO] \033[30;42m 200 \033[0m Succeed.")
    else:
        print("[ERROR] \033[30;41m {} \033[0m Failed when second request in func::respond_with_internet.".format(second_response.status_code))
        return None, None
    result = second_response.text
    if "deepseek" in model:
        thought = remove_markdown(
            result[result.find(r"\u003cthink\u003e") + len(r"\u003cthink\u003e"):result.find(r"\u003c/think\u003e")])
        result = result[result.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):result.find("\"},\"")]
        result = remove_markdown(result)
    else:
        thought = ""
        result = remove_markdown(result[result.find("\"content\":\"") + len("\"content\":\""):].split("\"")[0])
    return result, thought


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
        print("[ERROR] \033[30;41m {} \033[0m Failed".format(resp.status_code))
        return None, None
    result = resp.text
    if "deepseek" in model:
        thought = remove_markdown(result[result.find(r"\u003cthink\u003e")+len(r"\u003cthink\u003e"):result.find(r"\u003c/think\u003e")])
        result = result[result.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):result.find("\"},\"")]
        result = remove_markdown(result)
    else:
        thought = ""
        result = remove_markdown(result[result.find("\"content\":\"")+len("\"content\":\""):].split("\"")[0])
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

if __name__ == "__main__":
    # model = "qwen:4b"
    # response = respond(model,temperature=0.0,memory=[{"role":"user","content":"你好"},{"role":"assistant","content":"你好！很高兴能为你提供帮助。请问有什么问题需要我回答呢？"},{"role":"user","content":"请问你怎么看待AI的？"}],host="127.0.0.1",port=11434)
    model = "deepseek-r1:1.5b"
    # response1 = respond(model,0.0,[{"role":"user","content":"无畏契约是什么游戏"}])
    response = respond_with_internet(model,0.0,[{"role":"user","content":"无畏契约是什么游戏"}])