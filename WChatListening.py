from wcferry import Wcf,WxMsg
from queue import Empty
from threading import Thread
from link_model import respond

memory = {}
model = {}
initialized = []
num_context = {}
temperature_room = {}
addition = {}
thought_output = {}
HOLD_TAG = [False]

def memo_add(role:str, content:str, roomid):
    memory[roomid].append({'role':role,'content':content})
    if len(memory[roomid]) > num_context[roomid]:
        del memory[roomid][1]

def memo_clear(roomid):
    memory[roomid].clear()
    memory[roomid].append({"role": "system","content": "请想象你现在加入了一个群聊，你需要对群聊里的消息进行回复。回复尽量简短，而且要求风趣贴心。"})
    # init(roomid, model=model[roomid])

def memo_init(roomid):
    memory[roomid] = [{"role": "system","content": "请想象你现在加入了一个群聊，你需要对群聊里的消息进行回复。回复尽量简短，而且要求风趣贴心。"}]
    model[roomid] = "deepseek-r1:8b"
    num_context[roomid] = 20
    temperature_room[roomid] = 0.0
    addition[roomid] = " 请用纯文字回答，不含有任何格式，同时你的回答尽量简短。"
    thought_output[roomid] = False
    # init(roomid,model=model[roomid])
    initialized.append(roomid)

def memo_init_single(roomid):
    memory[roomid] = []
    model[roomid] = "deepseek-r1:8b"
    num_context[roomid] = 20
    temperature_room[roomid] = 0.0
    addition[roomid]  = ""
    thought_output[roomid] = True
    initialized.append(roomid)

def memo_reset(text : str, roomid):
    memory[roomid].clear()
    memory[roomid].append({"role": "user","content": text})

def order(message,msg,roomid,wcf):
    if message == "#Restart":
        print("\033[34m[ORDER] Restart in {}.\033[0m".format(roomid))
        memo_clear(roomid)
        wcf.send_text("Reset context.", msg.roomid)
        return
    elif message.startswith("#ResetPrompt"):
        print("\033[34m[ORDER] ResetPrompt in {}.\033[0m".format(roomid))
        text = message[message.find("#ResetPrompt") + len("#ResetPrompt") + 1:]
        memo_reset(text, roomid)
        wcf.send_text("Reset prompt.", msg.roomid)
        return
    elif message.startswith("#ChooseModel"):
        print("\033[34m[ORDER] Changed Model in {}.\033[0m".format(roomid))
        text = message[message.find("#ChooseModel") + len("#ChooseModel") + 1:]
        print("[Choose] {}".format(text))
        if text != "deepseek-r1:14b" and text != "deepseek-r1:8b":
            wcf.send_text("No such model.", msg.roomid)
            return
        model[roomid] = text
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
        text = int(message[message.find("#Thought") + len("#Thought") + 1:])
        thought_output[roomid] = text
        wcf.send_text(f"Thought: {"True" if text else "False"}.", msg.roomid)
        return
    elif message.startswith("#KillErr"):
        print("\033[34m[ORDER] KillErr in {}.\033[0m".format(roomid))
        memo_init(roomid)
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
    else:
        print("\033[34m[ORDER] Illegal message sent in {}.\033[0m".format(roomid))
        wcf.send_text("Illegal message.", msg.roomid)
        return


def processMsg(msg : WxMsg,wcf : Wcf):
    print("[INFO] Received message from RoomID:\033[4m{}\033[0m".format(msg.roomid))
    roomid = msg.roomid
    if msg.is_at(wcf.get_self_wxid()) or ("chatroom" not in roomid):
        message = msg.content[msg.content.find("@Bot")+len("@Bot")+1:] if "chatroom" in roomid else msg.content
        if message.startswith("#"):
            order(message,msg,roomid,wcf)
            return
        if HOLD_TAG[0]:
            print("\033[30;44m[HOLD]\033[0m Refused requirement.")
            wcf.send_text("[HOLD]Now service is unavailable.",roomid)
            return
        if roomid not in initialized:
            print("[INFO] Initializing {}.".format(roomid))
            if "chatroom" in roomid:
                memo_init(roomid)
            else:
                memo_init_single(roomid)
        message = message + addition[roomid]
        memo_add("user", message, roomid)
        result,thought = respond(model=model[roomid],
                                 temperature=temperature_room[roomid],
                                 memory=memory[roomid])
        memo_add("assistant", message, roomid)
        if thought_output[roomid] and len(thought) != 0:
            wcf.send_text(f"思考过程：{thought}", msg.roomid)
        wcf.send_text(result,msg.roomid)
        print("[INFO] Sent message to {}. Success Respond.".format(msg.roomid))

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
    print("\033[3mBot running.\033[0m")

if __name__ == "__main__":
    wcf = Wcf()
    print("\033[3mWCF Generated.\033[0m")
    enableReceiving(wcf)
    wcf.keep_running()