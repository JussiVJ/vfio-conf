import fileinput

def config():
    for line in fileinput.FileInput("testfiles/testfilemodload", inplace=1):
        if "vfio-pci" in line:
            line = "#vfio"
        print(line,end="")

    for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
        if "vfio-pci options" in line or "#vfio_int" in line:
            line = "#vfio-pci" + '\n'
        print(line,end="")

    linelist = []
    for line in fileinput.FileInput("testfiles/testfilegrub",inplace=1):
        if "GRUB_CMDLINE_LINUX_DEFAULT" in line and "vfio-pci" in line:
                for item in ''.join(line.split('"')).split(' '):
                    if 'vfio-pci' not in item and 'GRUB_CMDLINE_LINUX_DEFAULT' not in item:
                        linelist.append(item)
                linelist[len(linelist)-1] = linelist[len(linelist)-1].replace('\n', '"' + '\n')
                line = 'GRUB_CMDLINE_LINUX_DEFAULT="' + ' '.join(linelist)
                result = False
        print(line,end="")
