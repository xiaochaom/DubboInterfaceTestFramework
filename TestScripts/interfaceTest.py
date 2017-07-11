# -*- coding: utf-8 -*-：


import hashlib,urllib,json
import base64,requests
from ServiceTool import ServiceTool
from DubboService.HttpProcesser import HttpProcesser
import cardId,random,time
from Lib.DBTool import DBTool


def login():
    m = hashlib.md5()
    m.update("123456")
    loginParamsHarder = """{"rid":"123456"}"""


    #边城分销商
    #username = "lxstest01"

    #凤凰古城2
    username = 'lxstest01'
    # username = "ycdsh1"
    # username = 'yutao01'
    password = "123456"

    rid = "123456"
    data = """{"username":"%s","password":"%s","type":"2","version":"2.0.1",}""" % (username, password)
    data_encode = urllib.quote(base64.encodestring(data))
    sign = ServiceTool.md5(data + rid)
    login_params = """data=%s&sign=%s""" % (data_encode, sign)

    login_res = HttpProcesser("http://api.stage.mftour.net", "/user/login", loginParamsHarder, login_params).post()
    # print login_res.text
    final_tokenJson = json.loads(login_res.text)
    final_token = final_tokenJson['responseBody']['token']
    return final_token

#最小随机数 最大随机人数 买票数量 占库存 产品Id
def order(min,max,orderNum,buyTicket,productId,final_token):

    orderFlag = 0
    buyOrderNum = 0
    cardIds=[]

    orderIds = []
    for i in range(0,orderNum):
        cardIds.append([])

        if buyOrderNum == buyTicket:

            print '买了%s单，下单完毕，爱咋咋地' % (i)
            break
        randomNum = random.randint(min, max)
        print '本次票包含人数是',randomNum
        tourists  =''


        orderFlag = orderFlag + randomNum

        if orderFlag >= buyTicket:
            randomNum = (buyTicket - buyOrderNum)
            buyOrderNum = buyOrderNum + randomNum
        else:
            buyOrderNum = buyOrderNum + randomNum

        print '计算总人数后确定的本次票包含人数是',randomNum

        if(type(productId) == long):


            for j in range(0,randomNum):
                cardIds[i].append(cardId.makeNew())


                if tourists == '':
                        tourists = """{
                            "idcardNo":"%s",
                            "productId":"%s",
                            "remark":"remark",
                            "tourist":"wang%s",
                            "touristMobile":"13113131313",
                            "touristSpell":"wang%s"
                        }"""  % (cardIds[i][j],productId,j,j)
                else:
                        tourists = """%s,{
                                            "idcardNo":"%s",
                                            "productId":"%s",
                                            "remark":"remark",
                                            "tourist":"wang%s",
                                            "touristMobile":"13113131313",
                                            "touristSpell":"wang%s"
                                        }""" % (tourists,cardIds[i][j],productId, j, j)
            idCard = cardId.makeNew()
            # A区政策 4160257637482497
            # B区政策 4160259583639553
            # VIP 4160255221563393
            data = """
                                               {"contactee":{"contactMobile":"13113131313","contactee":"autotest","contacteeSpell":"","email":"","idcardNo":"%s"},
                                               "filleds":[],
                                               "products":[
                                                   {"productId":"%s","productNum":%s,"strategyId":"4160259583639553"}
                                               ],
                                               "remark":"",
                                               "saleType":"5",
                                               "scenicId":"4159865319063552",
                                               "spuId":"4160038057279488",
                                               "supplierId":"4159857034854401",
                                               "travelDate":"2017-06-07",
                                               "tourists":[%s],
                                               "version": "2.0.1"
                                                }
                                               """ % (idCard, productId, randomNum, tourists)
        elif(type(productId)==list):
                pass
                # for j in range(0, randomNum):
                #     cardIds[i].append(cardId.makeNew())
                #
                #     if tourists == '':
                #         tourists = """{
                #                 "idcardNo":"%s",
                #                 "productId":"%s",
                #                 "remark":"remark",
                #                 "tourist":"wang%s",
                #                 "touristMobile":"13113131313",
                #                 "touristSpell":"wang%s"
                #             }""" % (cardIds[i][j], productId, j, j)
                #     else:
                #         tourists = """%s,{
                #                                 "idcardNo":"%s",
                #                                 "productId":"%s",
                #                                 "remark":"remark",
                #                                 "tourist":"wang%s",
                #                                 "touristMobile":"13113131313",
                #                                 "touristSpell":"wang%s"
                #                             }""" % (tourists, cardIds[i][j], productId, j, j)
                #     idCard  = cardId.makeNew()
                # data = """
                #                     {"contactee":{"contactMobile":"13312345678","contactee":"sdsa","contacteeSpell":"","email":"","idcardNo":"%s"},
                #                     "filleds":[],
                #                     "products":[
                #                         {"productId":"%s","productNum":%s,"strategyId":"4182764551667714"}
                #                     ],
                #                     "remark":"",
                #                     "saleType":"5",
                #                     "scenicId":"2216619736663741",
                #                     "spuId":"4182760860680192",
                #                     "supplierId":"4182658131230721",
                #                     "travelDate":"2017-06-07",
                #                     "tourists":[%s],
                #                     "version": "2.0.1"
                #                      }
                #                     """ % (idCard, productId[product], randomNum, tourists)




        final_data = urllib.quote(base64.encodestring(data.strip()))


        sign_pre = "%s%s" % (urllib.unquote(final_data), final_token)
        final_sign = ServiceTool.md5(str(sign_pre))


        headers ={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0","token":final_token}
        final_param =  ['data',''],['sign','']
        final_param[0][1] =final_data
        final_param[1][1] = final_sign

        print '现在占用库存是%s' % buyOrderNum

        result =requests.post(url="http://api.stage.mftour.net/appapi/createOrder/forApp", data=final_param, headers=headers, timeout=10)
        final_resultJson = json.loads(result.text)
        try:
            final_orderId = final_resultJson['responseBody']['orderId']
            orderIds.append(final_orderId)
        except:
            print result.text
        paydata = """
                    {
                        "orderId":"%s",
                        "type":"0",
                        "version":"2.0.1"
                    }
                """ % final_orderId
        headers ={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0","token":final_token}

        pay_data = urllib.quote(base64.encodestring(paydata.strip()))
        pay_sign_pre = "%s%s" % (urllib.unquote(pay_data), final_token)
        pay_final_sign = ServiceTool.md5(str(pay_sign_pre))

        pay_final_param = ['data', ''], ['sign', '']
        pay_final_param[0][1] =pay_data
        pay_final_param[1][1] = pay_final_sign
        payResult =requests.post(url="http://api.stage.mftour.net/appapi/payment/pay", data=pay_final_param, headers=headers, timeout=10)


        pay_final_resultJson = json.loads(payResult.text)
        pay_final_message = pay_final_resultJson['message']
        pay_final_code = pay_final_resultJson['code']

        print final_orderId,'       message',pay_final_message,'       code',pay_final_code

    print orderIds
    print '完事'
    return orderIds



def checkTicket(cardIds):
    dbtool = DBTool( host='172.16.16.9', port=3306, username='core_r', password='EDEE512BA63B7DA',db='trade')



    # time.sleep(10)
    for i in range(0, len(cardIds)):
        print '------------' + str(cardIds[i]) + '====================='
        data = dbtool.execute_sql("""SELECT voucher_content from t_voucher_base where transaction_id = '%s' """ % cardIds[i])

        for j in range(0,len(data)):

            url = "http://fhgc.stage.piaozhijia.com/ticketService/QueryOrders?macId=863789020447557&cardId=%s" % (
            data[j])
            print url

            getOrderDetailByReseller = requests.get(
                    url=url,
                    timeout=10)
            print getOrderDetailByReseller.text
            queryOeders = json.loads(getOrderDetailByReseller.text)
            ticketURL = ''
            try:
                ticketURL = """ http://fhgc.stage.piaozhijia.com/ticketService/checkTicketDevice?ticketData={"request_macid":%%20"863789020447557", "child_product_id":"%s", "ticket_id":"%s", "is_group":"2"}""" % (
                queryOeders['responseBody'][0]['child_product_list'][0]['child_product_id'],
                queryOeders['responseBody'][0]['ticket_id'])
                print ticketURL
                checkTicketDevice = requests.get(
                        url=ticketURL,
                        timeout=10)
                print checkTicketDevice.text
            except Exception,e:
                print e
                print ticketURL

                print getOrderDetailByReseller.text




def refundTicketOrder(final_token,orderIdList):
    headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0",
               "token": final_token}
    for i in range(0, len(orderIdList)):

        dataJson = """{"orderId":"%s",
                               "version":"2.0.1"
                               }""" % str(orderIdList[i])
        data = urllib.quote(base64.encodestring((dataJson)))
        sign_pre = "%s%s" % (urllib.unquote(data), final_token)
        final_sign = ServiceTool.md5(str(sign_pre))

        final_param = ['data', ''], ['sign', '']
        final_param[0][1] = data
        final_param[1][1] = final_sign

        print orderIdList[i]

        result = requests.get(url="http://api.stage.mftour.net/appapi/order/getOrderDetailByReseller",
                              params=final_param,
                              headers=headers, timeout=10)

        refundRequstJson = json.loads(result.text)

        order_id = refundRequstJson['responseBody']['order_id']
        for i in range(0, len(refundRequstJson['responseBody']['merchs'][0]['vouchers'])):
            merchId = refundRequstJson['responseBody']['merchs'][0]['vouchers'][i]['merchId']
            voucherId = refundRequstJson['responseBody']['merchs'][0]['vouchers'][i]['voucherId']
            productId = refundRequstJson['responseBody']['merchs'][0]['productId']
            price = refundRequstJson['responseBody']['merchs'][0]['price']
            refundJson = """{
                                               "tickets" : [
                                                 {
                                                   "productNum" : 1,
                                                   "merchId" : "%s",
                                                   "voucherId" : "%s",
                                                   "productId" : "%s",
                                                   "merchPrice" : "%s"
                                                 }
                                               ],
                                               "orderId" : "%s",
                                               "version" : "2.0.1"
                                             } """ % (merchId, voucherId, productId, price, order_id)
            refundData = urllib.quote(base64.encodestring((refundJson)))
            refundSign = "%s%s" % (urllib.unquote(refundData), final_token)
            refund_final_sign = ServiceTool.md5(str(refundSign))
            refundParam = ['data', ''], ['sign', '']
            refundParam[0][1] = refundData
            refundParam[1][1] = refund_final_sign
            # refundParam = """data=%s&sign=%s"""%(refundData,refundSign)

            #  refundHeader = """ {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0",
            # "token": "%s"}""" % token
            refundRequst = requests.post(url="http://api.stage.mftour.net/appapi/settlement/refundMoney",
                                         data=refundParam,
                                         headers=headers, timeout=10)
            #
            # refundRequst = HttpProcesser('http://api.stage.mftour.net','/appapi/settlement/refundMoney',refundHeader,refundParam).post()
            print refundRequst.text


def PartCheckTicket(cardIds,token):
    time.sleep(10)
    for i in range(0, len(cardIds)):
        for j in range(0, len(cardIds[i])):

            if(j<2):
                headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0",
                           "token": token}
                dataJson = """{"orderId":"%s",
                                            "version":"2.0.1"
                                            }""" % str(cardIds[i][j])
                data = urllib.quote(base64.encodestring((dataJson)))
                sign_pre = "%s%s" % (urllib.unquote(data), token)
                final_sign = ServiceTool.md5(str(sign_pre))

                final_param = ['data', ''], ['sign', '']
                final_param[0][1] = data
                final_param[1][1] = final_sign

                print cardIds[i][j]

                result = requests.get(url="http://api.stage.mftour.net/appapi/order/getOrderDetailByReseller",
                                      params=final_param,
                                      headers=headers, timeout=10)

                print result.text



            url = "http://fhgc.stage.piaozhijia.com/ticketService/QueryOrders?macId=863789020447557&cardId=%s" % (
            cardIds[i][j])
            print url

            getOrderDetailByReseller = requests.get(
                url=url,
                timeout=10)

            queryOeders = json.loads(getOrderDetailByReseller.text)
            try:
                ticketURL = """ http://fhgc.stage.piaozhijia.com/ticketService/checkTicketDevice?ticketData={"request_macid":%%20"863789020447557", "child_product_id":"%s", "ticket_id":"%s", "is_group":"2"}""" % (
                queryOeders['responseBody'][0]['child_product_list'][0]['child_product_id'],
                queryOeders['responseBody'][0]['ticket_id'])
                print ticketURL
                checkTicketDevice = requests.get(
                    url=ticketURL,
                    timeout=10)
                print checkTicketDevice.text
            except:
                print ticketURL

                print getOrderDetailByReseller.text


