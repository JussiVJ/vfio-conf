import fileinput
import os

for line in fileinput.FileInput("main.py",inplace=1):
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

for item in os.listdir("modules"):
    if '.py' in item:
        for line in fileinput.FileInput(item,inplace=1):
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
