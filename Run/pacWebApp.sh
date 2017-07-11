baseroot="/home/interface/DubboInterface/DubboInterfaceTestFramework"
binroot="/home/InterfaceFrameworkOnline"
pythonlibroot="/usr/local/python/lib/python2.7"

#pac runCaseDebugTask.py
binName="runCaseDebugTask"
killall -9 ${binName}
rm -rf build/ dist/ ${binName}.spec ${binName};
pyinstaller -F -p ${pythonlibroot},${baseroot} ${baseroot}/Run/${binName}.py ;
rm -rf ${binName};
cp dist/${binName} .;
rm -rf build/ dist/ ${binName}.spec;

#pac runPlatformTask.py
binName="runPlatformTask"
killall -9 ${binName}
rm -rf build/ dist/ ${binName}.spec ${binName};
pyinstaller -F -p ${pythonlibroot},${baseroot} ${baseroot}/Run/${binName}.py ;
rm -rf ${binName};
cp dist/${binName} .;
rm -rf build/ dist/ ${binName}.spec;

#pac runTaskCancel.py
binName="runTaskCancel"
killall -9 ${binName}
rm -rf build/ dist/ ${binName}.spec ${binName};
pyinstaller -F -p ${pythonlibroot},${baseroot} ${baseroot}/Run/${binName}.py ;
rm -rf ${binName};
cp dist/${binName} .;
rm -rf build/ dist/ ${binName}.spec;

#pac listenTaskRunning.py
binName="listenTaskRunning"
killall -9 ${binName}
rm -rf build/ dist/ ${binName}.spec ${binName};
pyinstaller -F -p ${pythonlibroot},${baseroot} ${baseroot}/Run/${binName}.py ;
rm -rf ${binName};
cp dist/${binName} .;
rm -rf build/ dist/ ${binName}.spec;

rm -rf ${binroot}/bin/run*
rm -rf ${binroot}/bin/listenTaskRunning
# copy to execute folder
binName="runCaseDebugTask"
killall -9 ${binName}
rm -rf ${binroot}/bin/${binName}
cp ${binName} ${binroot}/bin/

binName="runPlatformTask"
killall -9 ${binName}
rm -rf ${binroot}/bin/${binName}
cp ${binName} ${binroot}/bin/

binName="runTaskCancel"
killall -9 ${binName}
rm -rf ${binroot}/bin/${binName}
cp ${binName} ${binroot}/bin/

binName="listenTaskRunning"
killall -9 ${binName}
rm -rf ${binroot}/bin/${binName}
cp ${binName} ${binroot}/bin/