if __name__ == '__main__':
    # stockNum = 500
    # minNum = 1
    # maxNum = 50
    # remainStockNum = 500
    #
    # orderNum = 20
    #
    # createdOrderNum = 0
    # remainOrderNum = 20
    #
    # orderStockList = []
    #
    # for i in range(0,orderNum):
    #     currentNum = random.randint(minNum,maxNum)
    #     orderStockList.append(currentNum)

    order(1, 100, 300, 248, 4160040137654273, login())

    # checkTicketOrder =order(2, 50,50,2,4160189320658946,login())
    # checkTick et(checkTicketOrder)
    # refundTicketOrder = order(1, 50, 50, 200, 4160040137654273, login())
    # refundTicket(17, 50, 50, 1, 4160189320658946, login())
    # PartCheckTicketOrder = order(1, 50, 50, 50, 4160040137654273, login())
    # PartCheckTicket(PartCheckTicketOrder,login())
    # checkTicket([1040117060600073])

    # refundTicketOrder(login(),[1040117060600074])



    # dbtool = DBTool( host='172.16.16.9', port=3306, username='core_r', password='EDEE512BA63B7DA',db='trade')
    # data = dbtool.execute_sql("""select DISTINCT transaction_id FROM t_voucher_base where transaction_id in ( SELECT transaction_id FROM t_order WHERE order_status = 10 and contact_mobile = '13312345678') and show_start_time >= 20170606000000 """)
    # print  data
    # refundTicketOrder(login(),[1040117060600061])

