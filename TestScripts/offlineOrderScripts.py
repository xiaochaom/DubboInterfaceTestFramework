# -*- coding: utf-8 -*-：


import hashlib,urllib,json
import base64,requests
from DubboService.ServiceTool import ServiceTool
from DubboService.HttpProcesser import HttpProcesser
import random,time
from TestScripts.cardId import *
import logging,threading,logging.handlers
from Lib.DBTool import DBTool
import sys

def saaslogin(username,password):
    s = requests.session()
    host = "http://saas.stage.mftour.net"
    url = "/saas/login/doLogin"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"}
    final_param = ['username', ''], ['password', '']
    final_param[0][1] = username
    final_param[1][1] = password
    retres = s.post(url="%s%s" % (host, url), data=final_param, headers=headers, timeout=10)
    token_url = "/saas/login/menus"
    retres = s.post(url="%s%s" % (host, token_url), timeout=10)
    logging.info( retres.text)
    final_tokenJson = json.loads(retres.text)
    return final_tokenJson['data']['user']['token']

def userlogin(username,password):
    rid = "123456"
    data = """{"username":"%s","password":"%s","type":"2","version":"2.0.1",}""" % (username, password)
    data_encode = urllib.quote(base64.encodestring(data))
    sign = ServiceTool.md5(data + rid)
    login_params = """data=%s&sign=%s""" % (data_encode, sign)
    loginParamsHarder = """{"rid":"%s"}""" % rid
    login_res = HttpProcesser("http://api.stage.mftour.net", "/user/login", loginParamsHarder, login_params).post()
    # print login_res.text
    final_tokenJson = json.loads(login_res.text)
    final_token = final_tokenJson['responseBody']['token']
    return  final_token

