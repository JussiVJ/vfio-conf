import fileinput
for line in fileinput.FileInput("gui.py",inplace=1):
    if 'testfilemodprobe' in line:
        line = line.replace("/etc/modprobe.d/vfioconf.conf", "testfilemodprobe")
    if 'testfilegrub' in line:
        line = line.replace("/etc/default/grub", "testfilegrub")
    if 'testfilemkinitcpio' in line:
        line = line.replace("/etc/mkinitcpio.conf", "testfilemkinitcpio")
    if 'testfileos' in line:
        line = line.replace("/etc/os-release", "testfileos")
    if 'testfilemodload' in line:
        line = line.replace("/etc/modules/vfioconf.conf", "testfilemodload")
    print(line,end="")
