# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""
import sys,logging,re,random,datetime,chardet, json, time,redis
import httplib,urllib,types

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Config.Config import Config
from Lib.DBTool import DBTool
from Lib.UsualTools import UsualTools
from Config.EncodeConf import MyEncode
from Config.GlobalConf import ServiceConf
from HttpProcesser import HttpProcesser
from CommonProcess import CommonProcess
import exceptions
import requests
import traceback
from urllib import quote
from urllib import unquote
import base64
import hashlib
from ServiceTool import ServiceTool
from TestcaseHttpGroup import TestcaseHttpGroup
from TestcaseHttpDesc import TestcaseHttpDesc
from TestcaseHttpStep import TestcaseHttpStep
from Config.Const import *

class HttpService(object):
    """Http接口测试底层服务
    接收用例，使用httplib发送请求并获取结果断言。
    """
    def execute_testcases(self, case_list=[], config=Config("../ConfFile/http.conf"), env="test"):
        """
        获取excel数据并返回一个list，list包含N个dict，每个dict保存用例Excel中的各个值。规则如下：
        :param case_list: 一个列表，列表中每个值都是一个dict，对应的key如下。
         [  "用例编号", "名称",   "描述", "数据初始化", "数据恢复",  "HTTP请求头信息" , "接口","参数", "预期结果", "变量配置"]   (Excel列名)
            case_id      name     desc     data_init    data_recover  header            url     params  expect      varsconf  (dict的key)
        :return: case_list_with_testresult: 一个list，主体与case_list一致，只是每个值中的dict增加key returnMsg(执行dubbo接口返回的结果)，对应的key如下。
         [  "用例编号", "名称",   "描述", "数据初始化", "数据恢复",  "HTTP请求头信息" , "接口","参数", "预期结果", "变量配置"]   (Excel列名) 返回结果       断言结果        测试结果        测试时间
            case_id      name     desc     data_init    data_recover  header            url     params  expect      varsconf  (dict的key)    return_msg     assert_msg       test_result    perform_time
        """
        def set_error_before_request(case_dict,err_msg):
            logging.info(u"HttpService.py: execute_testcases: %s" % err_msg)
            case_dict['return_msg'] = err_msg.encode('utf8')
            case_dict['perform_time'] = "null"
            case_dict['test_result'] = ERROR
            case_dict['assert_msg'] = case_dict['return_msg']
            return  case_dict
        def set_fail_before_request(case_dict,err_msg,ptime):
            logging.info(u"HttpService.py: execute_testcases: %s" % err_msg)
            case_dict['return_msg'] = err_msg.encode('utf8')
            case_dict['perform_time'] = "%.3f s" % ptime
            case_dict['test_result'] = FAIL
            case_dict['assert_msg'] = case_dict['return_msg']
            return  case_dict

        cp = CommonProcess()
        logging.info(u"HttpService.py: execute_testcases: 测试环境是%s" % env)
        case_list_with_testresult = case_list
        # ===================加载系统配置信息===============================
        conf = config.conf_dict
        logging.debug(u"进入执行后的conf:%s" % conf)
        logging.info(u"HttpService.py: execute_testcases: 配置是%s" % conf )
        host = conf[env]['request_host']
        logging.info(u"HttpService.py: execute_testcases: 请求地址[%s]" % host)
        db_host = conf[env]['db_host']
        db_port = int(conf[env]['db_port'])
        db_user = conf[env]['db_user']
        db_pass = conf[env]['db_pass']

        if host == '' :
            logging.info(
                u"使用用例中提供的地址。\n"
                u"#规则是优先使用用例中提供的uri，如果没有，那么使用配置文件中的uri，\n"
                u"uri规则要带有协议，host，端口，例如http://10.0.18.13:8888，如果是80可以不带端口。")
        else:
            logging.info(u"找到host地址：%s" % host)

        if db_host == '' or db_port == '' or db_user == '' or db_pass == '':
            logging.info(u"HttpService.py: execute_testcases: FATAL_ERROR: 配置文件错误！终止执行！请检查配置文件是否包含当前系统的配置。")
            sys.exit(0)

        # ----解析系统名称和配置文件结束-------
        logging.info(u"HttpService.py: execute_testcases: DB请求信息[%s:%s:%s:%s]" % (db_host, db_port, db_user, db_pass))
        db_user = UsualTools.decrypt(db_user) #解密db_user
        db_pass = UsualTools.decrypt(db_pass) #解密db_pass

        for i in range(0, len(case_list)):
            time_start = time.time()
            logging.info(u"HttpService.py: execute_testcases: 开始执行第%d条用例。" % (i+1))
            db = DBTool()
            case_list_with_testresult[i]['request_host'] = host
            case_list_with_testresult[i]['initTakeTime'] = 0.0
            case_list_with_testresult[i]['recoverTakeTime'] = 0.0
            case_list_with_testresult[i]['execTakeTime'] = 0.0
            case_list_with_testresult[i]['totalTakeTime'] = 0.0
            try:
                case_id = case_list[i]['case_id'].strip()
                name = case_list[i]['name'].strip()
                desc = case_list[i]['desc'].strip()
                sqls_string_init = case_list[i]['data_init'].strip().strip()
                sqls_string_recover = case_list[i]['data_recover'].strip()
                header = case_list[i]['header'].strip()
                url = case_list[i]['url'].strip()
                params = case_list[i]['params'].strip()
                expect = case_list[i]['expect'].strip()
                varsconf = case_list[i]['varsconf'].strip()
            except Exception,e:
                case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 读取用例列表数据错误。")
                continue

            try:
                logging.info(u"HttpService.py: execute_testcases: 开始执行用例=>编号[%s]名称[%s]" % (case_id, name))
                is_sqls_string_init_executed = False
                is_get_http_response = False
                if case_id == '' or name == '' or desc == '' or sqls_string_init == '' or sqls_string_recover == '' or header=='' or url=='' or expect == '':
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 用例错误，有非空字段为空，请检查用例。")
                    continue
                #用例ID校验TC_sysname_0001
                case_id_split_list = case_id.split('_')
                if len(case_id_split_list) != 3 or case_id_split_list[0] != 'TC':
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TC_sysname_0001。")
                    continue
                try:
                    if int(case_id_split_list[2]) < 1 :
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TC_sysname_0001。")
                        continue
                except Exception, e:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 用例错误，用例编号不符合规则，请检查用例。用例编号规则为 TC_sysname_0001。")
                    continue

                #校验服务名 com.sdfsdf.sdflasd.sdklf
                #if re.match('^[a-z]+[\.][a-zA-Z0-9.]+[a-zA-Z0-9]$', service_name) == None:
                # 校验接口名字，小写字母开头，只包含字母和数字的驼峰命名法
                #if re.match('^[a-z][0-9a-zA-Z]+$', method_name) == None:

                db = DBTool(db_host,db_port,db_user,db_pass)
                # # =================特殊格式化处理变量配置。============================
                varsconf = cp.get_processed_vars(varsconf,env,db)
                logging.debug(u"HttpService.py: execute_testcases: 处理完成的变量配置：%s" % varsconf)

                #得到token
                is_get_token = False
                varsstring = cp.get_vars_by_varsconf(varsconf, env)
                var_dict = cp.get_var_dict_by_varstring(varsstring)
                try:
                    req = requests.session()
                    token_value=var_dict['KEY_token'].strip()
                    logging.info(u"开始获取token。")
                    if "GET_TOKEN(" in token_value:
                        token_params = cp.get_sub_string(token_value,"GET_TOKEN(",")")
                        token_params_list = token_params.strip().split(",")
                        if len(token_params_list)!=4:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: GET_TOKEN()参数错误，应该为GET_TOKEN(type,resellerId,username,password)。")
                            continue
                        login_host = host
                        login_url = "/appapi/user/login"
                        rid = token_params_list[1]  # 加入header中 resellerId
                        login_header = """{"rid":"%s"}""" % rid
                        rstype = token_params_list[0]
                        username = token_params_list[2]
                        password = token_params_list[3]
                        data = """{"username":"%s","password":"%s","type":%s,"version":"2.0.1",}""" % (username,password,rstype)
                        logging.info(u"登录数据为：%s" % data)
                        data_encode = quote(base64.encodestring(data))
                        sign = ServiceTool.md5(data + rid)
                        login_params = """data=%s&sign=%s""" % (data_encode,sign)
                        login_res = HttpProcesser(login_host,login_url,login_header,login_params,sess=req).post()
                        login_return_json =  login_res.text
                        if login_res.status_code != 200:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: GET_TOKEN()失败，返回状态码错误，返回码是%d。" % login_res.status_code)
                            continue
                        try:
                            login_return_dict = json.loads(login_return_json)
                            final_token = login_return_dict['responseBody']['token']
                            logging.info(u"得到token是：%s" % final_token)
                            varsconf = self.replace_GET_TOKEN(varsconf,final_token)
                            case_list[i]['varsconf'] = varsconf
                            is_get_token = True
                        except Exception,e:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: GET_TOKEN()失败[用户名：%s 密码：%s rid:%s 类型：%s]，没有返回有效JSON，返回内容为%s。" % (username, password, rid, rstype, login_return_json))
                            continue
                except Exception,e:
                    logging.debug( u"HttpService.py: execute_testcases:没有KEY_token变量，本次请求不需要获取KEY_token。")

                is_get_rid = False
                try:
                    rid_value = var_dict['KEY_rid'].strip()
                    is_get_rid = True
                except Exception,e:
                    logging.debug(u"HttpService.py: execute_testcases:没有KEY_rid变量，本次请求不需要获取rid。")

                is_get_data = False
                try:
                    data_value=var_dict['KEY_data'].strip()
                    logging.info(u"开始处理data。")
                    if "GET_DATA{(" in data_value:
                        data_sub = cp.get_sub_string(data_value,"GET_DATA{(",")}")
                        if data_sub!=False and data_sub.strip()!="":
                            logging.info(u"请求的data是%s " % data_sub.strip())
                            final_data = ServiceTool.encryptData(data_sub)#.replace("%0A",'')
                            logging.info(u"加密后的data是%s " % final_data)
                            varsconf = self.replace_GET_DATA(varsconf, final_data)
                            case_list[i]['varsconf'] = varsconf
                            is_get_data = True
                    else:
                        logging.debug(u"没有data 处理需求")

                    if is_get_data:
                        try:
                            sign_value = var_dict['KEY_sign']
                            logging.info(u"开始处理sign。")
                            if "GET_SIGN()" == sign_value.strip():
                                if is_get_token:
                                    sign_pre = "%s%s" % (unquote(final_data),final_token)
                                elif is_get_rid:
                                    sign_pre = "%s%s" % (unquote(final_data), rid_value)
                                else:
                                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 变量中有KEY_data时，必须要有KEY_token或者KEY_rid。")
                                    continue
                                final_sign = ServiceTool.md5(str(sign_pre))
                                varsconf = self.replace_GET_SIGN(varsconf, final_sign)
                                case_list[i]['varsconf'] = varsconf
                            else:
                                logging.debug( u"没有sign处理需求")
                        except Exception, e:
                            logging.debug(u"HttpService.py: execute_testcases:没有sign变量，本次请求不需要处理sign。")
                except Exception,e:
                    logging.debug( u"HttpService.py: execute_testcases:没有KEY_data变量，本次请求不需要处理data。")

                is_common_token_get = False
                try:
                    common_token_value=var_dict['COMMON_token'].strip()
                    logging.info(u"开始获取COMMON_token。")
                    #COMMON_token=GET_COMMON_TOKEN("host","url","method","params","token_path");
                    if "GET_COMMON_TOKEN(" in common_token_value:
                        token_params = cp.get_sub_string(common_token_value,"GET_COMMON_TOKEN(",")")
                        token_params_list = token_params.strip().split(",")
                        print token_params_list
                        if len(token_params_list)!=5:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],
                                u"CASE_ERROR: GET_COMMON_TOKEN()参数错误，GET_COMMON_TOKEN(host,url,method,params,token_path)。\n "
                                u"host若使用系统配置填写default。\n"
                                u"url为路径，例如/user/login。\n"
                                u"method为get或者post。\n"
                                u"params为参数组合，例如username=testuser&password=testpwd。\n"
                                u"token_path为返回json的token路径，例如返回json{'token':'df3eDfe322SEDFEZsdx'}，那么token_path填入['token']。\n"
                                u"COMMON_token变量举例：COMMON_token=GET_COMMON_TOKEN(http://www.test.com,/user/login,post,username=testuser&password=123456,['token']);")
                            continue

                        login_host = token_params_list[0] == DATA_DEFAULT and host or token_params_list[0]
                        login_url = token_params_list[1]
                        login_method = token_params_list[2]
                        login_params = token_params_list[3]
                        token_path = token_params_list[4]
                        login_header = "{}"

                        logging.debug("%s:%s" % (login_host,login_url))

                        if login_method.lower() == "post":
                            login_res = HttpProcesser(login_host,login_url,login_header,login_params,sess=req).post()
                        elif login_method.lower() == "get":
                            login_res = HttpProcesser(login_host, login_url, login_header, login_params,sess=req).get()

                        logging.debug("%s:%s" % (login_res.text, login_res.status_code))
                        login_return_json =  login_res.text

                        if login_res.status_code != 200:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: GET_COMMON_TOKEN()失败，返回状态码错误，返回码是%d。" % login_res.status_code)
                            continue
                        try:
                            login_return_dict = json.loads(login_return_json)
                            final_token = eval("login_return_dict%s" % token_path)
                            logging.info(u"得到token是：%s" % final_token)
                            varsconf = self.replace_GET_COMMON_TOKEN(varsconf,final_token)
                            case_list[i]['varsconf'] = varsconf
                            is_common_token_get = True
                        except Exception,e:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: GET_COMMON_TOKEN()失败[HOST:%s URL:%s METHOD:%s PARAMS:%s TOKEN_PATH:%s]，没有返回有效JSON，返回内容为%s。" % (login_host, login_url, login_method, login_params,token_path, login_return_json))
                            continue
                except Exception,e:
                    logging.debug(u"错误信息：%s" % e.message)
                    logging.debug( u"HttpService.py: execute_testcases:没有COMMON_token变量，本次请求不需要获取COMMON_token。")


                #================格式化处理变量配置结束==========================

                # =================对data、param、expect等进行变量替换。============================
                #参数处理sqls_string_init、sqls_string_recover、params、expect 的参数 进行参数带入处理
                sqls_string_init = cp.process_vars(sqls_string_init,varsconf,env)
                case_list_with_testresult[i]['data_init'] = sqls_string_init
                #print sqls_string_init
                sqls_string_recover = cp.process_vars(sqls_string_recover, varsconf, env)
                case_list_with_testresult[i]['data_recover'] = sqls_string_recover
                #print sqls_string_recover
                header = cp.process_vars(header, varsconf, env)
                case_list_with_testresult[i]['header'] = header
                #print header
                url = cp.process_vars(url, varsconf, env)
                case_list_with_testresult[i]['url'] = url
                #print url
                params = cp.process_vars(params, varsconf, env)
                case_list_with_testresult[i]['params'] = params
                if is_get_data:
                    case_list_with_testresult[i]['params'] = "%s\n未加密的data值为：%s" % (case_list_with_testresult[i]['params'],data_sub)
                #print params
                expect = cp.process_vars(expect, varsconf, env)
                case_list_with_testresult[i]['expect'] = expect
                #print expect
                #=====变量替换处理结束============================================================

                # ===数据初始化和数据恢复语句验证Start===
                if sqls_string_init != DATA_DEFAULT :
                    init_time_start = time.time()
                    logging.info( UsualTools().get_current_time() + u"HttpService.py: execute_testcases: 进入数据初始化验证。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    if (cp.validate_sql_strings(sqls_string_init, db) == False):
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 数据初始化验证错误，请检查相应sql语句是否含有where子句或者影响超过%d条数据。" % ServiceConf().sql_effect_lines)
                        continue
                    init_time_end = time.time()
                    case_list_with_testresult[i]['initTakeTime'] = init_time_end - init_time_start
                else:
                    logging.info( u"HttpService.py: execute_testcases: 数据初始化默认值default，不进行数据初始化验证。")

                if sqls_string_recover != DATA_DEFAULT:
                    logging.info( u"HttpService.py: execute_testcases: 进入数据恢复验证。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    if (cp.validate_sql_strings(sqls_string_recover, db) == False):
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 数据恢复验证错误，请检查相应sql语句是否含有where子句或者影响超过%d条数据。" % ServiceConf().sql_effect_lines)
                        continue
                else:
                    logging.info( u"HttpService.py: execute_testcases: 数据恢复默认值default，不进行数据恢复验证。")
                # =====数据初始化和数据恢复语句验证End=====
                # 数据初始化
                if sqls_string_init != DATA_DEFAULT :
                    logging.info( u"HttpService.py: execute_testcases: 进入数据初始化执行。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    if cp.execute_sql_strings(sqls_string_init, db) == False:
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 数据初始化执行错误，请检查相应sql语句是否正确。")
                        case_list_with_testresult[i]['data_init'] = u"[SQL语句有错误，请检查]\r\n" + case_list_with_testresult[i]['data_init']
                        continue
                    is_sqls_string_init_executed = True
                else:
                    logging.info( u"HttpService.py: execute_testcases: 数据初始化默认值default，不进行数据初始化执行。")

                #======================开始Http接口调用，校验完成。========================================
                request_host = cp.get_sub_string(header, "URI:[", "];") #"http://www.baidu.com:9999等"
                if request_host == False or request_host.strip()=='': request_host = host
                case_list_with_testresult[i]['request_host'] = request_host
                request_method = cp.get_sub_string(header, "METHOD:[", "];").strip().lower() #POST or GET
                request_header = cp.get_sub_string(header, "HEADER:[", "];") # 键值对应的header
                #print request_header
                request_url = url # /user/getinfo
                request_params = params #id=1&name=王吉亮
                request_start_time = time.time()
                try:
                    if request_method == "post":
                        res = HttpProcesser(request_host,request_url,request_header,request_params,sess=req).post()
                    elif request_method == "get":
                        res = HttpProcesser(request_host, request_url, request_header, request_params,sess=req).get()
                    else:
                        case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 目前仅支持POST或GET请求，不支持方法[%s]，请检查用例设置。" % request_method)
                        continue
                except Exception,e:
                    res = e
                request_end_time = time.time()
                perform_time = request_end_time - request_start_time
                case_list_with_testresult[i]['execTakeTime'] = perform_time
                logging.info(u"HttpService.py: execute_testcases: HTTP请求执行时间：%f秒" % perform_time)
                logging.debug(u"HttpService.py: execute_testcases: res：%s" % res)
                logging.debug(u"HttpService.py: execute_testcases: type(res)：%s" % type(res) )

                if res == False:
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"CASE_ERROR: 请求参数异常，请检查用例。")
                    continue
                elif type(res) == types.StringType and res[0:10]=="EXCEPTION:":
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"HTTP_ERROR: HTTP请求发送request时发生异常，异常信息：%s。" % res)
                    continue

                if type(res) == type(exceptions.ValueError()):
                    case_list_with_testresult[i] = set_fail_before_request(case_list_with_testresult[i],u"FAIL: 请求超时或者其他http错误。原因：%s" % (res.message),perform_time)
                    continue
                if type(res) != type(requests.models.Response()) :
                    case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i], u"HTTP_ERROR: 返回数据类型错误，应该是[%s],实际是[%s]。" % (type(requests.models.Response()),type(res)))
                    continue

                case_list_with_testresult[i]['perform_time'] = "%.3f s" % perform_time
                actual_status_code = res.status_code
                actual_headers = res.headers

                #print actual_headers
                actual_msg = res.content

                #===============处理网页的字符编码============================
                encode_msg = res.encoding
                charset_act = actual_msg.lower().replace(" ","").replace("\"","").replace("\'","")
                encode_msg2 = cp.get_sub_string(charset_act, "charset=", ">")
                encode_msg3 = cp.get_sub_string(charset_act, "charset=", ";")
                if len(encode_msg2) <= 10 and encode_msg2.strip()!="":
                    encode_msg = encode_msg2
                elif len(encode_msg3) <= 10  and encode_msg3.strip()!="":
                    encode_msg = encode_msg3
                else:
                    logging.debug(u"未获取到charset，无法解析网页！使用默认encode。")

                logging.debug(u"res.encoding编码：%s，处理后的encode为%s." % (res.encoding,encode_msg))

                # =================================================================
                if encode_msg!=None:
                    actual_msg = actual_msg.decode(encode_msg).encode('utf8')
                logging.debug(u"状态码：%s\n "
                              u"头信息：%s\n "
                              u"返回内容：%s \n "
                              u"字符编码：%s" % (actual_status_code, json.dumps(dict(actual_headers)), actual_msg, encode_msg))

                case_list_with_testresult[i]['return_msg'] = u"状态码：%s \n 头信息：%s \n 返回内容：%s".encode('utf8') % (actual_status_code,actual_headers,actual_msg)
                is_sqls_string_init_executed = True
                is_get_http_response = True
                #==================================================HTTP调用完成========================================================
                #得到返回结果，进行断言。分为状态、头信息、body断言，数据库断言。
                #初始化断言key
                case_list_with_testresult[i]['test_result'] = ""
                case_list_with_testresult[i]['assert_msg'] = ""
                def set_res_after_request(case_dict,tr, msg):
                    logging.info(u"HttpService.py: execute_testcases: %s " % msg)
                    case_dict['test_result'] = tr
                    case_dict['assert_msg'] = u"%s %s".encode('utf8') % (case_dict['assert_msg'],msg)
                    return case_dict
                #DONE 处理预期状态码
                expect_status_code = cp.get_sub_string(expect, "[RES_STATUS]", "[ENDRES_STATUS]")
                if expect_status_code.strip()=='':
                    logging.info(u"HttpService.py: execute_testcases: 未发现预期Response状态码，不进行返回值Response状态码断言。 ")
                else:
                    #断言状态码
                    if expect_status_code.strip()!='':
                        try:
                            expect_status_code = int(expect_status_code.strip())
                        except Exception,e:
                            case_list_with_testresult[i] = set_res_after_request(case_list_with_testresult[i], ERROR, u"STATUS断言：CASE_ERROR: 预期状态码[%s]不是数字。 " % expect_status_code.strip())
                            continue
                        if expect_status_code == actual_status_code:
                            #断言通过
                            case_list_with_testresult[i] = set_res_after_request(case_list_with_testresult[i], PASS, u"STATUS断言：PASS: 预期状态码验证通过，实际状态码为[%s]。 " %  actual_status_code)
                        else:
                            case_list_with_testresult[i] = set_res_after_request(case_list_with_testresult[i], FAIL, u"STATUS断言：FAIL: 预期状态码验证失败，实际状态码为[%s]。 " % actual_status_code)
                            continue

                # 处理预期头信息
                expect_header = cp.get_sub_string(expect, "[RES_HEADERS]", "[ENDRES_HEADERS]")
                if expect_header.strip()=='':
                    logging.info(u"HttpService.py: execute_testcases: 未发现预期Response头信息，不进行返回值Response头信息断言。 ")
                else:
                    # 进入头信息
                    actual_headers_json = json.dumps(dict(actual_headers))
                    #print actual_headers_json
                    return_expect_assert_result = cp.assert_result_http(expect_header, actual_headers_json)
                    logging.info(u"HttpService.py: execute_testcases: 断言结果list:%d" % len(return_expect_assert_result))
                    logging.info(u"HttpService.py: execute_testcases: 断言结果list：%s" % return_expect_assert_result)
                    case_list_with_testresult[i]['test_result'] = return_expect_assert_result[1]
                    case_list_with_testresult[i]['assert_msg'] = u"%s\nHEADERS断言：%s。 ".encode('utf8') % (case_list_with_testresult[i]['assert_msg'], return_expect_assert_result[0])
                    if return_expect_assert_result[1]!=PASS: continue

                # 处理预期内容=也就是response显示的部分，即body
                return_expect = cp.get_sub_string(expect, "[RES_CONTENT]", "[ENDRES_CONTENT]")
                if return_expect.strip()=='':
                    logging.info(u"HttpService.py: execute_testcases: 未发现预期Response返回值，不进行返回值Response预期结果断言。  ")
                else:
                    #进入预期结果断言
                    return_expect_assert_result = cp.assert_result_http(return_expect,actual_msg)
                    logging.info(u"HttpService.py: execute_testcases: 断言结果list:%d" % len(return_expect_assert_result))
                    logging.info(u"HttpService.py: execute_testcases: 断言结果list：%s" % return_expect_assert_result)
                    case_list_with_testresult[i]['test_result'] = return_expect_assert_result[1]
                    case_list_with_testresult[i]['assert_msg'] = u"%s\nCONTENT断言：%s。 ".encode('utf8') % (case_list_with_testresult[i]['assert_msg'], return_expect_assert_result[0])
                    if return_expect_assert_result[1] != PASS: continue

                #进行数据库断言部分
                dbdata_expect = cp.get_sub_string(expect, "[DBDATA]", "[ENDDBDATA]")
                if dbdata_expect.strip()=="":
                    logging.info(u"HttpService.py: execute_testcases: 未发现预期数据库数据，不进行数据库预期结果断言。 ")
                    try:
                        if case_list_with_testresult[i]['test_result'] != PASS and case_list_with_testresult[i][
                            'test_result'] != FAIL and case_list_with_testresult[i]['test_result'] != ERROR:
                            case_list_with_testresult[i] = set_res_after_request(case_list_with_testresult[i], ERROR,
                                                                                 u"\nDBDATA断言：%s。 " % u"CASE_ERROR: 用例错误：没有预期结果，也没有数据库预期。无法进行断言。")
                            continue
                    except Exception, e:
                        case_list_with_testresult[i]['assert_msg'] = set_res_after_request(case_list_with_testresult[i],
                                                                                           ERROR,
                                                                                           u"\nDBDATA断言：%s。 " % u"CASE_ERROR: 用例错误：没有预期结果，也没有数据库预期。无法进行断言。")
                        continue
                else :
                    # 进入数据库结果断言
                    if sqls_string_init == DATA_DEFAULT: db.flush()
                    assert_db_result = cp.assert_dbdata(dbdata_expect,db)
                    logging.debug(u"HttpService.py: execute_testcases: 数据库断言结果：%s" % assert_db_result)
                    case_list_with_testresult[i]['assert_msg'] = u"%s\nDBDATA断言：%s".encode("utf8") % (case_list_with_testresult[i]['assert_msg'] , assert_db_result[0] )
                    case_list_with_testresult[i]['test_result'] = assert_db_result[1]
            except Exception, e:
                logging.info( u"HttpService.py: execute_testcases: CASE_ERROR: 异常信息：%s" % e)
                error_msg = u"CASE_ERROR: %s" % e
                case_list_with_testresult[i]['test_result'] = ERROR
                case_list_with_testresult[i]['assert_msg'] = u"%s\n%s。 ".encode('utf8') % (case_list_with_testresult[i]['assert_msg'], error_msg)
                case_list_with_testresult[i]['return_msg'] = u"HTTP_请求错误: %s".encode('utf8') % e
                case_list_with_testresult[i]['perform_time'] = "null"
            finally:
                # 数据回复
                if sqls_string_recover != DATA_DEFAULT and is_sqls_string_init_executed == True :
                    recover_time_start = time.time()
                    logging.info( u"HttpService.py: execute_testcases: 进入数据恢复执行。")
                    #db = DBTool(db_host,db_port,db_user,db_pass)
                    if cp.execute_sql_strings(sqls_string_recover, db) == False:
                        logging.info( u"HttpService.py: execute_testcases: CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")
                        case_list_with_testresult[i]['data_recover'] = u"[SQL语句有错误，请检查]\r\n" + case_list_with_testresult[i]['data_recover']
                        if is_get_http_response == False:
                            case_list_with_testresult[i] = set_error_before_request(case_list_with_testresult[i],u"CASE_ERROR: 数据恢复错误，请检查相应sql语句是否正确。")
                    recover_time_end = time.time()
                    case_list_with_testresult[i]['recoverTakeTime'] = recover_time_end - recover_time_start
                else:
                    logging.info( u"HttpService.py: execute_testcases: 数据恢复默认值default或者未执行数据初始化，不执行数据恢复。")
                    logging.info( u"HttpService.py: execute_testcases: return_msg的值是：%s" % case_list_with_testresult[i]['return_msg'])
                time_end = time.time()
                case_take_time = time_end-time_start
                case_list_with_testresult[i]['totalTakeTime'] = case_take_time
                db.release()
                logging.info(u"HttpService.py: execute_testcases: 本条用例[%s]执行总时间：%f秒" % (case_id, case_take_time))
                try:
                    logging.debug(u"case_dict_finally:%s" % case_list_with_testresult[i])
                except Exception,e:
                    logging.debug(u"Finnally error : %s " % e)
                logging.info(u"==================================================================================================================")
        #print u"case_list_with_testresult after execute: %s" % case_list_with_testresult
        return case_list_with_testresult

    def execute_group_testcases(self,group_case_list=[], config=Config("../ConfFile/test.conf"), env="test"):
        """
        group_case_list的每个元素是一个TestcaseHttpGroup对象，TestcaseHttpGroup中有TestcaseHttpDesc和TestcaseHttpStep的list
        """
        cp = CommonProcess()
        logging.debug(group_case_list)
        logging.info(u"HttpService.py: execute_testcases: 测试环境是%s" % env)
        # case_list_with_testresult = group_case_list
        # ===================加载系统配置信息====各个环境的db和各个产品的hosturi======================
        conf = config.conf_dict
        logging.debug(u"进入执行后的conf:%s" % conf)
        logging.info(u"HttpService.py: execute_testcases: 配置是%s" % conf )
        logging.debug(conf[env])
        #对应环境下相关uri  host 格式 http://1.0.64.49:8118
        supportConsoleUri = conf[env][SUPPORT_CONSOLE_URI]
        pcDistributeUri = conf[env][PC_DISTRIBUTE_URI]
        appapiUri = conf[env][APPAPI_URI]
        weidianUri = conf[env][WEIDIAN_URI]
        saasUri = conf[env][SAAS_URI]
        settlementUri = conf[env][SETTLEMENT_URI]
        #数据库相关配置
        db_host = conf[env]['db_host']
        db_port = int(conf[env]['db_port'])
        db_user = conf[env]['db_user']
        db_pass = conf[env]['db_pass']
        # ----解析系统名称和配置文件结束-------
        logging.info(u"HttpService.py: execute_testcases: DB请求信息[%s:%s:%s:%s]" % (db_host, db_port, db_user, db_pass))
        db_user = UsualTools.decrypt(db_user) #解密db_user
        db_pass = UsualTools.decrypt(db_pass) #解密db_pass
        if db_host == '' or db_port == '' or db_user == '' or db_pass == '':
            logging.info(u"HttpService.py: execute_testcases: FATAL_ERROR: 配置错误！终止执行！请检查配置是否包含当前系统的配置。")
            sys.exit(0)
        db = DBTool(db_host, db_port, db_user, db_pass)

        for i in range(0, len(group_case_list)):
            try:
                requestSession = requests.session()  #全局请求session，每个组合用例一个生命周期，组合用例执行完退出。
                varsPool = {} #变量池，里面存入知道到当前步骤之前可用的变量，包括前置变量和后置变量。
                tgc = TestcaseHttpGroup() #构建当前HTTP组合用例对象
                tgc.copy(group_case_list[i])
                tgcDesc = tgc.tgcDesc
                tgcSteps = tgc.tgcStepList
                tgcType = tgc.tgcType
                if tgcType == TESTCASE_TYPE_GROUP:
                    logging.info(u"HttpService.py: execute_testcases: 开始执行第%d条用例。" % (i+1))
                else:
                    logging.info(u"HttpService.py: execute_testcases: 第%d条用例不是组合用例，暂不执行当前用例。" % (i + 1))
                    continue
                #TODO 开始断言tgcDesc的有效性
                # print tgcDesc.toString()
                # print "######################################################################################################"
                for j in range(0,len(tgcSteps)):
                    # TODO 给当前步骤对象赋值
                    tgcStep = TestcaseHttpStep()
                    tgcStep.copy(tgcSteps[j])

                    #TODO 验证步骤字段

                    #TODO 处理前置变量和关键字
                    varsPool = cp.get_varspool(varsPool,tgcStep.varsconf,env,db)
                    logging.debug("varsPool:%s" % varsPool)

                    #TODO 处理数据初始化、数据回复、head、host、uri、method、params、url等变量替换  关键字替换
                    # =================对data、param、expect等进行变量替换。============================
                    # 参数处理sqls_string_init、sqls_string_recover、params、expect 的参数 进行参数带入处理
                    tgcStep.protocol = cp.replace_vars(tgcStep.protocol, varsPool)
                    tgcStep.host = cp.replace_vars(tgcStep.host, varsPool)
                    tgcStep.method = cp.replace_vars(tgcStep.method, varsPool)
                    tgcStep.data_init = cp.replace_vars(tgcStep.data_init, varsPool)
                    tgcStep.data_recover = cp.replace_vars(tgcStep.data_recover, varsPool)
                    tgcStep.header = cp.replace_vars(tgcStep.header, varsPool)
                    tgcStep.url = cp.replace_vars(tgcStep.url, varsPool)
                    tgcStep.params = cp.replace_vars(tgcStep.params, varsPool)
                    # =====变量替换处理结束============================================================
                    ##===================处理token相关关键字===========================================
                    # TODO 处理token关键字
                    loopstep,varsPool,tgcStep = self.process_kw_about_tokens(varsPool,tgcStep,appapiUri,env,db)
                    logging.debug("varsPoolAfterProcessTokens:%s" % varsPool)
                    if loopstep == False: continue
                    #-====================处理token等结束==============================================
                    #TODO 执行HTTP请求
                    tmphost = tgcStep.host.lower()
                    if tmphost == SUPPORT_CONSOLE_URI:
                        tmphost = supportConsoleUri
                    elif tmphost == PC_DISTRIBUTE_URI:
                        tmphost = pcDistributeUri
                    elif tmphost == APPAPI_URI:
                        tmphost = appapiUri
                    elif tmphost == SAAS_URI:
                        tmphost = saasUri
                    elif tmphost == WEIDIAN_URI:
                        tmphost = weidianUri
                    elif tmphost == SETTLEMENT_URI:
                        tmphost = settlementUri
                    else:
                        print "需要检验tmphost符合 http://ipordomain:port 的形式。"
                    tgcStep.host = tmphost
                    tmpurl = tgcStep.url
                    tmpheader = tgcStep.header
                    tmpparams = tgcStep.params
                    if tgcStep.method.lower() == POST:
                        #do post
                        reqRes = HttpProcesser(tmphost,tmpurl,tmpheader,tmpparams,requestSession).post()
                    elif tgcStep.method.lower() == GET:
                        reqRes = HttpProcesser(tmphost, tmpurl, tmpheader, tmpparams, requestSession).get()
                    else:
                        tgcStep.setError(u"仅支持POST或者GET请求。")

                    #TODO 处理后置变量和关键字
                    varsPool = cp.get_varspool(varsPool,tgcStep.varsconf_result,env,db)
                    logging.debug("varsPool222:%s" % varsPool)

                    #TODO 处理预期结果和预期数据库相关变量替换 关键字替换
                    tgcStep.expect = cp.replace_vars(tgcStep.expect, varsPool)
                    #TODO 对替换后的预期结果和数据库预期进行断言
                    tgcStep.setPass(reqRes.text, "测试通过j%d" % j, "300ms")

                    #TODO 将此步骤更新到步骤列表
                    tgcSteps[j] = tgcStep

                #TODO 已执行完所有步骤
                #TODO 将步骤结果赋值给tgc
                tgc.tgcStepList = tgcSteps

                #TODO 根据tgcStepList的结果给tgcDesc赋值
                total_perform_time = "10000ms"
                for indexStepOnGenerateResult in range(0,len(tgcSteps)):
                    tmpStepInGeneResult = TestcaseHttpStep()
                    tmpStepInGeneResult.copy(tgcSteps[indexStepOnGenerateResult])
                    if tmpStepInGeneResult.test_result == ERROR :
                        tgcDesc.setError(tmpStepInGeneResult.return_msg)
                        break
                    elif tmpStepInGeneResult.test_result == FAIL :
                        tgcDesc.setFail(tmpStepInGeneResult.return_msg,u"FAIL:步骤%d测试未通过。" % indexStepOnGenerateResult,total_perform_time)
                        break
                    elif tmpStepInGeneResult.test_result == PASS:
                        tgcDesc.setPass(tmpStepInGeneResult.return_msg, u"PASS:测试通过。",total_perform_time)
                #TODO 将tgcDesc赋值给tgc
                tgc.tgcDesc = tgcDesc

                #TODO 将tgc赋值给组合用例数组group_case_list
                group_case_list[i] = tgc

            except Exception,e:
                logging.debug(traceback.format_exc())
                logging.debug(e)
            finally:
                logging.debug("")

        return group_case_list

    def replace_GET_TOKEN2(self, params, token):
        find_start_tag = "GET_TOKEN("
        find_end_tag = ")"
        startpos = params.find(find_start_tag)  # 不存在是-1
        if startpos == -1: return params
        endpos = params.find(find_end_tag,startpos)
        return params.replace(params[startpos:endpos+len(find_end_tag)], token)

    def replace_GET_TOKEN(self,params, token):
        """
        NOW_FORMAT(%Y-%m-%d %H:%M:%S)
        """
        find_start_tag = "GET_TOKEN("
        find_end_tag = ")"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params
        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                continue
            else:
                #开始替换format
                try:
                    substr_tobe_replace =  params_splited[i+1][0:Dpos+len(find_end_tag)]
                    params_splited[i+1] = params_splited[i+1].replace(substr_tobe_replace,token)
                except Exception, e:
                    params_splited[i + 1] = params_splited[i+1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_GET_COMMON_TOKEN(self,params, token):
        """
        NOW_FORMAT(%Y-%m-%d %H:%M:%S)
        """
        find_start_tag = "GET_COMMON_TOKEN("
        find_end_tag = ")"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params
        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                continue
            else:
                #开始替换format
                try:
                    substr_tobe_replace =  params_splited[i+1][0:Dpos+len(find_end_tag)]
                    params_splited[i+1] = params_splited[i+1].replace(substr_tobe_replace,token)
                except Exception, e:
                    params_splited[i + 1] = params_splited[i+1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_GET_DATA(self, params, data):
        find_start_tag = "GET_DATA{("
        find_end_tag = ")}"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params
        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                continue
            else:
                #开始替换format
                try:
                    substr_tobe_replace =  params_splited[i+1][0:Dpos+len(find_end_tag)]
                    params_splited[i+1] = params_splited[i+1].replace(substr_tobe_replace,data)
                except Exception, e:
                    params_splited[i + 1] = params_splited[i+1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_GET_SIGN(self, params, sign):
        find_start_tag = "GET_SIGN("
        find_end_tag = ")"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params
        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                continue
            else:
                #开始替换format
                try:
                    substr_tobe_replace =  params_splited[i+1][0:Dpos+len(find_end_tag)]
                    params_splited[i+1] = params_splited[i+1].replace(substr_tobe_replace,sign)
                except Exception, e:
                    params_splited[i + 1] = params_splited[i+1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def process_kw_about_tokens(self,varsPool,tgcStep,appapiUri,env,db):
        cp = CommonProcess()
        is_get_token = False
        try:
            req = requests.session()
            token_value = varsPool['KEY_token'].strip()
            logging.info(u"开始获取token。")
            if "GET_TOKEN(" in token_value:
                token_params = cp.get_sub_string(token_value, "GET_TOKEN(", ")")
                token_params_list = token_params.strip().split(",")
                if len(token_params_list) != 4:
                    tgcStep.setError(u"CASE_ERROR: GET_TOKEN()参数错误，应该为GET_TOKEN(type,resellerId,username,password)。")
                    return False, varsPool, tgcStep
                login_host = appapiUri
                login_url = "/appapi/user/login"
                rid = token_params_list[1]  # 加入header中 resellerId
                login_header = """{"rid":"%s"}""" % rid
                rstype = token_params_list[0]
                username = token_params_list[2]
                password = token_params_list[3]
                data = """{"username":"%s","password":"%s","type":%s,"version":"2.0.1",}""" % (
                username, password, rstype)
                logging.info(u"登录数据为：%s" % data)
                data_encode = quote(base64.encodestring(data))
                sign = ServiceTool.md5(data + rid)
                login_params = """data=%s&sign=%s""" % (data_encode, sign)
                login_res = HttpProcesser(login_host, login_url, login_header, login_params,
                                          sess=req).post()
                login_return_json = login_res.text
                if login_res.status_code != 200:
                    tgcStep.setError(u"CASE_ERROR: GET_TOKEN()失败，返回状态码错误，返回码是%d。" % login_res.status_code)
                    return False, varsPool, tgcStep
                try:
                    login_return_dict = json.loads(login_return_json)
                    final_token = login_return_dict['responseBody']['token']
                    logging.info(u"得到token是：%s" % final_token)
                    # 重新处理varsconf
                    tgcStep.varsconf = self.replace_GET_TOKEN(tgcStep.varsconf, final_token)
                    varsPool = cp.get_varspool(varsPool, tgcStep.varsconf, env, db)
                    logging.debug("varsPool:%s" % varsPool)
                    is_get_token = True
                except Exception, e:
                    retTmpMsg = u"CASE_ERROR: GET_TOKEN()失败[用户名：%s 密码：%s rid:%s 类型：%s]，没有返回有效JSON，返回内容为%s。" % (
                    username, password, rid, rstype, login_return_json)
                    tgcStep.setError(retTmpMsg)
                    return False, varsPool, tgcStep
        except Exception, e:
            logging.debug(u"HttpService.py: execute_testcases:没有KEY_token变量，本次请求不需要获取KEY_token。")

        is_get_rid = False
        try:
            rid_value = varsPool['KEY_rid'].strip()
            is_get_rid = True
        except Exception, e:
            logging.debug(u"HttpService.py: execute_testcases:没有KEY_rid变量，本次请求不需要获取rid。")

        is_get_data = False
        try:
            data_value = varsPool['KEY_data'].strip()
            logging.info(u"开始处理data。")
            if "GET_DATA{(" in data_value:
                data_sub = cp.get_sub_string(data_value, "GET_DATA{(", ")}")
                if data_sub != False and data_sub.strip() != "":
                    logging.info(u"请求的data是%s " % data_sub.strip())
                    final_data = ServiceTool.encryptData(data_sub)  # .replace("%0A",'')
                    logging.info(u"加密后的data是%s " % final_data)
                    tgcStep.varsconf = self.replace_GET_DATA(tgcStep.varsconf, final_data)
                    varsPool = cp.get_varspool(varsPool, tgcStep.varsconf, env, db)
                    logging.debug("varsPool:%s" % varsPool)
                    is_get_data = True
            else:
                logging.debug(u"没有data 处理需求")

            if is_get_data:
                try:
                    sign_value = varsPool['KEY_sign']
                    logging.info(u"开始处理sign。")
                    if "GET_SIGN()" == sign_value.strip():
                        if is_get_token:
                            sign_pre = "%s%s" % (unquote(final_data), final_token)
                        elif is_get_rid:
                            sign_pre = "%s%s" % (unquote(final_data), rid_value)
                        else:
                            tgcStep.setError(u"CASE_ERROR: 变量中有KEY_data时，必须要有KEY_token或者KEY_rid。")
                            return False, varsPool, tgcStep
                        final_sign = ServiceTool.md5(str(sign_pre))
                        tgcStep.varsconf = self.replace_GET_SIGN(tgcStep.varsconf, final_sign)
                        varsPool = cp.get_varspool(varsPool, tgcStep.varsconf, env, db)
                        logging.debug("varsPool:%s" % varsPool)
                    else:
                        logging.debug(u"没有sign处理需求")
                except Exception, e:
                    logging.debug(u"HttpService.py: execute_testcases:没有sign变量，本次请求不需要处理sign。")
        except Exception, e:
            logging.debug(u"HttpService.py: execute_testcases:没有KEY_data变量，本次请求不需要处理data。")

        is_common_token_get = False
        try:
            common_token_value = varsPool['COMMON_token'].strip()
            logging.info(u"开始获取COMMON_token。")
            # COMMON_token=GET_COMMON_TOKEN("host","url","method","params","token_path");
            if "GET_COMMON_TOKEN(" in common_token_value:
                token_params = cp.get_sub_string(common_token_value, "GET_COMMON_TOKEN(", ")")
                token_params_list = token_params.strip().split(",")
                print token_params_list
                if len(token_params_list) != 5:
                    tgcStep.setError(
                        u"CASE_ERROR: GET_COMMON_TOKEN()参数错误，GET_COMMON_TOKEN(host,url,method,params,token_path)。\n "
                        u"host若使用系统配置填写default。\n"
                        u"url为路径，例如/user/login。\n"
                        u"method为get或者post。\n"
                        u"params为参数组合，例如username=testuser&password=testpwd。\n"
                        u"token_path为返回json的token路径，例如返回json{'token':'df3eDfe322SEDFEZsdx'}，那么token_path填入['token']。\n"
                        u"COMMON_token变量举例：COMMON_token=GET_COMMON_TOKEN(http://www.test.com,/user/login,post,username=testuser&password=123456,['token']);")
                    return False, varsPool, tgcStep

                login_host = token_params_list[0] == DATA_DEFAULT and appapiUri or token_params_list[0]
                login_url = token_params_list[1]
                login_method = token_params_list[2]
                login_params = token_params_list[3]
                token_path = token_params_list[4]
                login_header = "{}"

                logging.debug("%s:%s" % (login_host, login_url))

                if login_method.lower() == POST:
                    login_res = HttpProcesser(login_host, login_url, login_header, login_params, sess=req).post()
                elif login_method.lower() == GET:
                    login_res = HttpProcesser(login_host, login_url, login_header, login_params, sess=req).get()

                logging.debug("%s:%s" % (login_res.text, login_res.status_code))
                login_return_json = login_res.text

                if login_res.status_code != 200:
                    tgcStep.setError(u"CASE_ERROR: GET_COMMON_TOKEN()失败，返回状态码错误，返回码是%d。" % login_res.status_code)
                    return False, varsPool, tgcStep
                try:
                    login_return_dict = json.loads(login_return_json)
                    final_token = eval("login_return_dict%s" % token_path)
                    logging.info(u"得到token是：%s" % final_token)
                    tgcStep.varsconf = self.replace_GET_COMMON_TOKEN(tgcStep.varsconf, final_token)
                    varsPool = cp.get_varspool(varsPool, tgcStep.varsconf, env, db)
                    is_common_token_get = True
                except Exception, e:
                    tgcStep.setError(
                        u"CASE_ERROR: GET_COMMON_TOKEN()失败[HOST:%s URL:%s METHOD:%s PARAMS:%s TOKEN_PATH:%s]，没有返回有效JSON，返回内容为%s。" % (
                            login_host, login_url,
                            login_method, login_params,
                            token_path, login_return_json))
                    return False, varsPool, tgcStep
        except Exception, e:
            logging.debug(u"错误信息：%s" % e.message)
            logging.debug(u"HttpService.py: execute_testcases:没有COMMON_token变量，本次请求不需要获取COMMON_token。")
        finally:
            return  True, varsPool, tgcStep

if __name__ == "__main__":
    # from ExcelProcess.ExcelProcess import ExcelProcess
    evalString = "a=EVAL{(  math(abc)  )}"
    evalString = "seatChartId=EVAL{( SQL_SELECT{( select max(id) from stock.stock_seat_chart where id=1)}+1)}"

