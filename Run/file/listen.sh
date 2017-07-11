#!/bin/sh
cdnclient_pid=`ps -aux|grep -v 'grep'|grep -c '/home/InterfaceFrameworkOnline/bin/runtask'`
echo $cdnclient_pid

if [ $cdnclient_pid -ne 2 ] ; then
echo "runtask status error."
echo "Kill other alived runtask service and then startup"
killall -9 runtask
echo "runtask service killed"
echo "Starting runtask service ..."
/home/InterfaceFrameworkOnline/bin/runtask 2>&1 &
echo "runtask service started!"
else
echo "runtask service was exited!"
fi
