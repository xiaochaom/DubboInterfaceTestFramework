#!/bin/sh
cdnclient_pid=`ps -aux|grep -v 'grep'|grep -c 'runCaseDebugTask'`
echo $cdnclient_pid

if [ $cdnclient_pid -ne 2 ] ; then
echo "runCaseDebugTask status error."
else
echo "runCaseDebugTask service was exited!"
fi

cdnclient_pid=`ps -aux|grep -v 'grep'|grep -c 'runPlatformTask'`
echo $cdnclient_pid

if [ $cdnclient_pid -ne 2 ] ; then
echo "runPlatformTask status error."
else
echo "runPlatformTask service was exited!"
fi

