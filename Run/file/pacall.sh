killall run
#./pacrun.sh
rm -rf build/ dist/ run.spec run;
pyinstaller -F -p /usr/local/python/lib/python2.7,/home/interface/DubboInterface/DubboInterfaceTestFramework /home/interface/DubboInterface/DubboInterfaceTestFramework/Run/run.py ;
rm -rf run;
cp dist/run .;
rm -rf build/ dist/ run.spec;

killall runtask
#./pactask.sh
rm -rf build/ dist/ runtask.spec runtask;
pyinstaller -F -p /usr/local/python/lib/python2.7,/home/interface/DubboInterface/DubboInterfaceTestFramework /home/interface/DubboInterface/DubboInterfaceTestFramework/Run/runtask.py ;
rm -rf runtask;
cp dist/runtask .;
rm -rf build/ dist/ runtask.spec;

#./cptobin.sh
killall runtask
cp listen.sh /home/InterfaceFrameworkOnline/bin/
cp run /home/InterfaceFrameworkOnline/bin/
cp runtask /home/InterfaceFrameworkOnline/bin/
chmod +x /home/InterfaceFrameworkOnline/bin/listen.sh