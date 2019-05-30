import itchat, time
from itchat.content import *
import requests


@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    # 回复信息
    # 获取对方发送的数据msg.text
    print(msg.user.NickName, msg.user.RemarkName)
    print(msg.text)
    # 调用聊天机器人
    # requests.post('http://api.turingos.cn/turingos/api/v2',data={})
    # 将对方发送的数据传递给聊天机器人，获取聊天机器人回复的信息
    # 将获取聊天机器人回复的信息，传递给对方
    msg.user.send('小慧: %s, %s' % (msg.user.RemarkName, msg.text))
    if msg.text == 'q':
        itchat.logout()


@itchat.msg_register([PICTURE, RECORDING, ATTACHMENT, VIDEO])
def download_files(msg):
    msg.download(msg.fileName)
    typeSymbol = {
        PICTURE: 'img',
        VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)


@itchat.msg_register(FRIENDS)
def add_friend(msg):
    msg.user.verify()
    msg.user.send('Nice to meet you!')


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    if msg.isAt:
        msg.user.send(u'@%s\u2005I received: %s' % (
            msg.actualNickName, msg.text))


itchat.auto_login()
itchat.run()
