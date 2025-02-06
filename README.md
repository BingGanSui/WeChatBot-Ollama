# Bot基础功能
在**私聊**中可以直接向Bot发送信息。
在**群聊**中使用 **@Bot+内容** 的格式向Bot发送信息。
默认设置如下：

    “Prompt提示词”:”请想象你现在加入了一个群聊，你需要对群里的消息进行回复。回复尽量简短，而且要求风趣贴心。”,
    “Addition消息发送尾缀”:”请用纯文字回答，不含有如回车等任何格式，同时你的回答尽量简短”,
    “ContextNum上下文保留数量”:20,
    “Temperature模型温度”:0.0,
    “Model默认模型“:”deepseek-r1:8b”,
    “ThoughtOutput是否输出思考过程”:False
    
# Bot指令
## 重启对话
    @Bot #Restart
## 确认存活
    @Bot #Alive
## 设定提示词
    @Bot #ResetPrompt <content>
## 设定消息发送尾缀
    @Bot #Add <content>
## 设定上下文保留数量
    @Bot #ContextNum <content>
\<content>为一个整数
## 选择模型
    @Bot #ChooseModel <content>
当前可选择：**deepseek-r1:8b**, **deepseek-r1:14b**
## 设定是否输出思考
    @Bot #Thought <content>
\<content>为 **1或0**
## 设定模型温度
    @Bot #SetTemp <content>
\<content>为0-1之间的小数
## 重新初始化
    @Bot #KillErr
清除所有参数与对话记录，重新启动模型
**可通过此命令解决非网络故障**