#order手撕票
def orderOffline(token = '111',productId=4182761531768832,spuId=4182760860680192,strategyRelationId=4182777436569606,
                 supplierId=4182658131230721,resellerId=4043419632599040,
                 scenicId=828524026975080448,salePointId=4182799246950400,mobile="18611599536",contacteeTag="autotestscripts"):
    final_token = token
    host = "http://api.stage.mftour.net"
    url = "/saas/sale/trade/create"
    data = """
{
  "deliveryCode": "",
  "contactee":{"contactMobile":"%s","contactee":"%s","contacteeSpell":"wjltestauto","email":""},
  "merchs": [
    {
      "number": 15,
      "seats": [],
      "price": "158.00",
      "skuId": "%s",
      "strategyRelationId": "%s",
      "supplierId": "%s",
      "scenicId": "%s"
    }
  ],
  "guideId": "",
  "resellerId": "%s",
  "spuId": "%s",
  "touristSourceCity": "",
  "touristSourceCountry": "",
  "touristSourceProvince": "",
  "travelDept": "",
  "travelId": "",
  "visitorId": "",
  "remark": "autotestremartOfflineOrderTest",
  "payType": "3",
  "ticketOfficeId": "%s",
  "transactionId": "",
  "playDate": "2017-06-07",
  "voucherType": "4",
  "filledModelList": [],
  "type": "appapi"
}""" % (mobile,contacteeTag,productId,strategyRelationId,supplierId,scenicId,resellerId,spuId,salePointId)
    final_data = ServiceTool.encryptData(data)
    final_sign = ServiceTool.encryptSign(data,final_token)

    headers ={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0","token":final_token}
    final_param =  ['data',''],['sign','']
    final_param[0][1] =final_data
    final_param[1][1] = final_sign
    result = requests.post(url="%s%s" % (host, url), data=final_param, headers=headers, timeout=10)
    retJson = result.text
    retDict = json.loads(retJson)
    if retDict['code'] == "10000" :
        logging.info("下单成功！单号：%s" % retDict['responseBody'])
        return [True,retDict]
    else:
        logging.info("ERROR:"+ retDict['code'])
        logging.info(retDict)
        return [False,retDict]

#order身份证
def orderOfflineIdCard(token = '111',productId=4182761531768832,spuId=4182760860680192,strategyRelationId=4182777436569606,
                 supplierId=4182658131230721,resellerId=4043419632599040,
                 scenicId=828524026975080448,salePointId=4182799246950400,idcardNo="370681198401022228",mobile="18611599536",contacteeTag="autotestscripts",dateStr="2017-06-08"):
    try:
        final_token = token
        host = "http://api.stage.mftour.net"
        url = "/saas/sale/trade/create"
        data = """
    {
      "deliveryCode": "",
      "merchs": [
        {
          "number": 1,
          "seats": [],
          "price": "1.0",
          "skuId": "%s",
          "strategyRelationId": "%s",
          "supplierId": "%s",
          "scenicId": "%s"
        }
      ],
      "guideId": "",
      "resellerId": "%s",
      "spuId": "%s",
      "touristSourceCity": "",
      "touristSourceCountry": "",
      "touristSourceProvince": "",
      "travelDept": "",
      "travelId": "",
      "visitorId": "",
      "remark": "",
      "payType": "3",
      "ticketOfficeId": "%s",
      "transactionId": "",
      "playDate": "%s",
      "voucherType": "3",
      "contactee": {
        "contactMobile": "%s",
        "contactee": "%s"
      },
      "filledModelList": [],
      "tourists": [
        {
          "idcardNo": "%s",
          "product": {
            "id": "%s",
            "name": "1"
          },
          "productId": "%s"
        }
      ],
      "windowUse": "tourists",
      "type": "appapi"
    }""" % (productId,strategyRelationId,supplierId,scenicId,resellerId,spuId,salePointId,dateStr,mobile,contacteeTag,idcardNo,productId,productId)
        final_data = ServiceTool.encryptData(data)
        final_sign = ServiceTool.encryptSign(data,final_token)

        headers ={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0","token":final_token}
        final_param =  ['data',''],['sign','']
        final_param[0][1] =final_data
        final_param[1][1] = final_sign
        result = requests.post(url="%s%s" % (host, url), data=final_param, headers=headers, timeout=10)
        retJson = result.text
        retDict = json.loads(retJson)
        if retDict['code'] == "10000" :
            logging.info("下单成功！单号：%s" % retDict['responseBody'])
            return [True,retDict]
        else:
            logging.info("ERROR:"+ retDict['code'])
            logging.info(retDict)
            return [False,retDict]
    except Exception,e:
        logging.info(e)

#order身份证
def orderOfflineIdCardMultiSku(token = '111',productIds=[4182761531768832],spuId=4182760860680192,strategyRelationIds=[4182777436569606],
                 supplierId=4182658131230721,resellerId=4043419632599040,
                 scenicId=828524026975080448,salePointId=4182799246950400,mobile="18611599536",contacteeTag="autotestscripts",dateStr="2017-06-08",minRand = 1, maxRand = 20):
    try:
        merchsStr = ""
        touristsStr = ""
        for i in range(0,len(productIds)):
            orderNum = random.randint(minRand,maxRand)
            if merchsStr == "":
                merchsStr = """
                    {
                  "number": %d,
                  "seats": [],
                  "price": "1.0",
                  "skuId": "%s",
                  "strategyRelationId": "%s",
                  "supplierId": "%s",
                  "scenicId": "%s"
                }
                """ % (orderNum,productIds[i],strategyRelationIds[i],supplierId,scenicId)
            else:
                merchsStr = merchsStr + """,{
                "number": %d,
                "seats": [],
                "price": "1.0",
                "skuId": "%s",
                "strategyRelationId": "%s",
                "supplierId": "%s",
                "scenicId": "%s"
                }""" % (orderNum,productIds[i], strategyRelationIds[i], supplierId, scenicId)
            for j in range(0,orderNum):
                if touristsStr=="":
                    touristsStr = """
                        {
                          "idcardNo": "%s",
                          "product": {
                            "id": "%s",
                            "name": "1"
                          },
                          "productId": "%s"
                        }
                """ % (makeNew(),productIds[i],productIds[i])
                else:
                    touristsStr = touristsStr + """
                                        ,{
                                  "idcardNo": "%s",
                                  "product": {
                                    "id": "%s",
                                    "name": "1"
                                  },
                                  "productId": "%s"
                }""" % (makeNew(), productIds[i], productIds[i])

        final_token = token
        host = "http://api.stage.mftour.net"
        url = "/saas/sale/trade/create"
        data = """
    {
      "deliveryCode": "",
      "merchs": [
        %s
      ],
      "guideId": "",
      "resellerId": "%s",
      "spuId": "%s",
      "touristSourceCity": "",
      "touristSourceCountry": "",
      "touristSourceProvince": "",
      "travelDept": "",
      "travelId": "",
      "visitorId": "",
      "remark": "",
      "payType": "3",
      "ticketOfficeId": "%s",
      "transactionId": "",
      "playDate": "%s",
      "voucherType": "3",
      "contactee": {
        "contactMobile": "%s",
        "contactee": "%s"
      },
      "filledModelList": [],
      "tourists": [
        %s
      ],
      "windowUse": "tourists",
      "type": "appapi"
    }""" % (merchsStr,resellerId,spuId,salePointId,dateStr,mobile,contacteeTag,touristsStr)
        final_data = ServiceTool.encryptData(data)
        final_sign = ServiceTool.encryptSign(data,final_token)

        # headers ={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0","token":final_token}
        # final_param =  ['data',''],['sign','']
        # final_param[0][1] =final_data
        # final_param[1][1] = final_sign
        # result = requests.post(url="%s%s" % (host, url), data=final_param, headers=headers, timeout=10)
        headers = """{"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0",
                   "token": "%s"}""" % final_token
        final_param = "data=%s&sign=%s" % (final_data,final_sign)
        result = HttpProcesser(host,url,headers,final_param).post()

        retJson = result.text
        print retJson
        retDict = json.loads(retJson)
        if retDict['code'] == "10000" :
            logging.info("下单成功！单号：%s" % retDict['responseBody'])
            return [True,retDict]
        else:
            logging.info("ERROR:"+ retDict['code'])
            logging.info(retDict)
            return [False,retDict]
    except Exception,e:
        logging.info(e)
        return [False, "ERROR%s" % e]


def getOrderList(contacteeTag):
    dbtool = DBTool(host='172.16.16.9', port=3306, username='core_r', password='EDEE512BA63B7DA', db='trade')
    sql = "select DISTINCT(order_id) from t_order_merch where order_id in (select order_id from t_order where contactee='%s') and merch_state=0" % contacteeTag
    logging.info(sql)
    res = dbtool.execute_sql(sql)
    return res

def getOrderListBySupplierIdAndDate(supplierId,dateStr):
    dbtool = DBTool(host='172.16.16.9', port=3306, username='core_r', password='EDEE512BA63B7DA', db='trade')
    res = dbtool.execute_sql("select order_id from t_order_merch where order_id in (select transaction_id from t_voucher_base where supplier_id='%s' and start_time='%s 00:00:00') and merch_state=0" % (supplierId,dateStr))
    return res

def checkTicket(orderIdList,macIds,percentRate=0.5,percentCheckRate=1.0):
    dbtool = DBTool( host='172.16.16.9', port=3306, username='core_r', password='EDEE512BA63B7DA',db='trade')
    # time.sleep(10)
    maxMacLen = len(macIds)-1
    looplen = int(float(len(orderIdList))*percentRate)
    print looplen
    logging.info("全部订单数量%d，退款比例%f,实际应退款单数：%d。" % (len(orderIdList), percentRate, looplen))
    totalCount = 0
    failCount = 0
    passCount = 0
    for i in range(0, looplen):
        logging.info( '-=====OrderID:::--' + str(orderIdList[i][0]) + '=========尝试检票。。。=========')
        sql = """SELECT voucher_content from t_voucher_base where transaction_id = '%s' """ % orderIdList[i][0]
        data = dbtool.execute_sql(sql)
        logging.info(sql)
        lenCheck = int(float(len(data))*percentCheckRate)
        for j in range(0,lenCheck):
            try:
                indexMac = random.randint(0, maxMacLen)
                macId = macIds[indexMac]
                url = "http://voucher.stage.mftour.net/ticketService/QueryOrders?macId=%s&voucherContent=%s" % (macId,data[j][0])
                logging.info(url)
                getOrderDetailByReseller = requests.get(url=url,timeout=10)
                logging.info( getOrderDetailByReseller.text)
                queryOeders = json.loads(getOrderDetailByReseller.text)
                ticketURL = ''
                totalCount+=1
                ticketURL = """ http://voucher.stage.mftour.net/ticketService/checkVoucher?macId=%s&voucherIds=%s""" % (macId,queryOeders['voucherList'][0]['voucherId'])
                logging.info(ticketURL)
                checkTicketDevice = requests.get(url=ticketURL,timeout=10)
                retText = checkTicketDevice.text
                retdict = json.loads(retText)
                logging.info(retText)
                if retdict['code'] == '0001':
                    logging.info("检票成功")
                    passCount+=1
                else:
                    logging.info("检票失败")
                    failCount+=1
            except Exception,e:
                logging.info( e )
                logging.info("检票失败")
                failCount += 1
        logging.info("共检票%d，成功%d，失败%d。" % (totalCount,passCount,failCount))

def rerundOrder(orderIdList,percentOrder = 0.1):
    s = requests.session()
    host = "http://saas.stage.mftour.net"
    url = "/saas/login/doLogin"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"}
    final_param = ['username', ''], ['password', '']
    final_param[0][1] = "fhgc002"
    final_param[1][1] = "123456"
    retres = s.post(url="%s%s" % (host, url), data=final_param, headers=headers, timeout=10)
    token_url = "/saas/login/menus"
    retres = s.post(url="%s%s" % (host, token_url), timeout=10)
    looplen = int(float(len(orderIdList))*percentOrder)
    logging.info("全部订单数量%d，退款比例%f,实际应退款单数：%d。" %(len(orderIdList),percentOrder,looplen))
    dbtool = DBTool(host='172.16.16.9', port=3306, username='core_r', password='EDEE512BA63B7DA', db='trade')
    totalCount = 0
    failCount = 0
    passCount = 0
    for i in range(0, looplen):
        totalCount += 1
        orderId=orderIdList[i][0]
        sqlrefund = "select merch_id from t_order_merch where order_id='%s'" % orderId
        refundIdList = dbtool.execute_sql(sqlrefund)
        print refundIdList
        refundId = refundIdList[0][0]

        host = "http://saas.stage.mftour.net"
        url = "/saas/orders/refund"
        headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"}
        final_param = ['orderId', ''], ['refundIdsAndNums', ''], ['content', '']
        final_param[0][1] = orderId
        final_param[1][1] = "%s,1" % refundId
        final_param[2][1] = "testrefundbywjl"
        retres = s.post(url="%s%s" % (host, url), data=final_param, headers=headers, timeout=10)
        retstr = retres.text
        try:
            retdict = json.loads(retstr.strip())
            if retdict['code'] == "0000":
                print "退款成功"
                passCount+=1
            else:
                print "退款失败"
                print retstr
                failCount+=1
        except Exception,e:
            print e
            print "退款失败"
            print retstr
            failCount+=1

    dbtool.release()
    logging.info("应退款%d,实际执行%d,成功%d,失败%d。" % (looplen,totalCount,passCount,failCount))


def orderToFhgc(contacteeTag,dateStr,times):
    # 凤凰古城
    skuId = 4182736231727104
    spuId = 4182734688223232
    strategyId = 4182746298056708
    supplierId = 4182658131230721
    strategyRelationId = [[4182789583273985, 3469382589349889], [4182775087759361, 3742834423300096],
                          [4182777436569601, 4043419632599040], [4182779449835521, 4152481032503296], [4182775087759361, 3742834423300096]]  # id,resellerId
    tickctOfficeId = [4182799246950400, 4182799985147904]  # supplierId = 4182658131230721
    scenicId = 828524026975080448
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('fhgc002', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1
        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToFhgcMultiSku(contacteeTag,dateStr,times):
    # 凤凰古城
    skuIds = [4182736231727104,4182736231727106,4182741264891904]
    spuId = 4182734688223232
    strategyId = 4182746298056708
    supplierId = 4182658131230721
    strategyRelationIds = [[4182789583273985,4182789583273987,4182789583273989], 3469382589349889]  # id,resellerId
    tickctOfficeId = [4182799246950400, 4182799985147904]  # supplierId = 4182658131230721
    scenicId = 828524026975080448
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('fhgc002', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            rettmp = orderOfflineIdCardMultiSku(token=saastoken, productIds=skuIds, spuId=spuId,
                                            strategyRelationIds=strategyRelationIds[0],
                                            supplierId=supplierId, resellerId=strategyRelationIds[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
            totalCount += 1
            # print rettmp
            if rettmp[0]:
                orderIdList.append(rettmp[1]['responseBody'])
                passCount += 1
            else:
                failCount += 1
    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToGcbj(contacteeTag, dateStr,times):
    #古城八景+夜游沱江
    skuId=4182761531768832
    spuId=4182760860680192
    strategyId=4182764551667713
    supplierId=4182658131230721
    strategyRelationId=[[4182789583273990,3469382589349889],[4182775087759366,3742834423300096],[4182777436569606,4043419632599040],[4182779449835526,4152481032503296],[4182777436569606,4043419632599040]] #id,resellerId
    tickctOfficeId = [4182799246950400,4182799985147904] # supplierId = 4182658131230721
    scenicId=828524026975080448
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('fhgc002', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1

        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengA(contacteeTag, dateStr,times):
    #边城A区
    spuId = 4160102146244608
    skuId=4160103555530752
    strategyId=4160257637482496
    supplierId=4159857034854401
    strategyRelationId=[[4160726527115270,3469382589349889],[4160265958981632,3742834423300096],[4164254104551430,4152481032503296],[4160265958981632,3742834423300096],[4160726527115270,3469382589349889]] #id,resellerId
    tickctOfficeId = [4181564108308480,4181565316268032] # supplierId = 4182658131230721
    scenicId=4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('biancheng001', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1

        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengAGroup(contacteeTag,dateStr,times):
    # 凤凰古城
    skuIds = [4217625284968455]
    spuId = 4217625284968448
    strategyId = 4217625284968476
    supplierId = 4159857034854401
    strategyRelationIds = [[4217634009120768], 4159857034854401]  # id,resellerId
    tickctOfficeId = [4181564108308480, 4181565316268032]  # supplierId = 4182658131230721
    scenicId = 4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('fhgc002', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            rettmp = orderOfflineIdCardMultiSku(token=saastoken, productIds=skuIds, spuId=spuId,
                                            strategyRelationIds=strategyRelationIds[0],
                                            supplierId=supplierId, resellerId=strategyRelationIds[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint,
                                            contacteeTag=contacteeTag,dateStr=dateStr,minRand=50,maxRand=200)
            totalCount += 1
            # print rettmp
            if rettmp[0]:
                orderIdList.append(rettmp[1]['responseBody'])
                passCount += 1
            else:
                failCount += 1
    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengNCGroup(contacteeTag,dateStr,times):
    # 凤凰古城
    skuIds = [4222103398645761]
    spuId = 4222099976093696
    strategyId = 4223133739909120
    supplierId = 4159857034854401
    strategyRelationIds = [[[4223136021610496], 3544651299815425],[[4223136021610499], 4221787495792640],[[4223136021610504], 4222223703408640],[[4223136021610502], 4222310475169792],
                           [[4223136021610503], 4222314031939584],[[4223136021610501], 4222318997995520],[[4223329697792002], 4222329735413760],[[4223136021610500], 4222335506776064],
                           [[4223136021610498], 4222540457246720],[[4223136021610497], 4222664308752384]]  # id,resellerId
    tickctOfficeId = [4181564108308480, 4181565316268032,4222252850085888,4222253588283392]  # supplierId = 4182658131230721
    scenicId = 4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('fhgc002', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            index = random.randint(0,len(strategyRelationIds)-1)
            tmpStrategyRid = strategyRelationIds[index]
            rettmp = orderOfflineIdCardMultiSku(token=saastoken, productIds=skuIds, spuId=spuId,
                                                strategyRelationIds=tmpStrategyRid[0],
                                                supplierId=supplierId, resellerId=tmpStrategyRid[1],
                                                scenicId=scenicId, salePointId=tmpSalePoint,
                                                contacteeTag=contacteeTag,dateStr=dateStr,minRand=5,maxRand=20)
            totalCount += 1
            # print rettmp
            if rettmp[0]:
                orderIdList.append(rettmp[1]['responseBody'])
                passCount += 1
            else:
                failCount += 1
    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToFhgcGroup(contacteeTag,dateStr,times):
    # 凤凰古城
    skuIds = [4183179645157386,4183179645157412,4183179645157438]
    spuId = 4183179645157376
    strategyId = 4183179645157407
    supplierId = 4182658131230721
    strategyRelationIds = [[[4183184275668992,4183184275669001,4183184275669010], 4182658131230721]]  # id,resellerId
    tickctOfficeId = [4182799246950400, 4182799985147904,4228554861051904]  # supplierId = 4182658131230721
    scenicId = 828524026975080448
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('fhgc002', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            index = random.randint(0,len(strategyRelationIds)-1)
            tmpStrategyRid = strategyRelationIds[index]
            rettmp = orderOfflineIdCardMultiSku(token=saastoken, productIds=skuIds, spuId=spuId,
                                                strategyRelationIds=tmpStrategyRid[0],
                                                supplierId=supplierId, resellerId=tmpStrategyRid[1],
                                                scenicId=scenicId, salePointId=tmpSalePoint,
                                                contacteeTag=contacteeTag,dateStr=dateStr,minRand=5,maxRand=20)
            totalCount += 1
            # print rettmp
            if rettmp[0]:
                orderIdList.append(rettmp[1]['responseBody'])
                passCount += 1
            else:
                failCount += 1
    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengB(contacteeTag, dateStr,times):
    #边城B区
    spuId = 4160038057279488
    skuId=4160040137654273
    strategyId=4160259583639552
    supplierId=4159857034854401
    strategyRelationId=[[4160726527115272,3469382589349889],[4160265220784128,3742834423300096],[4164254104551432,4152481032503296],[4160265220784128,3742834423300096],[4160726527115272,3469382589349889]] #id,resellerId
    tickctOfficeId = [4181564108308480,4181565316268032] # supplierId = 4182658131230721
    scenicId=4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('biancheng001', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1

        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengVIP(contacteeTag, dateStr,times):
    #边城VIP区
    spuId = 4160188448243712
    skuId=4160189320658946
    strategyId=4160255221563392
    supplierId=4159857034854401
    strategyRelationId=[[4160726527115268,3469382589349889],[4160266630070272,3742834423300096],[4164254104551428,4152481032503296],[4160266630070272,3742834423300096],[4164254104551428,4152481032503296]] #id,resellerId
    tickctOfficeId = [4181564108308480,4181565316268032] # supplierId = 4182658131230721
    scenicId=4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('biancheng001', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1

        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengAandFhgc(contacteeTag, dateStr,times):
    #边城A区
    spuId = 4160206500528128
    skuId=4160207104507904
    strategyId=4160251799011328
    supplierId=4159857034854401
    strategyRelationId=[[4160726527115266,3469382589349889],[4160267301158912,3742834423300096],[4164254104551426,4152481032503296],[4160267301158912,3742834423300096],[4164254104551426,4152481032503296]] #id,resellerId
    tickctOfficeId = [4181564108308480,4181565316268032] # supplierId = 4182658131230721
    scenicId=4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('biancheng001', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1

        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)

def orderToBianchengBandFhgc(contacteeTag, dateStr,times):
    #边城B区+凤凰古城
    spuId = 4160224015941632
    skuId=4160224754139137
    strategyId=4160248644894720
    supplierId=4159857034854401
    strategyRelationId=[[4160726527115264,3469382589349889],[4160268039356416,3742834423300096],[4164254104551424,4152481032503296],[4160268039356416,3742834423300096],[4164254104551424,4152481032503296]] #id,resellerId
    tickctOfficeId = [4181564108308480,4181565316268032] # supplierId = 4182658131230721
    scenicId=4159865319063552
    contacteeTag = contacteeTag
    dateStr = dateStr

    saastoken = saaslogin('biancheng001', '123456')
    totalCount = 0
    passCount = 0
    failCount = 0
    orderIdList = []
    cardIdList = []
    for i in range(0, times):
        for tmpSalePoint in tickctOfficeId:
            for tmpStrategyRelation in strategyRelationId:
                cardId2 = makeNew()
                while True:
                    if cardId2 in cardIdList:
                        cardId2 = makeNew()
                    else:
                        break
                rettmp = orderOfflineIdCard(token=saastoken, productId=skuId, spuId=spuId,
                                            strategyRelationId=tmpStrategyRelation[0],
                                            supplierId=supplierId, resellerId=tmpStrategyRelation[1],
                                            scenicId=scenicId, salePointId=tmpSalePoint, idcardNo=cardId2,
                                            contacteeTag=contacteeTag,dateStr=dateStr)
                totalCount += 1
                if rettmp[0]:
                    orderIdList.append(rettmp[1]['responseBody'])
                    cardIdList.append(cardId2)
                    passCount += 1
                else:
                    failCount += 1

        logging.info("第%d次已经下单%d。成功%d，失败%d。" % (i + 1, totalCount, passCount, failCount))

    logging.info("共%s单。成功%d，失败%d。" % (totalCount, passCount, failCount))
    logging.info(orderIdList)
    logging.info(cardIdList)


if __name__ == '__main__':
    # skuTag = sys.argv[1] #gcbj fhgc bca bcb bcvip
    logging.basicConfig(level=logging.INFO)  # 初始化logging
    logFileName = "OfflineFhgcSJTtest05.log"
    logger = logging.getLogger('')
    consoletmp = logging.StreamHandler()
    console = logging.StreamHandler()
    handler = logging.handlers.RotatingFileHandler(logFileName, maxBytes=1024 * 1024 * 10, backupCount=5)  # 实例化handler
    logger.addHandler(handler)

    # #下单
    # contacteeTag = "wjltest——古城八景——20170608-test01"
    # dateStr = "2017-06-09"
    # macId = ["867908028233712"] # ["866693020841354","867908028233712"]
    # orderToGcbj(contacteeTag,dateStr,1)

    # #凤凰古城下单
    # contacteeTag = "wjltest凤凰古城20170608-test09-1元价格"
    # dateStr = "2017-06-08"
    # macId = ["867908028233712"] # ["866693020841354","867908028233712"]
    # orderToFhgc(contacteeTag,dateStr,1)

    #凤凰古城多规格下单
    # contacteeTag = "wjl凤凰古城多规格下单0613005"
    # dateStr = "2017-06-13"
    # macId = ["866693020841354","867908028233712"]
    # orderToFhgcMultiSku(contacteeTag,dateStr,100)

    # contacteeTag = "边城6月15日窗口下单30%比例"
    # dateStr = "2017-06-15"
    # macId = ["869315020639722","868404026631171"]

    # #边城A
    # contacteeTag = "wjltest边城A区20170608-test02"
    # dateStr = "2017-06-08"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengA(contacteeTag,dateStr,15)

    #边城B
    # contacteeTag = "wjltest边城B区20170618-test01"
    # dateStr = "2017-06-18"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengB(contacteeTag,dateStr,24)

    #边城VIP
    # contacteeTag = "wjltest边城VIP区20170608-test01"
    # dateStr = "2017-06-08"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengVIP(contacteeTag,dateStr,1)

    # #边城A+凤凰古城
    # contacteeTag = "wjltest边城A区+凤凰古城20170608-test01"
    # dateStr = "2017-06-08"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengAandFhgc(contacteeTag,dateStr,1)

    #边城B+凤凰古城
    # contacteeTag = "wjltest边城B区+凤凰古城20170608-test01"
    # dateStr = "2017-06-08"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengBandFhgc(contacteeTag,dateStr,1)

    # #边城AGroup
    # contacteeTag = "边城AGroup0615001"
    # dateStr = "2017-06-16"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengAGroup(contacteeTag,dateStr,1)

    # #边城内测Group
    # contacteeTag = "边城AGroup0615002"
    # dateStr = "2017-06-16"
    # macId = ["869315020639722","868404026631171"]
    # orderToBianchengNCGroup(contacteeTag,dateStr,1)

    # 凤凰古城团 团票
    contacteeTag = "凤凰古城团061502"
    dateStr = "2017-06-15"
    macId = ["866693020841354","867908028233712"]
    orderToFhgcGroup(contacteeTag,dateStr,1)

    # time.sleep(20)
    # # 获取可检票可退票的订单列表
    # orderIdList = getOrderList(contacteeTag)
    # print len(orderIdList)
    # # 检票
    # checkTicket(orderIdList,macId,0.95,1)

    # #获取可检票可退票的订单列表
    # orderIdList = getOrderList(contacteeTag)
    # print len(orderIdList)
    # # 退票
    # rerundOrder(orderIdList,1.0)

    # #检票
    # orderIdList = getOrderListBySupplierIdAndDate(supplierId=4159857034854401,dateStr=dateStr)
    # print orderIdList
    # print len(orderIdList)
    # rerundOrder(orderIdList, 1)