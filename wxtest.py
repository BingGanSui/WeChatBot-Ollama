from wcferry import Wcf, WxMsg
from queue import Empty
from threading import Thread

wcf=Wcf()

def processMsg(msg : WxMsg):
    if msg.from_group():
        print("[Received]",end="")
        print(msg.content,end=" type:")
        print(type(msg.content))

def enableListening():
    def core():
        while wcf.is_receiving_msg():
            try:
                msg = wcf.get_msg()
                processMsg(msg)
            except Empty:
                continue
            except Exception as e:
                print(f"ERROR:{e}")
                return
    wcf.enable_receiving_msg()
    Thread(target=core,name="WeChatBot_Listening",daemon=True).start()

enableListening()
wcf.keep_running()