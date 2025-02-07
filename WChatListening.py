import os
import time
from wcferry import Wcf,WxMsg
from queue import Empty
from threading import Thread
from link_model import respond,respond_with_internet
from json import loads,dumps

memory = {}
model = {}
initialized = []
num_context = {}
temperature_room = {}
addition = {}
thought_output = {}
prompt = {}
HOLD_TAG = [False]
models_dict = [
    "deepseek-r1:1.5b",
    "deepseek-r1:8b",
    "deepseek-r1:14b",
    "qwen:0.5b",
    "qwen:4b",
    "qwen:14b"
]

def file_save(path):
    global memory
    global temperature_room
    global addition
    global thought_output
    global prompt
    global num_context
    global initialized
    with open(os.path.join(path,"memory.json"),"w",encoding="utf-8") as f:
        f.write(dumps(memory,ensure_ascii=False))
    with open(os.path.join(path,"temperature_room.json"),"w",encoding="utf-8") as f:
        f.write(dumps(temperature_room,ensure_ascii=False))
    with open(os.path.join(path,"addition.json"),"w",encoding="utf-8") as f:
        f.write(dumps(addition,ensure_ascii=False))
    with open(os.path.join(path,"model.json"),"w",encoding="utf-8") as f:
        f.write(dumps(model,ensure_ascii=False))
    with open(os.path.join(path,"initialized.json"),"w",encoding="utf-8") as f:
        f.write(dumps(initialized,ensure_ascii=False))
    with open(os.path.join(path,"thought_output.json"),"w",encoding="utf-8") as f:
        f.write(dumps(thought_output,ensure_ascii=False))
    with open(os.path.join(path,"num_context.json"),"w",encoding="utf-8") as f:
        f.write(dumps(num_context,ensure_ascii=False))
    with open(os.path.join(path,"prompt.json"),"w",encoding="utf-8") as f:
        f.write(dumps(prompt,ensure_ascii=False))

def file_load(path):
    with open(os.path.join(path,"memory.json"),"r",encoding="utf-8") as f:
        global memory
        memory = loads(f.read())
    with open(os.path.join(path,"temperature_room.json"),"r",encoding="utf-8") as f:
        global temperature_room
        temperature_room = loads(f.read())
    with open(os.path.join(path,"addition.json"),"r",encoding="utf-8") as f:
        global addition
        addition = loads(f.read())
    with open(os.path.join(path,"model.json"),"r",encoding="utf-8") as f:
        global model
        model = loads(f.read())
    with open(os.path.join(path,"initialized.json"),"r",encoding="utf-8") as f:
        global initialized
        initialized = loads(f.read())
    with open(os.path.join(path,"thought_output.json"),"r",encoding="utf-8") as f:
        global thought_output
        thought_output = loads(f.read())
    with open(os.path.join(path,"num_context.json"),"r",encoding="utf-8") as f:
        global num_context
        num_context = loads(f.read())
    with open(os.path.join(path,"prompt.json"),"r",encoding="utf-8") as f:
        global prompt
        prompt = loads(f.read())

def memo_add(role:str, content:str, roomid):
    memory[roomid].append({'role':role,'content':content})
    if len(memory[roomid]) > num_context[roomid]:
        del memory[roomid][1]

def memo_clear(roomid):
    memory[roomid].clear()
    if "chatroom" in roomid:
        memory[roomid].append({"role": "system","content": prompt[roomid]})
    # init(roomid, model=model[roomid])

def memo_init(roomid):
    prompt[roomid] = "请想象你现在加入了一个群聊，你需要对群聊里的消息进行回复。回复尽量简短，而且要求风趣贴心。"
    memory[roomid] = [{"role": "system","content": prompt[roomid]}]
    model[roomid] = "deepseek-r1:1.5b"
    num_context[roomid] = 20
    temperature_room[roomid] = 0.0
    addition[roomid] = ""
    thought_output[roomid] = False
    # init(roomid,model=model[roomid])
    initialized.append(roomid)

