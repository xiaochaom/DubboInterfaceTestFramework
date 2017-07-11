DROP TABLE IF EXISTS `t_task`;
CREATE TABLE `t_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `command` varchar(1000) NOT NULL,
  `command_result` varchar(10000) DEFAULT NULL,
  `state`  int(1) DEFAULT 1 COMMENT '1、创建。2、进行中。3、正常完成。4执行过程出现异常。',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `mod_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
insert into t_task(command) VALUES ("/home/InterfaceFrameworkOnline/bin/run protocol=HTTP--file=/home/InterfaceFrameworkOnline/Testcases/TestcasesForHttp/Testcases_http.xlsx--case_line_list=--conf=dev--loglevel=DEBUG--logfile=/home/InterfaceFrameworkOnline/logs/loggingloghttp.1OnDev.log--is_send_mail=NO--mail_list=wangjiliang@mftour.cn--report_path=/home/InterfaceFrameworkOnline/reports--report_filename=ReportHttp.html--confpath=/home/InterfaceFrameworkOnline");
insert into t_task(command) VALUES ("/home/InterfaceFrameworkOnline/bin/run protocol=DUBBO--file=/home/InterfaceFrameworkOnline/Testcases/TestcasesForDubbo/Testcases_stock.xlsx--case_line_list=--conf=dev--loglevel=DEBUG--logfile=/home/InterfaceFrameworkOnline/logs/logginglogdubbo.1OnDev.log--is_send_mail=NO--mail_list=wangjiliang@mftour.cn--report_path=/home/InterfaceFrameworkOnline/reports--report_filename=ReportDubbo.html--confpath=/home/InterfaceFrameworkOnline");
