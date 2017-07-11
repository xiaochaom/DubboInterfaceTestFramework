# coding:utf-8
"""
Author:王吉亮
Date:20161201
"""
import sys,logging,re,random,datetime,chardet, json, time,redis

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")

from Config.GlobalConf import ServiceConf

class CommonProcess(object):

    def get_sub_string(self,params,start,end):
        params = params.strip()
        find_start_tag = start
        find_end_tag = end
        spos = params.find(find_start_tag)
        if spos == -1:  # 没有发现关键字 SQL_SELECT()
            return ''
        epos = params.find(find_end_tag, spos)
        if epos == -1:  # 没有发现关键字 find_end_tag
            return ''
        return params[spos + len(find_start_tag):epos]

    def validate_sql_strings(self, sqls_string, db):
        if sqls_string == "default":
            #logging.debug( u"CommonProcess.py: data sqls is %s." % sqls_string )
            return True
        init_data_sql_list = sqls_string.split(';')
        return_value = True
        for sql in init_data_sql_list:
            if sql.strip() == '': continue
            sql_effect_rows = db.get_effected_rows_count(sql)
            logging.info( u"CommonProcess.py: process_sql_strings: SQL语句[%s]影响数据库行数：%d" % (sql, sql_effect_rows))
            if sql_effect_rows > ServiceConf().sql_effect_lines : # or sql_effect_rows == -1:
                #logging.info( u"CommonProcess.py: execute_testcases: SQL语句影响数据库行数大于1，禁止执行！")
                return False
        return return_value

    def execute_sql_strings(self, sqls_string, db):
        if sqls_string == "default":
            #logging.debug( u"data sqls is %s." % sqls_string )
            return True
        init_data_sql_list = sqls_string.split(';')
        return_value = True
        for sql in init_data_sql_list:
            if sql.strip() == '': continue
            logging.debug( u"CommonProcess.py: execute_sql_strings: 执行SQL[%s]" % sql)
            exesqlret = db.execute_sql(sql)
            logging.debug(u"CommonProcess.py: execute_sql_strings: 执行SQL[%s]返回%s" %(sql,exesqlret) )
            if type(exesqlret) == type(()) :
                try:
                    if exesqlret[0] == 1054:
                        return False
                except Exception,e:
                    pass
        return return_value

    def replace_NOW_D(self,params):
        find_start_tag = "NOW()"
        find_end_tag = "D"
        nowplus_startpos = params.find(find_start_tag)  # 不存在是-1
        if nowplus_startpos == -1: return params
        #nowplus_endpos = params.find(find_end_tag, nowplus_startpos)  # 如果endpos没有那么就是只写当前日期
        #value_tobe_process = params[nowplus_startpos + len(find_start_tag):nowplus_endpos]
        sysnow = datetime.datetime.now().strftime('%Y%m%d')  # ('%Y-%m-%d %H:%M:%S')
        params_splited = params.split(find_start_tag)
        len_params_splited =  len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params

        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                params_splited[i+1] = sysnow + params_splited[i+1]
            else:
                value_tobe_process = params_splited[i+1][:Dpos]
                try:
                    if value_tobe_process[0] == "+":
                        tobe_plus_value = int(value_tobe_process[1:])
                        tobe_day = (datetime.datetime.now() + datetime.timedelta(days=tobe_plus_value)).strftime("%Y%m%d")
                        params_splited[i + 1] = params_splited[i+1].replace("+"+str(tobe_plus_value)+"D",tobe_day,1)
                    elif value_tobe_process[0] == "-":
                        tobe_plus_value = int(value_tobe_process[1:])
                        tobe_day = (datetime.datetime.now() - datetime.timedelta(days=tobe_plus_value)).strftime("%Y%m%d")
                        params_splited[i + 1] = params_splited[i + 1].replace("-"+str(tobe_plus_value) + "D", tobe_day, 1)
                    else:
                        params_splited[i+1] = sysnow + params_splited[i+1]
                except Exception, e:
                    params_splited[i + 1] = sysnow + params_splited[i + 1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_NOW_FORMAT(self,params):
        """
        NOW_FORMAT(%Y-%m-%d %H:%M:%S)
        """
        find_start_tag = "NOW_FORMAT("
        find_end_tag = ")"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params
        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                params_splited[i+1] = find_start_tag + params_splited[i+1]
                continue
            else:
                #开始替换format
                try:
                    strftime = params_splited[i+1][:Dpos]
                    sysnow = datetime.datetime.now().strftime(strftime)  # ('%Y-%m-%d %H:%M:%S')
                    substr_tobe_replace =  strftime + find_end_tag
                    params_splited[i+1] = params_splited[i+1].replace(substr_tobe_replace,sysnow)
                except Exception, e:
                    params_splited[i + 1] = find_start_tag + params_splited[i + 1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_NOW_FORMAT_D(self,params):
        """
        NOW_FORMAT(%Y-%m-%d %H:%M:%S)
        """
        find_start_tag = "NOW_FORMAT("
        find_end_tag = ")"
        find_D_tag = "D"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params

        for i in range(0,len_params_splited-1):
            endpos = params_splited[i+1].find(find_end_tag)
            if endpos == -1:
                params_splited[i + 1] = find_start_tag + params_splited[i + 1]
                continue
            else:
                #开始替换format
                try:
                    strftime = params_splited[i+1][:endpos]
                    #开始查找+1D  -1D等
                    Dpos = params_splited[i + 1].find(find_D_tag,endpos)
                    if Dpos == -1:
                        sysnow = datetime.datetime.now().strftime(strftime)
                        substr_tobe_replace = strftime + find_end_tag
                        params_splited[i + 1] = params_splited[i + 1].replace(substr_tobe_replace, sysnow)
                    else:
                        # 处理加减日期
                        value_tobe_process = params_splited[i + 1][endpos+len(find_end_tag):Dpos].strip()
                        try:
                            if value_tobe_process[0] == "+":
                                tobe_plus_value = int(value_tobe_process[1:])
                                sysnow = (datetime.datetime.now() + datetime.timedelta(days=tobe_plus_value)).strftime(strftime)
                                substr_tobe_replace =  params_splited[i+1][:Dpos+len(find_D_tag)]
                                params_splited[i + 1] = params_splited[i + 1].replace(substr_tobe_replace, sysnow)
                            elif value_tobe_process[0] == "-":
                                tobe_plus_value = int(value_tobe_process[1:])
                                sysnow = (datetime.datetime.now() - datetime.timedelta(days=tobe_plus_value)).strftime(strftime)
                                substr_tobe_replace =  params_splited[i+1][:Dpos+len(find_D_tag)]
                                params_splited[i + 1] = params_splited[i + 1].replace(substr_tobe_replace, sysnow)
                            else:
                                sysnow = datetime.datetime.now().strftime(strftime)
                                substr_tobe_replace = strftime + find_end_tag
                                params_splited[i + 1] = params_splited[i + 1].replace(substr_tobe_replace, sysnow)
                        except Exception, e:
                            params_splited[i + 1] = find_start_tag + params_splited[i + 1]
                except Exception, e:
                    params_splited[i + 1] = find_start_tag + params_splited[i + 1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_NOW_TIMESTAMP(self,params):
        find_start_tag = "NOW_TIMESTAMP()"
        find_end_tag = "S"
        nowplus_startpos = params.find(find_start_tag)  # 不存在是-1
        if nowplus_startpos == -1: return params
        # nowplus_endpos = params.find(find_end_tag, nowplus_startpos)  # 如果endpos没有那么就是只写当前日期
        # value_tobe_process = params[nowplus_startpos + len(find_start_tag):nowplus_endpos]
        sysnow = str(long(time.time()))  # ('时间戳')
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1:  # 没有发现关键字 NOW()
            return params

        for i in range(0, len_params_splited - 1):
            Dpos = params_splited[i + 1].find(find_end_tag)
            if Dpos == -1:
                params_splited[i + 1] = sysnow + params_splited[i + 1]
            else:
                value_tobe_process = params_splited[i + 1][:Dpos]
                try:
                    if value_tobe_process[0] == "+":
                        tobe_plus_value = long(value_tobe_process[1:])
                        tobe_day = str(long(sysnow) + tobe_plus_value)
                        params_splited[i + 1] = params_splited[i + 1].replace("+" + str(tobe_plus_value) + find_end_tag,
                                                                              tobe_day, 1)
                    elif value_tobe_process[0] == "-":
                        tobe_plus_value = long(value_tobe_process[1:])
                        tobe_day = str(long(sysnow) - tobe_plus_value)
                        params_splited[i + 1] = params_splited[i + 1].replace("-" + str(tobe_plus_value) + find_end_tag,
                                                                              tobe_day, 1)
                    else:
                        params_splited[i + 1] = sysnow + params_splited[i + 1]
                except Exception, e:
                    params_splited[i + 1] = sysnow + params_splited[i + 1]
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def get_vars_by_varsconf(self,varsconf,env):
        if type(varsconf).__name__ != "unicode" and type(varsconf).__name__ != "ascii":
            varsconf = unicode(varsconf, chardet.detect(varsconf)['encoding'])
        varsconfstr=""

        start_tag = "[CONF=common]"
        end_tag = "[ENDCONF]"
        find_start = varsconf.find(start_tag)
        if find_start >= 0 :
            find_end = varsconf.find(end_tag,find_start)
            if find_end >=0 :
                varsconfstr = varsconfstr + varsconf[find_start+len(start_tag):find_end].strip()

        start_tag = "[CONF=%s]" % env
        end_tag = "[ENDCONF]"
        find_start = varsconf.find(start_tag)
        if find_start >= 0 :
            find_end = varsconf.find(end_tag,find_start)
            if find_end >=0 :
                varsconfstr = varsconfstr + varsconf[find_start+len(start_tag):find_end].strip()

        return varsconfstr

    def get_var_dict_by_varstring(self,varstring):
        var_dict = {}
        var_list = varstring.split(';')
        for var in var_list:
            if var.strip()!='':
                tmplist = var.split("=")
                if len(tmplist) >= 2:
                    var_dict[tmplist[0].strip()] = tmplist[1].strip()
                    for i in range(2,len(tmplist)):
                        var_dict[tmplist[0].strip()] = var_dict[tmplist[0].strip()] + "=" + tmplist[i].strip()
                else:
                    #没有发现等于号
                    var_dict[tmplist[0].strip()] = ""
        for k,v in var_dict.items():
            tmpvar = "$var[%s]" % k
            if tmpvar in v:
                var_dict[k] = "不可自己给自己赋值"
        return var_dict

    def set_varspool(self,varspool = {},var_dict = {}):
        for k,v in var_dict.items():
            varspool[k] = v
        return varspool

    def replace_vars(self,to_be_processed_string,var_dict={}):
        processed_string = to_be_processed_string
        for k,v in var_dict.items():
            processed_string = processed_string.replace("$var[%s]" % k,v)
        return processed_string

    def process_vars(self, to_be_processed_string, varsconf, env):
        varsstring = self.get_vars_by_varsconf(varsconf, env)
        var_dict = self.get_var_dict_by_varstring(varsstring)
        return self.replace_vars(to_be_processed_string, var_dict)

    def replace_SQL_SELECT(self,params,db):
        """
        SQL_SELECT{( select total_num from stock.stock where id=233 )}  #有且仅有一行数据会有正确返回，否则不进行任何替换
        """
        logging.debug( u"CommonProcess.py: replace_SQL_SELECT:开始替换SQL_SELECT{( sqls )}")
        find_start_tag = "SQL_SELECT{("
        find_end_tag = ")}"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        #print params_splited
        if len_params_splited == 1: #没有发现关键字 find_start_tag
            logging.debug(u"CommonProcess.py: replace_SQL_SELECT:Length:1")
            return params

        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            logging.debug(u"CommonProcess.py: replace_SQL_SELECT:Endpos:%d" % Dpos)
            if Dpos == -1:
                params_splited[i + 1] = find_start_tag + params_splited[i+1]
                continue
            else:
                try:
                    sqlstring = params_splited[i+1][:Dpos] #sqlsting
                    logging.debug(u"CommonProcess.py: replace_SQL_SELECT:开始替换sql：%s" % sqlstring)
                    if db.get_effected_rows_count(sqlstring) != 1:
                        params_splited[i + 1] = find_start_tag + params_splited[i + 1]
                        continue
                    substr_tobe_replace = sqlstring + find_end_tag
                    sqlvalue = str(db.execute_sql(sqlstring)[0][0])
                    logging.debug(u"CommonProcess.py: replace_SQL_SELECT:开始替换sql_value：%s " % sqlvalue)
                    params_splited[i + 1] = params_splited[i + 1].replace(substr_tobe_replace, sqlvalue)
                    #print params_splited[i+1]
                except Exception, e:
                    #print "error %s" % e
                    logging.debug(u"CommonProcess.py: replace_SQL_SELECT:Error: %s" % e)
                    params_splited[i + 1] = find_start_tag + params_splited[i + 1]
                    continue
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def replace_EVAL(self,params):
        """
        EVAL{(random.randint(10,20))}
        """
        logging.debug(u"CommonProcess.py: replace_EVAL:开始替换EVAL{( python_systax )}")
        find_start_tag = "EVAL{("
        find_end_tag = ")}"
        params_splited = params.split(find_start_tag)
        len_params_splited = len(params_splited)
        if len_params_splited == 1: #没有发现关键字 NOW()
            return params

        for i in range(0,len_params_splited-1):
            Dpos = params_splited[i+1].find(find_end_tag)
            if Dpos == -1:
                params_splited[i + 1] = find_start_tag + params_splited[i + 1]
                continue
            else:
                try:
                    evalstring = params_splited[i+1][:Dpos]
                    evalue = str(eval(evalstring))
                    substr_tobe_replace =  evalstring + find_end_tag
                    params_splited[i+1] = params_splited[i+1].replace(substr_tobe_replace,evalue)
                except Exception, e:
                    params_splited[i + 1] = find_start_tag + params_splited[i + 1]
                    continue
        new_params = ""
        for value in params_splited:
            new_params = new_params + value
        return new_params

    def process_SQL_SELECT(self,params,db):
        find_start_tag = "SQL_SELECT{("
        find_end_tag = ")}"
        sql_string = self.get_sub_string(params,find_start_tag,find_end_tag).strip()
        logging.debug(u"CommonProcess.py: process_SQL_SELECT: 得到SQL：%s" % sql_string)
        if sql_string == '': return 1
        sql_start = sql_string.strip()[:6]
        if sql_start.lower() != "select":
            return 2
        effectCount = db.get_effected_rows_count(sql_string)
        logging.debug(u"CommonProcess.py: process_SQL_SELECT: 影响行数：%d" % effectCount)
        if effectCount != 1: return 3
        return db.execute_sql(sql_string)[0]

    def assert_dbdata(self,dbdata_expects,db):
        dbdata_expect_list = dbdata_expects.strip().split(";")
        ret_list = [u"",u""]
        for dbdata_expect in dbdata_expect_list:
            if dbdata_expect.strip() == "" : continue
            db_result = self.process_SQL_SELECT(dbdata_expect, db)
            if type(db_result) == type(1):
                if db_result == 1:
                    ret_list[0] = u"CASE_ERROR: 用例错误，请检查格式。\n" + ret_list[0]
                    ret_list[1] = u"ERROR"
                    return ret_list
                elif db_result == 2:
                    ret_list[0] = u"CASE_ERROR: 数据库断言错误，必须是SELECT语句。\n" + ret_list[0]
                    ret_list[1] = u"ERROR"
                    return ret_list
                elif db_result == 3:
                    ret_list[0] = u"FAIL: 数据库断言时，SELECT语句查询的结果必须有且仅有1行。\n" + ret_list[0]
                    ret_list[1] = u"FAIL"
                    return ret_list
                else:
                    ret_list[0] = u"CASE_ERROR: 不确定的数据库断言返回错误。\n" + ret_list[0]
                    ret_list[1] = u"ERROR"
                    return ret_list
            logging.debug(u"CommonProcess.py: assert_dbdata: 数据库预期[%s]的查询结果是[%s]" % (dbdata_expect,db_result) )
            ret_list[0] = ret_list[0] + (u"数据库预期[%s]的查询结果是[%s]。\n" % (dbdata_expect,db_result) )
            db_values = db_result
            len_db_values = len(db_values)
            equal_split_list = dbdata_expect.split("==")  # 等于判断
            unequal_split_list = dbdata_expect.split("!=")  # 不等于判断
            le_split_list = dbdata_expect.split(">=")  # 大于等于 large equal
            l_split_list = dbdata_expect.split(">")  # 大于 large
            se_split_list = dbdata_expect.split("<=")  # 小于等于 small equal
            s_split_list = dbdata_expect.split("<")  # 小于 small
            if len(equal_split_list)==2:
                #进入==判断
                e_list = equal_split_list[1].split(",")
                if len(e_list) != len_db_values:
                    ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据长度与断言结果数据长度不一致。\n"
                    ret_list[1] = u"FAIL"
                    return ret_list
                for i in range(0,len_db_values):
                    if str(db_values[i]).strip() != str(e_list[i]).strip():
                        ret_list[0] = u"FAIL: "  + ret_list[0] + u"数据库断言失败，查询结果返回数据与预期数据不一致。\n"
                        ret_list[1] = u"FAIL"
                        return ret_list
                ret_list[0] =  ret_list[0] + (u"数据库断言[%s]成功，查询结果返回数据与预期数据一致。\n" % dbdata_expect)
            elif len(unequal_split_list)==2:
                #进入!=判断
                e_list = unequal_split_list[1].split(",")
                if len(e_list) != len_db_values:
                    ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据长度与断言结果数据长度不一致。\n"
                    ret_list[1] = u"FAIL"
                    return ret_list
                for i in range(0,len_db_values):
                    if str(db_values[i]).strip() == str(e_list[i]).strip():
                        ret_list[0] = u"FAIL: "  + ret_list[0] + u"数据库断言失败，查询结果返回数据与预期数据不一致。\n"
                        ret_list[1] = u"FAIL"
                        return ret_list
                ret_list[0] =  ret_list[0] + (u"数据库断言[%s]成功，查询结果返回数据与预期数据一致。\n" % dbdata_expect)
            elif len(le_split_list)==2:
                #进入>=判断
                e_list = le_split_list[1].split(",")
                if len(e_list) != len_db_values:
                    ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据长度与断言结果数据长度不一致。\n"
                    ret_list[1] = u"FAIL"
                    return ret_list
                for i in range(0,len_db_values):
                    try:
                        if long(db_values[i]) < long(e_list[i].strip()):
                            ret_list[0] = u"FAIL: "  + ret_list[0] + u"数据库断言失败，查询结果返回数据与预期数据不一致。\n"
                            ret_list[1] = u"FAIL"
                            return ret_list
                    except Exception, e:
                        ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据或者预期数据不能转换为整数。\n"
                        ret_list[1] = u"FAIL"
                        return ret_list
                ret_list[0] =  ret_list[0] + (u"数据库断言[%s]成功，查询结果返回数据与预期数据一致。\n" % dbdata_expect)
            elif len(l_split_list)==2:
                #进入>判断
                e_list = l_split_list[1].split(",")
                if len(e_list) != len_db_values:
                    ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据长度与断言结果数据长度不一致。\n"
                    ret_list[1] = u"FAIL"
                    return ret_list
                for i in range(0,len_db_values):
                    try:
                        if long(db_values[i]) <= long(e_list[i].strip()):
                            ret_list[0] = u"FAIL: "  + ret_list[0] + u"数据库断言失败，查询结果返回数据与预期数据不一致。\n"
                            ret_list[1] = u"FAIL"
                            return ret_list
                    except Exception, e:
                        ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据或者预期数据不能转换为整数。\n"
                        ret_list[1] = u"FAIL"
                        return ret_list
                ret_list[0] =  ret_list[0] + (u"数据库断言[%s]成功，查询结果返回数据与预期数据一致。\n" % dbdata_expect)
            elif len(se_split_list)==2:
                #进入<=判断
                e_list = se_split_list[1].split(",")
                if len(e_list) != len_db_values:
                    ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据长度与断言结果数据长度不一致。\n"
                    ret_list[1] = u"FAIL"
                    return ret_list
                for i in range(0,len_db_values):
                    try:
                        if long(db_values[i]) > long(e_list[i].strip()):
                            ret_list[0] = u"FAIL: "  + ret_list[0] + u"数据库断言失败，查询结果返回数据与预期数据不一致。\n"
                            ret_list[1] = u"FAIL"
                            return ret_list
                    except Exception, e:
                        ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据或者预期数据不能转换为整数。\n"
                        ret_list[1] = u"FAIL"
                        return ret_list
                ret_list[0] =  ret_list[0] + (u"数据库断言[%s]成功，查询结果返回数据与预期数据一致。\n" % dbdata_expect)
            elif len(s_split_list)==2:
                #进入<判断
                e_list = s_split_list[1].split(",")
                if len(e_list) != len_db_values:
                    ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据长度与断言结果数据长度不一致。\n"
                    ret_list[1] = u"FAIL"
                    return ret_list
                for i in range(0,len_db_values):
                    try:
                        if long(db_values[i]) >= long(e_list[i].strip()):
                            ret_list[0] = u"FAIL: "  + ret_list[0] + u"数据库断言失败，查询结果返回数据与预期数据不一致。\n"
                            ret_list[1] = u"FAIL"
                            return ret_list
                    except Exception, e:
                        ret_list[0] = u"FAIL: " + ret_list[0] + u"数据库断言失败，查询结果返回数据或者预期数据不能转换为整数。\n"
                        ret_list[1] = u"FAIL"
                        return ret_list
                ret_list[0] =  ret_list[0] + (u"数据库断言[%s]成功，查询结果返回数据与预期数据一致。\n" % dbdata_expect)
            else:
                ret_list[0] = u"FAIL: 数据库断言失败，只能进行== != >= > <= =这六种断言方式。\n" + ret_list[0]
                ret_list[1] = u"FAIL"
                return ret_list
        ret_list[0] = u"PASS: 数据库断言全部成功！\n" + ret_list[0]
        ret_list[1] = u"PASS"
        return ret_list

    def assert_result_back(self, expect, return_msg):
        """
        断言预期结果和实际结果
        接受参数为expect, return_msg 两个字符串
        返回值为 code 断言结果 时间
        """
        # 首先要判断预期结果是否是JSON，还是字符串，如果是字符串，就测试返回结果是否保存字符串内容，异常返回是带字符串的
        expect = expect.strip()
        return_msg = return_msg.strip()
        actualList = return_msg.decode(chardet.detect(return_msg)['encoding']).split("elapsed:")
        perform_time = len(actualList) != 2 and "null" or actualList[1].split(".")[0].strip()
        # 遍历字典，比对结果
        failPointCount = [0]
        #定义一个变量，用来存储多个断言值不对的情况
        fail = ['']
        try:
            logging.debug(u"CommonProcess.py: assert_result: 预期结果：%s" % expect)
            logging.debug(u"CommonProcess.py: assert_result: 实际结果：%s" % return_msg)
            error_return_msg = return_msg.split(":")
            if  "ERROR" in error_return_msg[0] :
                return [return_msg,"ERROR","null"]
            logging.debug(u"CommonProcess.py: assert_result: 不是ERROR")
            if expect != "null":
                expectResultDict = json.loads(expect)
                #expect不是null，且是json字符串，要进行json递归断言。
            else:
                #expect是null，返回断言结果。
                if expect in return_msg:
                    return [u"PASS: 预期返回结果断言成功！".encode('utf8'), 'PASS', perform_time]
                else:
                    return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, return_msg), 'FAIL', perform_time]

            logging.debug(u"CommonProcess.py: assert_result: 已json loads 预期结果")
            #如果实际结果是json但是阶段后不是两截，说明返回值不对
            if len(actualList) != 2:
                return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, actualList[0]), 'FAIL','null']
            #对实际结果的第一节转json格式，如果转换失败，就抛错
            try:
                if actualList[0].strip().startswith('{') and actualList[0].strip().endswith('}'):
                    #说明实际结果是json
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果是json，开始loads。")
                    actualResultDict = json.loads(actualList[0].strip())
                    # 说明实际结果真的是json，loads成功。结构正确。
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果loads成功。")
                else:
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果不是json。")
                    if expect in actualList[0]:
                        return [u"PASS: 预期返回结果断言成功！", "PASS", perform_time]
                    else:
                        return [u"FAIL: 断言失败！", "FAIL", perform_time]
            except Exception, e:
                logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果json loads失败。")
                if expect in actualList[0]:
                    return [u"PASS: 预期返回结果断言成功！", "PASS", perform_time]
                else:
                    return [u"FAIL: 断言失败！", "FAIL", perform_time]
        except Exception, e:
            logging.debug(u"CommonProcess.py: assert_result_recur: 异常:%s" % e)
            if expect in return_msg:
                return [u"PASS: 预期返回结果断言成功！".encode('utf8'), 'PASS',perform_time]
            else:
                return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, return_msg), 'FAIL',perform_time]
        logging.debug( u"CommonProcess.py: assert_result: 实际结果：%s" % actualResultDict)
        logging.info( u"CommonProcess.py: assert_result: 接口使用时间:%s" % perform_time)
        #变量当前数组中的所有键值 判断是否相等
        #预期结果、实际结果都是json。下面开始key value的断言。
        def assert_string(expectValue,actualValue,current_key):
            # value不是字典，也不是list，不进行递归，只进行 相等判断 或者 数组长度判断。
            try:
                if str(actualValue) == str(expectValue):
                    # 如果值相等，那么退出循环，本次验证结束。
                    fail[0] = fail[0] + u"PASS: 断言成功！Key(%s)的值断言通过，预期%s，实际%s。\r\n".encode('utf8') % (current_key, str(expectValue), str(actualValue))
                    logging.info(u"CommonProcess.py: assert_result: 断言成功！Key(%s)的值断言通过，预期%s，实际%s。\r\n".encode('utf8') % (current_key, str(expectValue), str(actualValue)))
                else:
                    # 如果值不相等，判断expect的value是否是关键字LEN
                    expect_length = self.get_sub_string(str(expectValue), "LEN(", ")")
                    if expect_length != False and expect_length.strip() != "":
                        # 预期结果是断言长度
                        try:
                            int_expectlen = int(expect_length.strip())
                            # 预期长度获取成功，且转换成int成功。
                            actValue = actualValue
                            if type(actValue) != type([]):
                                logging.info(u"CommonProcess.py: assert_result: 实际值不是数组，无法断言。")
                                fail[0] = fail[0] + u"FAIL: 断言失败！实际值不是数组，无法断言。\r\n".encode('utf8')
                                failPointCount[0] += 1
                            # 开始判断长度。
                            int_actlen = len(actValue)
                            if int_actlen == int_expectlen:
                                fail[0] = fail[0] + u"PASS: 断言成功！Key(%s)的长度断言正确，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen)
                                logging.info(u"CommonProcess.py: assert_result: 断言成功！Key(%s)的长度断言正确，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen))
                            else:
                                logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的长度断言失败，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen))
                                fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的长度断言失败，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen)
                                failPointCount[0] += 1
                        except Exception, e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue))
                            fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue)
                            failPointCount[0] += 1
                    else:
                        # 预期结果不是断言长度，那么断言失败了。如果不是进行len判断，那么就是测试失败
                        logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue))
                        fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue)
                        failPointCount[0] += 1
            except Exception, e:
                logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果不存在这个key(%s)或者其他异常。")
                fail[0] = fail[0] + u"FAIL: 断言失败！实际结果不存在这个key(%s)或者其他异常。异常：%s".encode('utf8') % (current_key,e)
                failPointCount[0] += 1

        global_key=['']
        def recur_dict(value_recur, actual_value):
            tmptag = 0
            for t_key, t_value in value_recur.items():
                if tmptag > 0:
                    # [data  [id
                    list_gkey = global_key[0].split("]")
                    global_key[0] = ''
                    for i in range(0,len(list_gkey)-2):
                        global_key[0] = global_key[0] + list_gkey[i] + "]"
                tmptag += 1
                global_key[0] = global_key[0] + "[%s]" % t_key
                try:
                    if type(t_value) == type({}):
                        recur_dict(t_value, actual_value[t_key])
                        continue
                    elif type(t_value) == type([]):
                        # 判断list，是list进行list相关断言。
                        for ilistInRecur in range(0, len(t_value)):
                            if type(t_value[ilistInRecur]) == type({}):
                                global_key[0] = global_key[0] + "[%d]" % ilistInRecur
                                recur_dict(t_value[ilistInRecur], actual_value[t_key][ilistInRecur])
                            else:
                                assert_string(t_value[ilistInRecur],actual_value[t_key][ilistInRecur],global_key[0])
                        continue
                    else:
                        #不是dict 不是list ，进行string断言
                        try:
                            assert_string(value_recur[t_key],actual_value[t_key],global_key[0])
                        except Exception, e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                except Exception, e:
                    failPointCount[0] += 1
                    fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果没有这个key。异常：%s\r\n".encode('utf8') % (global_key[0], value_recur[t_key], e)

        for key, value in expectResultDict.items():
            global_key[0] = "[%s]" % key
            if type(value) == type({}):
                #value是字典，进行递归断言。
                try:
                    recur_dict(value,actualResultDict[key])
                except Exception, e:
                    failPointCount[0] += 1
                    fail[0] = fail[0] + u"FAIL: 断言失败！%s的值不对，预期结果%s，实际结果没有这个key。异常：%s\r\n".encode('utf8') % (key, value, e)
            elif type(value) == type([]):
                #判断list，是list进行list相关断言。
                #return [u"FAIL:进行LIST预期结果断言。", "FAIL", perform_time]
                for ilistAssert in range(0,len(value)):
                    if type(value[ilistAssert]) == type({}):
                        global_key[0] = global_key[0] + "[%d]" % ilistAssert
                        recur_dict(value[ilistAssert],actualResultDict[key][ilistAssert])
                    else:
                        assert_string(value[ilistAssert],actualResultDict[key][ilistAssert],global_key[0])
            else:
                # value不是字典，也不是list，不进行递归，只进行 相等判断 或者 数组长度判断。
                try:
                    assert_string(expectResultDict[key],actualResultDict[key],global_key[0])
                except Exception, e:
                    return [u"FAIL: 断言失败！实际结果不存在这个key或者其他异常。", "FAIL", perform_time]

        if failPointCount[0] == 0:
            logging.info( u"CommonProcess.py: assert_result_recur: PASS: 预期返回结果断言成功！")
            return [u"PASS: 返回内容全部断言通过。\r\n%s".encode('utf8') % fail[0],"PASS",perform_time]
        else:
            logging.info(u"CommonProcess.py: assert_result_recur: FAIL: 测试失败，断言失败点有%d个，请查看详情。" % failPointCount[0])
            return [u"FAIL: 返回内容最终断言失败。\r\n%s".encode('utf8') % fail[0],'FAIL',perform_time]

    def assert_result(self, expect, return_msg):
        """
        断言预期结果和实际结果
        接受参数为expect, return_msg 两个字符串
        返回值为 code 断言结果 时间
        """
        # 首先要判断预期结果是否是JSON，还是字符串，如果是字符串，就测试返回结果是否保存字符串内容，异常返回是带字符串的
        expect = expect.strip()
        return_msg = return_msg.strip()
        actualList = return_msg.decode(chardet.detect(return_msg)['encoding']).split("elapsed:")
        perform_time = len(actualList) != 2 and "null" or actualList[1].split(".")[0].strip()
        # 遍历字典，比对结果
        failPointCount = [0]
        #定义一个变量，用来存储多个断言值不对的情况
        fail = ['']
        try:
            logging.debug(u"CommonProcess.py: assert_result: 预期结果：%s" % expect)
            logging.debug(u"CommonProcess.py: assert_result: 实际结果：%s" % return_msg)
            error_return_msg = return_msg.split(":")
            if  "ERROR" in error_return_msg[0] :
                return [return_msg,"ERROR","null"]
            logging.debug(u"CommonProcess.py: assert_result: 不是ERROR")
            if expect != "null":
                isExpectInt = False
                isExpectFloat = False
                try:
                    intExpect = int(expect)
                    isExpectInt = True
                except Exception, e:
                    logging.info(u"预期结果是int。")
                try:
                    intExpect = float(expect)
                    isExpectFloat = True
                except Exception, e:
                    logging.info(u"预期结果是float。")

                if isExpectInt or isExpectFloat: raise ValueError(u"预期结果是int或者float。")

                expectResultDict = json.loads(expect)
                #expect不是null，且是json字符串，要进行json递归断言。
            else:
                #expect是null，返回断言结果。
                if expect in return_msg:
                    return [u"PASS: 预期返回结果断言成功！".encode('utf8'), 'PASS', perform_time]
                else:
                    return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, return_msg), 'FAIL', perform_time]

            logging.debug(u"CommonProcess.py: assert_result: 已json loads 预期结果")
            #如果实际结果是json但是阶段后不是两截，说明返回值不对
            if len(actualList) != 2:
                return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, actualList[0]), 'FAIL','null']
            #对实际结果的第一节转json格式，如果转换失败，就抛错
            try:
                if actualList[0].strip().startswith('{') and actualList[0].strip().endswith('}'):
                    #说明实际结果是json
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果是json，开始loads。")
                    actualResultDict = json.loads(actualList[0].strip())
                    # 说明实际结果真的是json，loads成功。结构正确。
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果loads成功。")
                else:
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果不是json。")
                    if expect in actualList[0]:
                        return [u"PASS: 预期返回结果断言成功！", "PASS", perform_time]
                    else:
                        return [u"FAIL: 断言失败！", "FAIL", perform_time]
            except Exception, e:
                logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果json loads失败。")
                if expect in actualList[0]:
                    return [u"PASS: 预期返回结果断言成功！", "PASS", perform_time]
                else:
                    return [u"FAIL: 断言失败！", "FAIL", perform_time]
        except Exception, e:
            logging.debug(u"CommonProcess.py: assert_result_recur: 异常:%s" % e)
            if expect in return_msg:
                return [u"PASS: 预期返回结果断言成功！".encode('utf8'), 'PASS',perform_time]
            else:
                return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, return_msg), 'FAIL',perform_time]
        logging.debug( u"CommonProcess.py: assert_result: 实际结果：%s" % actualResultDict)
        logging.info( u"CommonProcess.py: assert_result: 接口使用时间:%s" % perform_time)
        #变量当前数组中的所有键值 判断是否相等
        #预期结果、实际结果都是json。下面开始key value的断言。
        def assert_string(expectValue,actualValue,current_key):
            # value不是字典，也不是list，不进行递归，只进行 相等判断 或者 数组长度判断。
            try:
                if str(actualValue) == str(expectValue):
                    # 如果值相等，那么退出循环，本次验证结束。
                    fail[0] = fail[0] + u"PASS: 断言成功！Key(%s)的值断言通过，预期%s，实际%s。\r\n".encode('utf8') % (current_key, (expectValue == None and "null" or str(expectValue)), (actualValue == None and "null" or str(actualValue)))
                    logging.info(u"CommonProcess.py: assert_result: 断言成功！Key(%s)的值断言通过，预期%s，实际%s。\r\n".encode('utf8') % (current_key,(expectValue == None and "null" or str(expectValue)), (actualValue == None and "null" or str(actualValue))))
                else:
                    # 如果值不相等，判断expect的value是否是关键字LEN
                    expect_length = self.get_sub_string(str(expectValue), "LEN(", ")")
                    if expect_length != False and expect_length.strip() != "":
                        # 预期结果是断言长度
                        try:
                            int_expectlen = int(expect_length.strip())
                            # 预期长度获取成功，且转换成int成功。
                            actValue = actualValue
                            if type(actValue) != type([]):
                                logging.info(u"CommonProcess.py: assert_result: 实际值不是数组，无法断言。")
                                fail[0] = fail[0] + u"FAIL: 断言失败！实际值不是数组，无法断言。\r\n".encode('utf8')
                                failPointCount[0] += 1
                            # 开始判断长度。
                            int_actlen = len(actValue)
                            if int_actlen == int_expectlen:
                                fail[0] = fail[0] + u"PASS: 断言成功！Key(%s)的长度断言正确，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen)
                                logging.info(u"CommonProcess.py: assert_result: 断言成功！Key(%s)的长度断言正确，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen))
                            else:
                                logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的长度断言失败，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen))
                                fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的长度断言失败，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen)
                                failPointCount[0] += 1
                        except Exception, e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key,(expectValue == None and "null" or str(expectValue)), (actualValue == None and "null" or str(actualValue))))
                            fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, (expectValue == None and "null" or str(expectValue)), (actualValue == None and "null" or str(actualValue)))
                            failPointCount[0] += 1
                    else:
                        # 预期结果不是断言长度，那么断言失败了。如果不是进行len判断，那么就是测试失败
                        logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, (expectValue == None and "null" or str(expectValue)), (actualValue == None and "null" or str(actualValue))))
                        fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, (expectValue == None and "null" or str(expectValue)), (actualValue == None and "null" or str(actualValue)))
                        failPointCount[0] += 1
            except Exception, e:
                logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果不存在这个key(%s)或者其他异常。")
                fail[0] = fail[0] + u"FAIL: 断言失败！实际结果不存在这个key(%s)或者其他异常。异常：%s".encode('utf8') % (current_key,e)
                failPointCount[0] += 1

        global_key=['']
        def recur_dict(value_recur, actual_value):
            tmptag = 0
            for t_key, t_value in value_recur.items():
                if tmptag > 0:
                    # [data  [id
                    list_gkey = global_key[0].split("]")
                    global_key[0] = ''
                    for i in range(0,len(list_gkey)-2):
                        global_key[0] = global_key[0] + list_gkey[i] + "]"

                global_key[0] = global_key[0] + "[%s]" % t_key
                tmptag += 1
                try:
                    if type(t_value) == type({}):
                        try:
                            recur_dict(t_value, actual_value[t_key])
                        except Exception,e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                        continue
                    elif type(t_value) == type([]):
                        # 判断list，是list进行list相关断言。
                        tmplistindex=0
                        for ilistInRecur in range(0, len(t_value)):
                            if type(t_value[ilistInRecur]) == type({}):
                                if tmplistindex>0:
                                    # [data [0 [id 去掉重复的数组路径
                                    list_gkey = global_key[0].split("[%d]" % (tmplistindex-1))
                                    global_key[0] = list_gkey[0]

                                global_key[0] = global_key[0] + "[%d]" % ilistInRecur
                                tmplistindex+=1
                                recur_dict(t_value[ilistInRecur], actual_value[t_key][ilistInRecur])
                            else:
                                try:
                                    assert_string(t_value[ilistInRecur],actual_value[t_key][ilistInRecur],global_key[0])
                                except Exception,e:
                                    logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                                    fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                                    failPointCount[0] += 1
                        continue
                    else:
                        #不是dict 不是list ，进行string断言
                        try:
                            assert_string(value_recur[t_key],actual_value[t_key],global_key[0])
                        except Exception, e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                except Exception, e:
                    failPointCount[0] += 1
                    fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果没有这个key。异常：%s\r\n".encode('utf8') % (global_key[0], value_recur[t_key], e)

        for key, value in expectResultDict.items():
            global_key[0] = "[%s]" % key
            if type(value) == type({}):
                #value是字典，进行递归断言。
                try:
                    recur_dict(value,actualResultDict[key])
                except Exception, e:
                    failPointCount[0] += 1
                    fail[0] = fail[0] + u"FAIL: 断言失败！%s的值不对，预期结果%s，实际结果没有这个key。异常：%s\r\n".encode('utf8') % (key, value, e)
            elif type(value) == type([]):
                #判断list，是list进行list相关断言。
                #return [u"FAIL:进行LIST预期结果断言。", "FAIL", perform_time]
                tmplistindex = 0
                for ilistAssert in range(0,len(value)):
                    if type(value[ilistAssert]) == type({}):
                        if tmplistindex > 0:
                            # [data [0 [id 去掉重复的数组路径
                            list_gkey = global_key[0].split("[%d]" % (tmplistindex - 1))
                            global_key[0] = list_gkey[0]

                        global_key[0] = global_key[0] + "[%d]" % ilistAssert
                        tmplistindex+=1
                        try:
                            recur_dict(value[ilistAssert],actualResultDict[key][ilistAssert])
                        except Exception,e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                    else:
                        try:
                            assert_string(value[ilistAssert],actualResultDict[key][ilistAssert],global_key[0])
                        except Exception,e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
            else:
                # value不是字典，也不是list，不进行递归，只进行 相等判断 或者 数组长度判断。
                try:
                    assert_string(expectResultDict[key],actualResultDict[key],global_key[0])
                except Exception, e:
                    logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                    fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                    failPointCount[0] += 1

        if failPointCount[0] == 0:
            logging.info( u"CommonProcess.py: assert_result_recur: PASS: 预期返回结果断言成功！")
            return [u"PASS: 返回内容全部断言通过。\r\n%s".encode('utf8') % fail[0],"PASS",perform_time]
        else:
            logging.info(u"CommonProcess.py: assert_result_recur: FAIL: 测试失败，断言失败点有%d个，请查看详情。" % failPointCount[0])
            return [u"FAIL: 返回内容最终断言失败。\r\n%s".encode('utf8') % fail[0],'FAIL',perform_time]

    def assert_result_http(self, expect, return_msg):
        """
        断言预期结果和实际结果
        接受参数为expect, return_msg 两个字符串
        返回值为 code 断言结果 时间
        """
        # 首先要判断预期结果是否是JSON，还是字符串，如果是字符串，就测试返回结果是否保存字符串内容，异常返回是带字符串的
        expect = expect.strip()
        return_msg = return_msg.strip()
        # 遍历字典，比对结果
        failPointCount = [0]
        #定义一个变量，用来存储多个断言值不对的情况
        fail = ['']
        try:
            logging.debug(u"CommonProcess.py: assert_result: 预期结果：%s" % expect)
            logging.debug(u"CommonProcess.py: assert_result: 实际结果：%s" % return_msg)
            error_return_msg = return_msg.split(":")
            if  "ERROR" in error_return_msg[0] :
                return [return_msg,"ERROR"]
            logging.debug(u"CommonProcess.py: assert_result: 不是ERROR")
            if expect != "null":
                isExpectInt = False
                isExpectFloat = False
                try:
                    intExpect = int(expect)
                    isExpectInt = True
                except Exception,e:
                    logging.info(u"预期结果是int。")
                try:
                    intExpect = float(expect)
                    isExpectFloat = True
                except Exception,e:
                    logging.info(u"预期结果是float。")

                if isExpectInt or isExpectFloat: raise ValueError(u"预期结果是int或者float。")

                expectResultDict = json.loads(expect)
                #expect不是null，且是json字符串，要进行json递归断言。
            else:
                #expect是null，返回断言结果。
                if expect in return_msg:
                    return [u"PASS: 预期返回结果断言成功！".encode('utf8'), 'PASS']
                else:
                    return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, return_msg), 'FAIL']

            logging.debug(u"CommonProcess.py: assert_result: 已json loads 预期结果")
            #对实际结果的第一节转json格式，如果转换失败，就抛错
            try:
                if return_msg.startswith('{') and return_msg.endswith('}'):
                    #说明实际结果是json
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果是json，开始loads。")
                    actualResultDict = json.loads(return_msg)
                    # 说明实际结果真的是json，loads成功。结构正确。
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果loads成功。")
                else:
                    logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果不是json。")
                    if expect in return_msg:
                        return [u"PASS: 预期返回结果断言成功！", "PASS"]
                    else:
                        return [u"FAIL: 断言失败！", "FAIL"]
            except Exception, e:
                logging.debug(u"CommonProcess.py: assert_result_recur: 实际结果json loads失败。")
                if expect in return_msg:
                    return [u"PASS: 预期返回结果断言成功！", "PASS"]
                else:
                    return [u"FAIL: 断言失败！", "FAIL"]
        except Exception, e:
            logging.debug(u"CommonProcess.py: assert_result_recur: 异常:%s" % e)
            if expect in return_msg:
                return [u"PASS: 预期返回结果断言成功！".encode('utf8'), 'PASS']
            else:
                return [u"FAIL: 断言失败！参数值不对，预期结果%s，实际结果%s。".encode('utf8') % (expect, return_msg), 'FAIL']
        logging.debug( u"CommonProcess.py: assert_result: 实际结果：%s" % actualResultDict)
        #变量当前数组中的所有键值 判断是否相等
        #预期结果、实际结果都是json。下面开始key value的断言。
        def assert_string(expectValue,actualValue,current_key):
            # value不是字典，也不是list，不进行递归，只进行 相等判断 或者 数组长度判断。
            try:
                if str(actualValue) == str(expectValue):
                    # 如果值相等，那么退出循环，本次验证结束。
                    fail[0] = fail[0] + u"PASS: 断言成功！Key(%s)的值断言通过，预期%s，实际%s。\r\n".encode('utf8') % (current_key, str(expectValue), str(actualValue))
                    logging.info(u"CommonProcess.py: assert_result: 断言成功！Key(%s)的值断言通过，预期%s，实际%s。\r\n".encode('utf8') % (current_key, str(expectValue), str(actualValue)))
                else:
                    # 如果值不相等，判断expect的value是否是关键字LEN
                    expect_length = self.get_sub_string(str(expectValue), "LEN(", ")")
                    if expect_length != False and expect_length.strip() != "":
                        # 预期结果是断言长度
                        try:
                            int_expectlen = int(expect_length.strip())
                            # 预期长度获取成功，且转换成int成功。
                            actValue = actualValue
                            if type(actValue) != type([]):
                                logging.info(u"CommonProcess.py: assert_result: 实际值不是数组，无法断言。")
                                fail[0] = fail[0] + u"FAIL: 断言失败！实际值不是数组，无法断言。\r\n".encode('utf8')
                                failPointCount[0] += 1
                            # 开始判断长度。
                            int_actlen = len(actValue)
                            if int_actlen == int_expectlen:
                                fail[0] = fail[0] + u"PASS: 断言成功！Key(%s)的长度断言正确，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen)
                                logging.info(u"CommonProcess.py: assert_result: 断言成功！Key(%s)的长度断言正确，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen))
                            else:
                                logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的长度断言失败，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen))
                                fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的长度断言失败，预期长度%d，实际长度%d。\r\n".encode('utf8') % (current_key, int_expectlen, int_actlen)
                                failPointCount[0] += 1
                        except Exception, e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue))
                            fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue)
                            failPointCount[0] += 1
                    else:
                        # 预期结果不是断言长度，那么断言失败了。如果不是进行len判断，那么就是测试失败
                        logging.info(u"CommonProcess.py: assert_result: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue))
                        fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果%s。\r\n".encode('utf8') % (current_key, str(expectValue), actualValue)
                        failPointCount[0] += 1
            except Exception, e:
                logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果不存在这个key(%s)或者其他异常。")
                fail[0] = fail[0] + u"FAIL: 断言失败！实际结果不存在这个key(%s)或者其他异常。异常：%s".encode('utf8') % (current_key,e)
                failPointCount[0] += 1

        global_key=['']
        def recur_dict(value_recur, actual_value):
            tmptag = 0
            for t_key, t_value in value_recur.items():
                if tmptag > 0:
                    # [data  [id
                    list_gkey = global_key[0].split("]")
                    global_key[0] = ''
                    for i in range(0,len(list_gkey)-2):
                        global_key[0] = global_key[0] + list_gkey[i] + "]"

                global_key[0] = global_key[0] + "[%s]" % t_key
                tmptag += 1
                try:
                    if type(t_value) == type({}):
                        try:
                            recur_dict(t_value, actual_value[t_key])
                        except Exception,e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                        continue
                    elif type(t_value) == type([]):
                        # 判断list，是list进行list相关断言。
                        tmplistindex=0
                        for ilistInRecur in range(0, len(t_value)):
                            if type(t_value[ilistInRecur]) == type({}):
                                if tmplistindex>0:
                                    # [data [0 [id 去掉重复的数组路径
                                    list_gkey = global_key[0].split("[%d]" % (tmplistindex-1))
                                    global_key[0] = list_gkey[0]

                                global_key[0] = global_key[0] + "[%d]" % ilistInRecur
                                tmplistindex+=1
                                recur_dict(t_value[ilistInRecur], actual_value[t_key][ilistInRecur])
                            else:
                                try:
                                    assert_string(t_value[ilistInRecur],actual_value[t_key][ilistInRecur],global_key[0])
                                except Exception,e:
                                    logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                                    fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                                    failPointCount[0] += 1
                        continue
                    else:
                        #不是dict 不是list ，进行string断言
                        try:
                            assert_string(value_recur[t_key],actual_value[t_key],global_key[0])
                        except Exception, e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                except Exception, e:
                    failPointCount[0] += 1
                    fail[0] = fail[0] + u"FAIL: 断言失败！Key(%s)的值不对，预期结果%s，实际结果没有这个key。异常：%s\r\n".encode('utf8') % (global_key[0], value_recur[t_key], e)

        for key, value in expectResultDict.items():
            global_key[0] = "[%s]" % key
            if type(value) == type({}):
                #value是字典，进行递归断言。
                try:
                    recur_dict(value,actualResultDict[key])
                except Exception, e:
                    failPointCount[0] += 1
                    fail[0] = fail[0] + u"FAIL: 断言失败！%s的值不对，预期结果%s，实际结果没有这个key。异常：%s\r\n".encode('utf8') % (key, value, e)
            elif type(value) == type([]):
                #判断list，是list进行list相关断言。
                #return [u"FAIL:进行LIST预期结果断言。", "FAIL", perform_time]
                tmplistindex = 0
                for ilistAssert in range(0,len(value)):
                    if type(value[ilistAssert]) == type({}):
                        if tmplistindex > 0:
                            # [data [0 [id 去掉重复的数组路径
                            list_gkey = global_key[0].split("[%d]" % (tmplistindex - 1))
                            global_key[0] = list_gkey[0]

                        global_key[0] = global_key[0] + "[%d]" % ilistAssert
                        tmplistindex+=1
                        try:
                            recur_dict(value[ilistAssert],actualResultDict[key][ilistAssert])
                        except Exception,e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
                    else:
                        try:
                            assert_string(value[ilistAssert],actualResultDict[key][ilistAssert],global_key[0])
                        except Exception,e:
                            logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                            fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                            failPointCount[0] += 1
            else:
                # value不是字典，也不是list，不进行递归，只进行 相等判断 或者 数组长度判断。
                try:
                    assert_string(expectResultDict[key],actualResultDict[key],global_key[0])
                except Exception, e:
                    logging.info(u"CommonProcess.py: assert_result: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0])
                    fail[0] = fail[0] + u"FAIL: 断言失败！实际结果未发现相应的key(%s)。" % global_key[0]
                    failPointCount[0] += 1

        if failPointCount[0] == 0:
            logging.info( u"CommonProcess.py: assert_result_recur: PASS: 预期返回结果断言成功！")
            return [u"PASS: 返回内容全部断言通过。\r\n %s".encode('utf8') % fail[0],"PASS"]
        else:
            logging.info(u"CommonProcess.py: assert_result_recur: FAIL: 测试失败，断言失败点有%d个，请查看详情。" % failPointCount[0])
            return [u"FAIL: 返回内容最终断言失败。\r\n %s".encode('utf8') % fail[0],'FAIL']

    def get_processed_vars(self,varsconf,env,db):
        # =================特殊格式化处理变量配置。============================
        # 先参数自替换
        for j in range(0, 20):
            if "$var[" not in varsconf:
                break
            varsconf = self.process_vars(varsconf, varsconf, env)
        #logging.debug(u"处理后的变量配置：%s" % varsconf)
        # 然后参数处理。
        varsconf = self.replace_NOW_TIMESTAMP(varsconf)
        varsconf = self.replace_NOW_D(varsconf)
        varsconf = self.replace_NOW_FORMAT_D(varsconf)
        for k in range(0,20):
            if "EVAL{(" not in varsconf and "SQL_SELECT{(" not in varsconf :
                break
            # 先处理一次EVAL为sql查询服务EVAL{( 表达式 )}
            varsconf = self.replace_EVAL(varsconf)
            # 处理SQL查询 SQL_SELECT{( SQL语句 )} 有且仅有一行数据为合法，否则不予执行
            varsconf = self.replace_SQL_SELECT(varsconf, db)
        return varsconf

    def get_varspool(self,varsPool,varsconf,env,db):
        varsconf = self.get_processed_vars(varsconf, env, db)
        logging.debug(u"HttpService.py: execute_group_testcases: 处理完成的变量配置：%s" % varsconf)
        varsstring = self.get_vars_by_varsconf(varsconf, env)
        var_dict = self.get_var_dict_by_varstring(varsstring)
        varsPool = self.set_varspool(varsPool, var_dict)
        return varsPool