# coding:utf8
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import string
import email
from email.header import Header
from email.header import decode_header
import json
# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
import time
import hashlib
# from multiprocessing import Process
# from multiprocessing import Queue as tq
from threading import Thread
from queue import Queue as tq
import chardet
import re

to_list = ['sgwf525@126.com']
# flag = True
email_user = '****'
email_pass = '****'


class ReceiveMail(object):

    def __init__(self, name, to_list, tq):
        self.user = email_user
        self.passwd = email_pass
        self.name = name
        self.to_list = to_list
        self.cc_list = []
        self.tag = None
        self.doc = None
        self.tq = tq
        self.imap = "imap.exmail.qq.com"  # 腾讯企业邮箱iamp
        self.port = 993

    def my_decode(self, s, encoding):
        if encoding:
            return s.decode(encoding)
        return s

    def get_charset(self, message):
        # 获得字符编码方法
        return message.get_charset()
        # return default

    def parseEmail(self, msg):
        # 解析邮件正文方法
        mailContent = None
        contenttype = None
        suffix = None
        for part in msg.walk():
            if not part.is_multipart():
                contenttype = part.get_content_type()  # 获取内容类型
                # filename = part.get_filename()  # 获取附件名
                charset = self.get_charset(part)  # 获取编码格式
                if contenttype in ['text/plain']:
                    suffix = '.txt'
                if contenttype in ['text/html']:
                    suffix = '.html'
                if charset == None:
                    mailContent = part.get_payload(decode=True)
                else:
                    mailContent = part.get_payload(decode=True).decode(charset)  # 解码
        return (mailContent, suffix)

    def receive_mail(self):
        """
        接收邮件
        """
        flag = True
        self.server = imaplib.IMAP4_SSL(self.imap, port=self.port)
        self.server.login(self.user, self.passwd)
        while flag:
            # self.server = imaplib.IMAP4_SSL(self.imap, port=self.port)
            #
            # self.server.login(self.user, self.passwd)
            # log.info('登录成功')
            result, message = self.server.select("INBOX")
            typ, data = self.server.search(None, 'Unseen')  # 查询未读邮件
            coding = chardet.detect(data[0]).get('encoding')

            if data[0]:
                datas = data[0].decode(coding).split()
                for num in datas:
                    self.num = num
                    try:
                        typ, data = self.server.fetch(num, '(RFC822)')
                        data = data[0][1]
                        if isinstance(data, bytes):
                            coding = chardet.detect(data).get('encoding')
                            data = data.decode(coding)
                        msg = email.message_from_string(data)
                        ls = msg["From"].split(' ')
                        strfrom = ''
                        if(len(ls) == 2):
                            fromname = decode_header((ls[0]).strip('\"'))
                            strfrom = 'From : ' + \
                                self.my_decode(fromname[0][0], fromname[0][1]) + ls[1]
                        else:
                            strfrom = 'From : ' + msg["From"]
                        # strdate = 'Date : ' + msg["Date"]
                        # subject = decode_header(msg["Subject"])
                        to_list = re.findall(r"<(.*?)>", strfrom)[0]
                        # sub = self.my_decode(subject[0][0], subject[0][1])
                        #
                        # strsub = 'Subject : ' + sub
                        mailContent, suffix = self.parseEmail(msg)
                        # if mailContent:
                        #     coding = chardet.detect(mailContent).get('encoding')
                        if to_list in self.to_list:
                            # print('接收到来自{}停止发送信号'.format(self.name))
                            self.server.store(self.num, '+FLAGS', '\\Seen')  # 添加已读标记
                            self.tq.queue.clear()
                            # print('停止发送')
                            flag = False
                            # return True

                    except Exception as e:
                        # print('error:%s'%e)
                        pass
                        # return False
            time.sleep(5)
        self.server.close()
        # return False

    # def notify(self, publisher):
    #     self.receive_mail()


class MyEmail:

    def __init__(self, name, to_list, tq):
        self.user = email_user
        self.passwd = email_pass
        self.name = name
        self.to_list = to_list
        self.cc_list = []
        self.tag = '打卡提醒'
        self.plain = '回复任意邮件停止发送'
        self.doc = None
        self.tq = tq
        self.smtp = "smtp.exmail.qq.com"
        self.port = 465

    def send(self):
        '''
        发送邮件
        '''
        while True:
            try:
                server = smtplib.SMTP_SSL(self.smtp, port=self.port)
                server.login(self.user, self.passwd)
                server.sendmail("<%s>" % self.user, self.to_list + self.cc_list, self.get_attach())
                server.close()
                # print("The email to {} was sent successfully".format(self.name))
            except Exception as e:
                # print("send email failed:%s"%e)
                pass
            else:
                self.tq.put(1)
            time.sleep(60 * 2)
            if self.tq.empty():
                # print('停止对{}发送'.format(self.name))
                break

    def get_attach(self):
        '''
        构造邮件内容
        '''
        attach = MIMEMultipart()
        # 添加邮件内容
        # txt = MIMEText("FYI")
        # attach.attach(txt)
        if self.tag is not None:
            # 主题,最上面的一行
            attach["Subject"] = self.tag
        if self.user is not None:
            # 显示在发件人
            attach["From"] = "Data Team<%s>" % self.user
        if self.to_list:
            # 收件人列表
            attach["To"] = ";".join(self.to_list)
        if self.cc_list:
            # 抄送列表
            attach["Cc"] = ";".join(self.cc_list)
        if self.plain:
            attach.attach(MIMEText(str(self.plain), 'plain', 'utf-8'))
        if self.doc:
            # 估计任何文件都可以用base64，比如rar等
            # 文件名汉字用gbk编码代替
            name = os.path.basename(self.doc).encode("gbk")
            f = open(self.doc, "rb")
            doc = MIMEText(f.read(), "base64", "gb2312")
            doc["Content-Type"] = 'application/octet-stream'
            doc["Content-Disposition"] = 'attachment; filename="' + name + '"'
            attach.attach(doc)
            f.close()
        return attach.as_string()


def main():

    wf_tq = tq()
    wf_to_list = to_list
    rm = ReceiveMail('wangfan', wf_to_list, wf_tq)
    my = MyEmail('wangfan', wf_to_list, wf_tq)

    # wq_tq = tq()
    # wq_to_list = ['****']
    # rm1 = ReceiveMail('****', wq_to_list, wq_tq)
    # my1 = MyEmail('****', wq_to_list, wq_tq)

    t_list = []
    g1 = Thread(target=rm.receive_mail)
    g2 = Thread(target=my.send)
    # g3 = Thread(target=rm1.receive_mail)
    # g4 = Thread(target=my1.send)
    t_list.append(g1)
    t_list.append(g2)
    # t_list.append(g3)
    # t_list.append(g4)
    for t in t_list:
        t.start()
    for t in t_list:
        t.join()


if __name__ == '__main__':
    main()
