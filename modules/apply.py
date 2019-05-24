import fileinput
def arch(self, int=False, ids={}):
    pci_dev = []
    for item in ids:
        if ids[item] == True:
            pci_dev.append(item)
    if int == False:
        for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
            if "vfio-pci" in line and len(pci_dev) > 0:
                line = "vfio-pci options=" + ','.join(pci_dev) + '\n'
            elif len(pci_dev) == 0 and "vfio-pci" in line:
                line = "#vfio-pci" + '\n'
            print(line,end="")
    else:
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT" in line:
                linelist = line.split('"').split(" ")
                for item in linelist:
                    if "vfio" in item:
                        if len(pci_dev) == 0:
                            del item
                        else:
                            item = "vfio-pci.ids=" + ''.join(pci_dev)
                if len(pci_dev) > 0 and "vfio" not in ''.join(linelist):
                    linelist[0] = linelist[0] + '"vfio-pci.ids=' + ''.join(pci_dev)
                else:
                    linelist[0] = linelist[0] + '"'
                linelist[len(linelist)-1] = linelist[len(linelist)-1] + '"'
            print(line,end="")
