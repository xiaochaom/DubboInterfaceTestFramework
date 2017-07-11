# coding:utf-8
"""
Author:王吉亮
Date:20161027
Comment:已废弃，目前采用web平台任务，主要运行runCaseDebugTask和runPlatformTask。
"""

import sys

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append("..")


from Lib.UsualTools import UsualTools
import os,subprocess
from Lib.DBTool import DBTool
import logging
import time
from Config.Config import Config

if __name__ == "__main__":
    if UsualTools.isLinuxSystem():
        logging.basicConfig(level='INFO',
                            format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                            datefmt='%a, %d %b %Y %H:%M:%S',
                            filename='/home/InterfaceFrameworkOnline/logs/runtask.log',
                            filemode='w')
        # 循环遍历t_task表，顺序执行任务，执行时把state变成2，执行后变成3.
        conf = Config("../ConfFile/platform.conf").conf_dict
        while True:
            db = DBTool(conf['db']['host'], int(conf['db']['port']), conf['db']['username'], conf['db']['password'],
                        conf['db']['dbname'])
            results = db.execute_sql("select * from tb_taskpython where state=1 or state=2 order by create_time asc")
            for res in results:
                logging.info(u"执行命令：%s" % res[1])
                sqlupdate = "update tb_taskpython set state=2 where id=%d" % res[0]
                db.execute_sql(sqlupdate)
                message = subprocess.Popen(res[1], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out, err = message.communicate()
                outresult = ""
                for line in out.splitlines():
                    outresult = outresult + line + "\n"
                logging.debug(u"%s" % outresult)
                if "TEST_FINISHED" in outresult:
                    sqlupdate = """update tb_taskpython set state=3,command_result="%s" where id=%d""" % (outresult, res[0])
                else:
                    sqlupdate = """update tb_taskpython set state=4,command_result="%s" where id=%d""" % (outresult, res[0])
                logging.info(sqlupdate)
                db.execute_sql(sqlupdate)
            db.release()
            time.sleep(0.5)