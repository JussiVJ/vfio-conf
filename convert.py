import fileinput
for line in fileinput.FileInput("gui.py",inplace=1):
    if 'testfilemodprobe' in line:
        line = line.replace("testfilemodprobe", "/etc/modprobe.d/vfioconf.conf")
    if 'testfilegrub' in line:
        line = line.replace("testfilegrub", "/etc/default/grub")
    if 'testfilemkinitcpio' in line:
        line = line.replace("testfilemkinitcpio", initcpio)
    if 'testfileos' in line:
        line = line.replace("testfileos", "/etc/os-release")
    print(line,end="")
