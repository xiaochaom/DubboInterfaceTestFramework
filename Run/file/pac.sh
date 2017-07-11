rm -rf build/ dist/ run.spec ;
pyinstaller -F -p /usr/local/python/lib/python2.7,/home/interface/DubboInterface/DubboInterfaceTestFramework /home/interface/DubboInterface/DubboInterfaceTestFramework/Run/run.py ;
