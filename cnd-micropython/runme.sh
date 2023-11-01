cd /mnt/c/Users/cnd/Downloads/cnd-micropython; 
ampy --port /dev/ttyS21 mkdir bin
ampy --port /dev/ttyS21 mkdir lib
ampy --port /dev/ttyS21 mkdir lib/aioble
ampy --port /dev/ttyS21 mkdir lib/aioble/aioble
for FN in `cat sendme`;do echo $FN;ampy --port /dev/ttyS21 put $FN $FN;done