def memo_init_single(roomid):
    prompt[roomid] = ""
    memory[roomid] = []
    model[roomid] = "deepseek-r1:8b"
    num_context[roomid] = 20
    temperature_room[roomid] = 0.0
    addition[roomid]  = ""
    thought_output[roomid] = True
    initialized.append(roomid)

def memo_del(num,roomid):
    while num>0 and len(memory[roomid])>0:
        del memory[roomid][-1]

def order(message,msg,roomid,wcf):
    if message == "#Restart":
        print("\033[34m[ORDER] Restart in {}.\033[0m".format(roomid))
        memo_clear(roomid)
        wcf.send_text("Reset context.", msg.roomid)
        return
    elif message.startswith("#ResetPrompt"):
        print("\033[34m[ORDER] ResetPrompt in {}.\033[0m".format(roomid))
        text = message[message.find("#ResetPrompt") + len("#ResetPrompt") + 1:]
        prompt[roomid] = text
        wcf.send_text("Reset prompt.", msg.roomid)
        return
    elif message.startswith("#ChooseModel"):
        print("\033[34m[ORDER] Changed Model in {}.\033[0m".format(roomid))
        text = message[message.find("#ChooseModel") + len("#ChooseModel") + 1:]
        if text not in models_dict:
            wcf.send_text("No such model.", msg.roomid)
            return
        model[roomid] = text
        if "qwen" in text:
            thought_output[roomid] = False
        wcf.send_text("Changed Model.", msg.roomid)
        return
    elif message.startswith("#ContextNum"):
        print("\033[34m[ORDER] Reset ContextNum in {}.\033[0m".format(roomid))
        text = int(message[message.find("#ContextNum") + len("#ContextNum") + 1:])
        num_context[roomid] = text
        wcf.send_text(f"Contextnum set {text}.", msg.roomid)
        return
    elif message.startswith("#Alive"):
        print("\033[34m[ORDER] Checked Alive in {}.\033[0m".format(roomid))
        wcf.send_text("Alive.", msg.roomid)
        return
    elif message.startswith("#SetTemp"):
        print("\033[34m[ORDER] Reset Temp in {}.\033[0m".format(roomid))
        text = float(message[message.find("#SetTemp") + len("#SetTemp") + 1:])
        if text > 1.0 or text < 0.0:
            wcf.send_text("Illegal temperature.", msg.roomid)
            return
        else:
            temperature_room[roomid] = text
            wcf.send_text(f"Temperature set {text}.", msg.roomid)
            return
    elif message.startswith("#Add"):
        print("\033[34m[ORDER] Reset Addition in {}.\033[0m".format(roomid))
        text = message[message.find("#Add") + len("#Add") + 1:]
        addition[roomid] = text
        wcf.send_text(f"Reset addtion: {text}.", msg.roomid)
        return
    elif message.startswith("#Thought"):
        print("\033[34m[ORDER] Set output_thought in {}.\033[0m".format(roomid))
        if "qwen" in model[roomid]:
            thought_output[roomid] = False
            wcf.send_text("Thought is unavailable.", msg.roomid)
            return
        text = int(message[message.find("#Thought") + len("#Thought") + 1:])
        thought_output[roomid] = text
        wcf.send_text(f"Thought: {"True" if text else "False"}.", msg.roomid)
        return
    elif message.startswith("#KillErr"):
        print("\033[34m[ORDER] KillErr in {}.\033[0m".format(roomid))
        if "chatroom" in roomid:
            memo_init(roomid)
        else:
            memo_clear(roomid)
        wcf.send_text("KillErr.", msg.roomid)
        return
    elif message.startswith("#HOLD"):
        print("\033[30;44m[ORDER] HOLD ACTIVATED\033[0m")
        if roomid == "wxid_a4g0vnv07fcs11":
            HOLD_TAG[0] = True
            wcf.send_text("HOLD Activated.", roomid)
            return
        else:
            wcf.send_text("Illegal message.", msg.roomid)
            return
    elif message.startswith("#RELEASE"):
        print("\033[30;44m[ORDER] HOLD DEACTIVATED\033[0m")
        if roomid == "wxid_a4g0vnv07fcs11":
            HOLD_TAG[0] = False
            wcf.send_text("HOLD Deactivated.", roomid)
            return
        else:
            wcf.send_text("Illegal message.", msg.roomid)
            return
    elif message.startswith("#Show"):
        print("\033[34m[ORDER] Show Settings in {}.\033[0m".format(roomid))
        wcf.send_text(f"Model:{model[roomid]} , "+
                      f"NumContext:{num_context[roomid]} , "+
                      f"Temperature:{temperature_room[roomid]} , "+
                      f"Output_Thought:{True if thought_output[roomid] else False} , "+
                      f"Addition:{addition[roomid] if addition[roomid] != "" else None} ", msg.roomid)
        return
    elif message.startswith("#Del"):
        text = message[message.find("#Del") + len("#Del"):].replace(" ", "")
        num = 2 if text == "" else int(text)
        print("\033[34m[ORDER] Del {} conversations in {}.\033[0m".format(num,roomid))
        memo_del(num,roomid)
        wcf.send_text(f"Del {num}.", msg.roomid)
        return
    else:
        print("\033[34m[ORDER] Illegal message sent in {}.\033[0m".format(roomid))
        wcf.send_text("Illegal message.", msg.roomid)
        return

