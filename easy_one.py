from wcferry import Wcf,WxMsg
import requests
from queue import Empty
from threading import Thread

# msg = [{"role": "user","content": "请想象你现在加入了一个群聊，你需要对群聊里的消息进行回复。回复尽量简短，而且要求风趣贴心。"}]
memory = {}
# model = ["deepseek-r1:14b"]
model = {}
initialized = []
num_context = {}
temperature_room = {}
addition = {}
thought_output = {}
HOLD_TAG = [False]

def msg_add(role:str,content:str,roomid):
    memory[roomid].append({'role':role,'content':content})
    if len(memory[roomid]) > num_context[roomid]:
        del memory[roomid][1]

def msg_clear(roomid):
    memory[roomid].clear()
    memory[roomid].append({"role": "system","content": "请想象你现在加入了一个群聊，你需要对群聊里的消息进行回复。回复尽量简短，而且要求风趣贴心。"})
    # init(roomid, model=model[roomid])

def msg_init(roomid):
    memory[roomid] = [{"role": "system","content": "请想象你现在加入了一个群聊，你需要对群聊里的消息进行回复。回复尽量简短，而且要求风趣贴心。"}]
    model[roomid] = "deepseek-r1:8b"
    num_context[roomid] = 20
    temperature_room[roomid] = 0.0
    addition[roomid] = " 请用纯文字回答，不含有任何格式，同时你的回答尽量简短。"
    thought_output[roomid] = False
    # init(roomid,model=model[roomid])
    initialized.append(roomid)

def msg_init_single(roomid):
    memory[roomid] = []
    model[roomid] = "deepseek-r1:8b"
    num_context[roomid] = 20
    temperature_room[roomid] = 0.0
    addition[roomid]  = ""
    thought_output[roomid] = True
    initialized.append(roomid)

def msg_reset(text : str,roomid):
    memory[roomid].clear()
    memory[roomid].append({"role": "user","content": text})

def init(roomid,host="127.0.0.1",port=11434,model = "deepseek-r1:8b"):
    url = f"http://{host}:{port}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": 0.  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": memory[roomid]
    }
    res = requests.post(url, json=data, headers=headers, timeout=6000)
    res = res.text
    res = res[res.find(r"/think\u003e\n\n") + len(r"/think\u003e\n\n"):res.find("\"},\"")]
    msg_add("system",res,roomid)
    print("[INIT] Initialized.")

def respond(roomid,host="127.0.0.1",port=11434,model = "deepseek-r1:8b"):
    url = f"http://{host}:{port}/api/chat"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,  # 模型选择
        "options": {
            "temperature": temperature_room[roomid]  # 为0表示不让模型自由发挥，输出结果相对较固定，>0的话，输出的结果会比较放飞自我
        },
        "stream": False,  # 流式输出
        "messages": memory[roomid]  # 对话列表
    }
    print(f"[HEAD] {data}")
    print(f"{memory[roomid]} type:{str(type(memory[roomid]))}")
    resp = requests.post(url, json=data, headers=headers, timeout=6000)
    print(f"[Respond] {resp.json()}")
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

def processMsg(msg : WxMsg,wcf : Wcf):
    print("[PR_MSG] {} {} {} {}".format(msg.type, msg.id, msg.sender, msg.roomid))
    roomid = msg.roomid
    if msg.is_at(wcf.get_self_wxid()) or ("chatroom" not in roomid):
        print("[Received] {}".format(msg.content))
        message = msg.content[msg.content.find("@Bot")+len("@Bot")+1:] if "chatroom" in roomid else msg.content
        if message.startswith("#"):
            if message == "#Restart":
                msg_clear(roomid)
                wcf.send_text("Reset context.",msg.roomid)
                return
            elif message.startswith("#ResetPrompt"):
                text = message[message.find("#ResetPrompt")+len("#ResetPrompt")+1:]
                msg_reset(text,roomid)
                wcf.send_text("Reset prompt.", msg.roomid)
                return
            elif message.startswith("#ChooseModel"):
                text = message[message.find("#ChooseModel") + len("#ChooseModel") + 1:]
                print("[Choose] {}".format(text))
                if text != "deepseek-r1:14b" and text != "deepseek-r1:8b":
                    wcf.send_text("No such model.", msg.roomid)
                    return
                model[roomid] = text
                wcf.send_text("Changed Model.", msg.roomid)
                return
            elif message.startswith("#ContextNum"):
                text = int(message[message.find("#ContextNum") + len("#ContextNum") + 1:])
                num_context[roomid] = text
                wcf.send_text(f"Contextnum set {text}.", msg.roomid)
                return
            elif message.startswith("#Alive"):
                wcf.send_text("Alive.", msg.roomid)
                return
            elif message.startswith("#SetTemp"):
                text = float(message[message.find("#SetTemp") + len("#SetTemp") + 1:])
                if text > 1.0 or text < 0.0:
                    wcf.send_text("Illegal temperature.", msg.roomid)
                    return
                else:
                    temperature_room[roomid] = text
                    wcf.send_text(f"Temperature set {text}.", msg.roomid)
                    return
            elif message.startswith("#Add"):
                text = message[message.find("#Add") + len("#Add") + 1:]
                addition[roomid] = text
                wcf.send_text(f"Reset addtion: {text}.", msg.roomid)
                return
            elif message.startswith("#Thought"):
                text = int(message[message.find("#Thought") + len("#Thought") + 1:])
                thought_output[roomid] = text
                wcf.send_text(f"Thought: {"True" if text else "False"}.", msg.roomid)
                return
            elif message.startswith("#KillErr"):
                init(roomid)
                wcf.send_text("KillErr.", msg.roomid)
                return
            elif message.startswith("#HOLD"):
                if roomid == "wxid_a4g0vnv07fcs11":
                    HOLD_TAG[0] = True
                    wcf.send_text("HOLD Activated.",roomid)
                    return
                else:
                    wcf.send_text("Illegal message.", msg.roomid)
                    return
            elif message.startswith("#RELEASE"):
                if roomid == "wxid_a4g0vnv07fcs11":
                    HOLD_TAG[0] = False
                    wcf.send_text("HOLD deactivated.",roomid)
                    return
                else:
                    wcf.send_text("Illegal message.", msg.roomid)
                    return
            else:
                wcf.send_text("Illegal message.", msg.roomid)
                return
        if HOLD_TAG[0]:
            print("[HOLD] Refused requirement.")
            wcf.send_text("[HOLD]Now service is unavailable.",roomid)
            return
        if roomid not in initialized:
            if "chatroom" in roomid:
                msg_init(roomid)
            else:
                msg_init_single(roomid)
        print("[Respond] ",end="")
        message = message + addition[roomid]
        msg_add("user",message, roomid)
        result,thought = respond(roomid,model=model[roomid])
        msg_add("assistant", message, roomid)
        if thought_output[roomid] and len(thought) != 0:
            wcf.send_text(f"思考过程：{thought}", msg.roomid)
        wcf.send_text(result,msg.roomid)

def enableReceiving(wcf : Wcf):
    def core():
        while wcf.is_receiving_msg():
            try:
                processMsg(wcf.get_msg(),wcf)
            except Empty:
                continue
            except Exception as e:
                print("[ERROR] {}".format(e))
    wcf.enable_receiving_msg()
    Thread(target=core,name="WeChatBot",daemon=True).start()
    print("Listening started.")

if __name__ == "__main__":
    wcf = Wcf()
    print("Have already started.")
    enableReceiving(wcf)
    wcf.keep_running()