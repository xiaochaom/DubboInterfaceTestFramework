# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""
import sys,logging,re,random,datetime,chardet, json, time
import httplib,urllib,types,base64
import hmac, base64, struct, hashlib, time
from Config.GlobalConf import ServiceConf

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

class ServiceTool(object):

    @staticmethod
    def md5(str):
        import hashlib
        import types
        if type(str) is types.StringType:
            m = hashlib.md5()
            m.update(str)
            return m.hexdigest()
        else:
            return ''

    @staticmethod
    def encryptData(data):
        return urllib.quote(base64.encodestring(data.strip()))

    @staticmethod
    def decryptData(dataEncrypted):
        print len(dataEncrypted)
        dataEncrypted = urllib.unquote(dataEncrypted)
        print len(dataEncrypted)
        lens = len(dataEncrypted)
        lenx = lens - (lens % 4 if lens % 4 else 4)
        decStr = dataEncrypted[:lenx]
        print len(decStr)
        result = ''
        try:
            result = base64.decodestring(decStr)
        except:
            pass
        return result


    @staticmethod
    def encryptSign(data,token_or_rid):
        sign_pre = "%s%s" % (urllib.unquote(urllib.quote(base64.encodestring(data.strip()))), token_or_rid)
        final_sign = ServiceTool.md5(str(sign_pre))
        return final_sign

    @staticmethod
    def get_google_auth_code(secret, digest_mode=hashlib.sha1, intervals_no=None):
        if intervals_no == None:
            intervals_no = int(time.time()) // 30
        key = base64.b32decode(secret)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, digest_mode).digest()
        o = ord(h[19]) & 15
        h = (struct.unpack(">I", h[o:o + 4])[0] & 0x7fffffff) % 1000000
        while (len(str(h)) < 6):
            h = "0" + str(h)
        return h

    @staticmethod
    def getSettlementGoogleAuthTestCode():
        return ServiceTool.get_google_auth_code(ServiceConf().GOOGLE_AUTH_SETTLEMENT_TEST_KEY)

    @staticmethod
    def getSettlementGoogleAuthDevCode():
        return ServiceTool.get_google_auth_code(ServiceConf().GOOGLE_AUTH_SETTLEMENT_DEV_KEY)


if __name__ == "__main__":
    print ServiceTool().decryptData("eyJ2ZXJzaW9uIjoiMi4wLjAiLCJyaWQiOiIyMjE2NjE5NzM2NzYzNzg3In0%253D")

    print ServiceTool().decryptData("eyJ1c2VySWQiOiIyMjE2NjE5NzM2NzYzNzg3IiwicmlkIjoiMjIxNjYxOTczNjc2Mzc4NyJ9")

    print ServiceTool().decryptData("eyJ1c2VySWQiOiIyMjE2NjE5NzM2NzYzNzg3IiwicmlkIjoiMjIxNjYxOTczNjc2Mzc4NyIsInNpZCI6IjIyMTY2MTk3MzY2NjQzODQiLCJ0YXJnZXRTdXBwbGllcklkIjoiMjIxNjYxOTczNjY2NDM4NCIsInN1cHBsaWVySWQiOiIyMjE2NjE5NzM2NjY0Mzg0In0%253D")

    print ServiceTool.getSettlementGoogleAuthTestCode()
    print ServiceTool.getSettlementGoogleAuthDevCode()