def processMsg(msg : WxMsg,wcf : Wcf):
    print("[INFO] Received message from RoomID:\033[4m{}\033[0m".format(msg.roomid))
    roomid = msg.roomid
    if msg.is_at(wcf.get_self_wxid()) or ("chatroom" not in roomid) and msg.sender != wcf.self_wxid:
        message = msg.content[msg.content.find("@Bot")+len("@Bot")+1:] if "chatroom" in roomid else msg.content
        if roomid not in initialized:
            print("[INFO] Initializing {}.".format(roomid))
            if "chatroom" in roomid:
                memo_init(roomid)
            else:
                memo_init_single(roomid)
        if message.startswith("#"):
            order(message,msg,roomid,wcf)
            return
        if HOLD_TAG[0]:
            print("\033[30;44m[HOLD]\033[0m Refused requirement.")
            wcf.send_text("[HOLD]Now service is unavailable.",roomid)
            return
        message = message + addition[roomid]
        memo_add("user", message, roomid)
        if message.startswith("*"):
            memory[roomid][-1]["content"] = memory[roomid][-1]["content"].replace("*","")
            result,thought = respond_with_internet(model=model[roomid],
                                                   temperature=temperature_room[roomid],
                                                   memory=memory[roomid])
        else:
            result,thought = respond(model=model[roomid],
                                     temperature=temperature_room[roomid],
                                     memory=memory[roomid])
        if result is None:
            wcf.send_text("bot似乎似了",roomid)
            return
        memo_add("assistant", message, roomid)
        if thought_output[roomid] and len(thought) != 0:
            wcf.send_text(f"思考过程：{thought}", msg.roomid)
        wcf.send_text(result,msg.roomid)
        print("[INFO] Sent message to {}. Success Respond.".format(msg.roomid))

def enableReceiving(wcf : Wcf):
    def core():
        t1 = time.time()
        while wcf.is_receiving_msg():
            t2= time.time()
            if t2-t1>1500:
                print("[INFO] Save.")
                file_save("Save")
                t1=time.time()
            try:
                processMsg(wcf.get_msg(),wcf)
            except Empty:
                continue
            except Exception as e:
                print("\033[30;41m[ERROR]\033[0m {}".format(e))
    wcf.enable_receiving_msg()
    Thread(target=core,name="WeChatBot",daemon=True).start()
    print("\033[3mBot running.\033[0m")

if __name__ == "__main__":
    path = "Save"
    file_load(path)
    print("\033[3mHistory loaded.\033[0m")
    wcf = Wcf()
    print("\033[3mWCF Generated.\033[0m")
    enableReceiving(wcf)
    wcf.keep_running()