import fileinput
import os
for line in fileinput.FileInput("gui.py",inplace=1):
    if 'testfilemodprobe' in line:
        line = line.replace("testfilemodprobe", "/etc/modprobe.d/vfioconf.conf")
    if 'testfilegrub' in line:
        line = line.replace("testfilegrub", "/etc/default/grub")
    if 'testfilemkinitcpio' in line:
        line = line.replace("testfilemkinitcpio", "/etc/mkinitcpio.conf")
    if 'testfileos' in line:
        line = line.replace("testfileos", "/etc/os-release")
    if 'testfilemodload' in line:
        line = line.replace("testfilemodload", "/etc/modules/vfioconf.conf")
    print(line,end="")

os.remove("testfilemodprobe")
os.remove("testfilegrub")
os.remove("testfilemkinitcpio")
os.remove("testfileos")
os.remove("testfilemodload")
os.remove("test.py")
os.remove("convert.py")
