from wcferry import Wcf,WxMsg
import requests
from queue import Empty
from threading import Thread

def init(host="127.0.0.1",port=11434,model = "deepseek-r1:8b"):
    url = f"http://{host}:{port}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": 0.  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": [{
            "role": "system",
            "content": "这是一个测试群聊，为你接下来的工作做准备。"
        }]  # 对话列表
    }
    res = requests.post(url, json=data, headers=headers, timeout=6000)
    print("[INIT] Initialized.")
    print(f"[INIT] {res.text}")

def respond(msg:str,sender=None,host="127.0.0.1",port=11434,model = "deepseek-r1:8b",temperature = 0.0):
    url = f"http://{host}:{port}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": temperature  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": [{
            "role": "user",
            "content": msg
        }]  # 对话列表
    }
    print(f"{msg} type:{str(type(msg))}")
    resp = requests.post(url, json=data, headers=headers, timeout=60)
    result = resp.text
    result = result[result.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):result.find("\"},\"")]
    return result

def processMsg(msg : WxMsg,wcf : Wcf):
    print("[PR_MSG] {} {} {} {}".format(msg.type, msg.id, msg.sender, msg.roomid))
    if msg.is_at(wcf.get_self_wxid()):
        print("[Received] {}".format(msg.content))
        print("[Respond] ",end="")
        result = respond(msg.content[msg.content.find("@Bot")+len("@Bot"):],wcf.get_self_wxid())
        wcf.send_text(result,msg.roomid)

def enableReceiving(wcf : Wcf):
    def core():
        while wcf.is_receiving_msg():
            try:
                processMsg(wcf.get_msg(),wcf)
            except Empty:
                continue;
            except Exception as e:
                print("[ERROR] {}".format(e))
    wcf.enable_receiving_msg()
    Thread(target=core,name="WeChatBot",daemon=True).start()
    print("Listening started.")

if __name__ == "__main__":
    wcf = Wcf()
    init()
    print("Have already started.")
    enableReceiving(wcf)
    wcf.keep_running()