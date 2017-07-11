#!/usr/bin/python
# coding=utf-8
from mustaine.client import HessianProxy


"""
参考文档：http://blog.csdn.net/haizhaopeng/article/details/47104897
我们只需要知道提供服务暴露的URL和服务接口即可，这里URL为http://10.95.3.74:8080/http_dubbo/search，
接口为org.shirdrn.platform.dubbo.service.rpc.api.SolrSearchService。
运行程序，可以调用提供方发布的服务。
"""

serviceUrl = 'http://10.95.3.74:8080/http_dubbo/search'
q = 'q=*:*&fl=*&fq=building_type:1'
start = 0
rows = 10
resType = 'xml'
collection = 'tinycollection'
if __name__ == '__main__':
    proxy = HessianProxy(serviceUrl)
    result = proxy.search(collection, q, resType, start, rows)
    print result