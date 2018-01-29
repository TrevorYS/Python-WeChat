#coding:utf-8

import itchat
from echarts import Echart,Legend,Pie
import re
import jieba
import matplotlib.pyplot as plt
from wordcloud import WordCloud,ImageColorGenerator
import PIL.Image as Image
import os
import numpy as np
import time
from itchat.content import *


'''发送一条你好消息给微信上的文件传输助手'''
# itchat.send_msg(u'你好','filehelper')

@itchat.msg_register([TEXT,MAP,CARD,NOTE,SHARING])
def text_reply(msg):
    '''微信自动回复'''
    if not msg['FromUserName'] == itchat.get_friends(update=True)[0]["UserName"]:
        itchat.send_msg(u"[%s]收到好友@%s 的信息：%s\n" %
                        (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(msg['CreateTime'])),
                         msg['User']['NickName'],
                         msg.type), 'filehelper')
        print msg
        return u'[自动回复]您好，我现在有事不在，一会再和您联系。\n已经收到您的的信息：%s\n' % (msg.type)

class friends():

    def __init__(self):
        self.all_friends = itchat.get_friends(update=True)[1:]
        self.signatureList = []
    '''计算微信好友性别比例'''
    def get_sexInfo(self):
        '''初始化计数器'''
        male = female = other = 0
        '''遍历list，列表里的第一个是自己'''
        for i in self.all_friends:
            sex = i['Sex']
            if sex == 1:
                male += 1
            elif sex == 2:
                female += 1
            else:
                other += 1

        total = len(self.all_friends[1:])

        chart = Echart(u"%s的微信好友性别比例" % (self.all_friends[0]['NickName']),'from Wechat')
        chart.use(Pie('Wechat',
                      [
                          {'value':male,'name':u"男性 %.2f%%" %(float(male) / total * 100)},
                          {'value':female,'name':u"女性 %.2f%%" %(float(female) / total * 100)},
                          {'value':other,'name':u"其他 %.2f%%" %(float(other) / total * 100)},
                       ],
                      ))
        chart.use(Legend(["male","female","other"]))
        chart.plot()

    '''微信好友个性签名词云'''
    def get_friend_signature(self):
        for i in self.all_friends:
            signature = i["Signature"].strip().replace("span", "").replace("class", "").replace("emoji", "")
            '''利用正则表达式过滤emoji表情'''
            rep = re.compile("1f\d.+")
            signature = rep.sub("",signature)
            self.signatureList.append(signature)

        '''拼接字符串'''
        text = "".join(self.signatureList)
        print text
        # d = os.path.dirname(__file__)
        alice_coloring = np.array(Image.open(os.path.join("/Users/mac/Desktop/xiaohuangren.jpg")))

        wordlist_jieba = jieba.cut(text,cut_all=True)
        wl_space_split = " ".join(wordlist_jieba)

        my_wordcloud = WordCloud(background_color="white",max_words=2000,max_font_size=40,mask=alice_coloring,
                                 random_state=42,font_path='/Library/Fonts/Arial Unicode.ttf').generate(wl_space_split)
        image_colors = ImageColorGenerator(alice_coloring)
        plt.imshow(my_wordcloud.recolor(color_func=image_colors))
        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

        # 保存图片 并发送到手机
        my_wordcloud.to_file(os.path.join("/Users/mac/Desktop/","wechat_cloud.png"))
        itchat.send_image("/Users/mac/Desktop/wechat_cloud.png", 'filehelper')

        plt.imshow(my_wordcloud)
        plt.axis("off")
        plt.show()

    '''群发助手(个人)昵称+祝福语'''
    def send_wishes(self,SINCERE_WISH):
        for i in self.all_friends:
            itchat.send(SINCERE_WISH % (i['DisplayName']
                                  or i['NickName']), i['UserName'])

    '''群发助手(发送给群组人员)'''
    def send_special_wishe(self,REAL_SINCERE_WISH,chatroomName):
        itchat.get_chatrooms(update=True)
        chatrooms = itchat.search_chatrooms(name=chatroomName)
        if chatrooms is None:
            print u"没有找到群聊:" + chatroomName
        else:
            chatroom = itchat.update_chatroom(chatrooms[0]['UserName'])
            for i in chatroom['MemberList']:
                itchat.search_friends(userName=i['UserName'])
                itchat.send(REAL_SINCERE_WISH % (i['DisplayName']
                                           or i['NickName']), i['UserName'])



if __name__ == "__main__":
    itchat.auto_login()
    friend = friends()
    # friend.get_sexInfo()
    # friend.get_friend_signature()
    # friend.send_wishes(u'祝%s新年快乐！这是一条测试信息')
    # friend.send_special_wishe(u'%s新年快乐！！',u'老干部娱乐中心')

    itchat.run()