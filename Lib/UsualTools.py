# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

from time import time
import datetime,os
import smtplib
from email import Encoders
import email.MIMEMultipart
import email.MIMEText
import email.MIMEBase
from email.header import Header
from Config.Config import Config
from Lib.VerifyTool import VerifyTool
import platform,logging,types


class UsualTools(object):
    """常用函数"""

    @staticmethod
    def get_current_time():
        #return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def get_current_time_numstr():
        # return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        return datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    @staticmethod
    def send_mail(email_list,subject,emailText,filepath):
        #发送email
        receiver = []
        receivertmp = email_list.split(';')
        #print receivertmp
        for mail in receivertmp:
            if VerifyTool.IsEmail(mail):
                receiver.append(mail)
        #print receiver
        #print receiver
        #print u"%s" % emailText
        sender = 'wangjiliang@mftour.cn'
        smtpserver = 'smtp.exmail.qq.com'
        username = 'wangjiliang@mftour.cn'
        password = 'Wang1984'
        # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
        msg=email.MIMEMultipart.MIMEMultipart()
        text_msg = email.MIMEText.MIMEText(emailText, 'plain', 'utf-8')
        msg.attach(text_msg)
        msg['From'] = sender
        msg['To'] =  ";".join(receiver)
        msg['Subject'] = Header(subject, 'utf-8')
        #print msg
        # 构造MIMEBase对象做为文件附件内容并附加到根容器
        contype = 'application/octet-stream'
        maintype, subtype = contype.split('/', 1)
        ## 读入文件内容并格式化
        if filepath!="":
            data = open(filepath, 'rb')
            file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
            file_msg.set_payload(data.read( ))
            data.close( )
            email.Encoders.encode_base64(file_msg)
            ## 设置附件头
            filename_list = filepath.split('/')
            filename = filename_list[len(filename_list)-1]
            basename = os.path.basename(filename)
            file_msg.add_header('Content-Disposition', 'attachment', filename = basename)
            msg.attach(file_msg)
        smtp = smtplib.SMTP(smtpserver)
        #smtp.connect(smtpserver)
        smtp.login(username, password)
        # 用smtp发送邮件
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()
        print "Email send!"

    @staticmethod
    def encrypt(infos):
        encryptInfos = ''
        for i in range (0,len(infos)):
            if i == len(infos): break
            encryptInfos = encryptInfos + str(hex(ord(infos[i])))[-2:]
        #print encryptInfos
        return encryptInfos

    @staticmethod
    def decrypt(encryptedInfos):
        decryptInfos = ""
        for i in range(0,len(encryptedInfos),2):
            hextoint = int("%s%s" % (encryptedInfos[i],encryptedInfos[i+1]),16)
            decryptInfos = decryptInfos + chr(hextoint)
        #print decryptInfos
        return decryptInfos

    @staticmethod
    def isWindowsSystem():
        return 'Windows' in platform.system()

    @staticmethod
    def isLinuxSystem():
        return 'Linux' in platform.system()

    @staticmethod
    def isMacOS():
        return 'Darwin' in platform.system()

if __name__ == "__main__":
    info = "ceshi_wr"
    print info
    enc = UsualTools.encrypt(info)
    encdbuser = Config("../ConfFile/test.conf").conf_dict['stock']['db_user']
    print encdbuser
    dec = UsualTools.decrypt(encdbuser)

    info = "mfpzjtour@123"
    print info
    enc = UsualTools.encrypt(info)
    encdbuser = Config("../ConfFile/test.conf").conf_dict['stock']['db_pass']
    print encdbuser
    dec = UsualTools.decrypt(encdbuser)
