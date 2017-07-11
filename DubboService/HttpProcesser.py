# -*- coding: utf-8 -*-
import sys,re,time,types
sys.path.append("..")
import requests # python处理http相关的类库

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append("..")

import json,logging

'''
描述：Http处理器，根据host url params构建类对象并校验对象合法性，并且提供GET POST请求。处理并校验host、url、params
作者：王吉亮
日期：2016年7月7日
'''
class HttpProcesser(object):
    def __init__(self,host,url,header,params,sess = requests.session()):
        self.sess = sess
        self.timeout = 10
        #host应校验末尾是数字或字母，并且开头是http://,否则host格式不合法，创建对象失败
        host = host.strip().lower()
        if ((host[-1:].isalpha() or host[-1:].isdigit()) and (host[0:7]=="http://" or host[0:8]=="https://") ):
            self.__host = host
        else:
            raise ValueError(u"EXCEPTION: 参数host格式不正确，请检查。 host: %s" % host)
        #url应校验是/开头
        if (url[0:1]=="/" and url[-1:]!="/") or url=="/" or url=="":
            self.__url = url
        else:
            raise ValueError(u"EXCEPTION: 参数url格式不正确，请检查。 url: %s" % url)
        #params companyKey=874d8c821358a5e26f2524b10f43a292&https=0&ajax=1  需要处理为map类型
        self.__params = {}
        if params.strip() != "":
            keyvaluelist = params.split("&")
            for keyvalue in keyvaluelist:
                tmplist = keyvalue.split("=")
                if len(tmplist) == 2:
                    self.__params[tmplist[0]]=tmplist[1]
                elif len(tmplist)<2:
                    raise ValueError(u"EXCEPTION: 参数params格式不正确，请检查[参数%s的长度为%d.]。 params: %s" % (tmplist[0],len(tmplist),params))
                elif len(tmplist)>2:
                    tag = 0
                    key = tmplist[0]
                    value=tmplist[1]
                    for tmp in tmplist:
                        if tag==0 or tag==1:
                            tag+=1
                        else:
                            value += "="+ tmp
                    self.__params[key]=value

        #应为map类型
        try:
            header_dict = json.JSONDecoder().decode(header)
        except Exception,e:
            raise ValueError(u"EXCEPTION: 参数header类型不正确，请检查,应该为合法JSON字符串。")
        if type(header_dict) is types.DictType :
            self.__header = header_dict
        else:
            raise ValueError(u"EXCEPTION: 参数header类型不正确，请检查,应该为dict类型。")
    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self,host):
        #host应校验末尾是数字或字母，并且开头是http://,否则host格式不合法，创建对象失败
        if ((host[-1:].isalpha() or host[-1:].isdigit()) and host[0:7]=="http://" ):
            self.__host = host
        else:
            raise ValueError(u"EXCEPTION: 参数host格式不正确，请检查。 host: %s" % host)

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self,url):
        #url应校验是/开头
        if (url[0:1]=="/" ):
            self.__url = url
        else:
            raise ValueError(u"EXCEPTION: 参数url格式不正确，请检查。 url: %s" % url)

    @property
    def params(self):
        return self.__params

    @params.setter
    def params(self,params):
        #params companyKey=874d8c821358a5e26f2524b10f43a292&https=0&ajax=1  需要处理为map类型
        keyvaluelist = params.split("&")
        self.__params={}
        for keyvalue in keyvaluelist:
            tmplist = keyvalue.split("=")
            if len(tmplist) == 2:
                self.__params[tmplist[0]]=tmplist[1]
            elif len(tmplist)<2:
                raise ValueError(u"EXCEPTION: 参数params格式不正确，请检查[参数%s的长度为%d.]。 params: %s" % (tmplist[0],len(tmplist),params))
            elif len(tmplist)>2:
                tag = 0
                key = tmplist[0]
                value=tmplist[1]
                for tmp in tmplist:
                    if tag==0 or tag==1:
                        tag+=1
                    else:
                        value += "="+ tmp
                self.__params[key]=value

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self,headers):
        #应为map类型
        if type(headers) is types.DictType :
            self.__header = headers
        else:
            raise ValueError(u"EXCEPTION: 参数headers类型不正确，请检查,应该为dict类型。")

    def post(self):
        try:
            result = self.sess.post(self.host + self.url, headers=self.header, data=self.params,timeout=self.timeout)
            logging.debug(u"Host是%s" % self.host)
            logging.debug( u"发送POST请求%s" % self.url)
            logging.debug( u"参数是%s" % self.params)
            logging.debug( u"头信息是%s" % self.header)
            return result
        except Exception,e:
            raise ValueError(u"EXCEPTION: POST请求时发生异常：%s" % e)

    def get(self):
        try:
            result = self.sess.get(self.host + self.url,headers=self.header,params=self.params,timeout=self.timeout)
            logging.debug(u"Host是%s" % self.host)
            logging.debug( u"发送GET请求%s" % self.url)
            logging.debug( u"参数是%s" % self.params)
            logging.debug( u"头信息是%s" % self.header)
            return result
        except Exception, e:
            raise ValueError(u"EXCEPTION: GET请求时发生异常：%s" % e)


    def post_jsontype(self):
        try:
            result = self.sess.post(self.host + self.url, headers=self.header, data=json.dumps(self.params), timeout=self.timeout)
            logging.debug(u"Host是%s" % self.host)
            logging.debug(u"发送POST请求%s" % self.url)
            logging.debug(u"参数是%s" % self.params)
            logging.debug(u"头信息是%s" % self.header)
            return result
        except Exception, e:
            raise ValueError(u"EXCEPTION: POST请求时发生异常：%s" % e)


    def get_jsontype(self):
        try:
            result = self.sess.get(self.host + self.url, headers=self.header, params=json.dumps(self.params), timeout=self.timeout)
            logging.debug(u"Host是%s" % self.host)
            logging.debug(u"发送GET请求%s" % self.url)
            logging.debug(u"参数是%s" % self.params)
            logging.debug(u"头信息是%s" % self.header)
            return result
        except Exception, e:
            raise ValueError(u"EXCEPTION: GET请求时发生异常：%s" % e)


if __name__ == '__main__':
    pass