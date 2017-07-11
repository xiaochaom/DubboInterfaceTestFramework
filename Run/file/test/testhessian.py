# -*- coding:utf-8 -*-
from pyhessian.client import HessianProxy
from pyhessian import protocol
import json


def InvokeHessian(service, interface, method, req, retcode='000000'):
    try:
        url = 'http://192.168.0.1:10883/' + service + '.' + interface

        print 'URL:\t%s' % url
        print 'Method:\t%s' % method
        print 'Req:\t%s' % req
        res = getattr(HessianProxy(url), method)(req)
        print 'Res:\t%s' % json.dumps(res, ensure_ascii=False)

    except Exception, e:
        print e


if __name__ == '__main__':
    service = 'com.service.common.api.service'
    interface = 'TestHessianService'
    method = 'testHessian'
    req = protocol.object_factory('com.service.common.api.service.model.req.TestHessianRequest',spuId=813576647191044096L, updateBy="autotestwang",reason="个人爱好自动化")

    InvokeHessian(service, interface, method, req)