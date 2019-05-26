import fileinput
def arch(self, int=False, ids={}):
    pci_dev = []
    for item in ids:
        if ids[item] == True:
            pci_dev.append(item)
    print(pci_dev)
    if int == False:
        for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
            if "vfio-pci" in line and len(pci_dev) > 0:
                line = "vfio-pci options ids=" + ','.join(pci_dev) + '\n'
            elif len(pci_dev) == 0 and "vfio-pci" in line:
                line = "#vfio-pci" + '\n'
            print(line,end="")
    else:
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT" in line:
                if "vfio" not in line:
                    line = line.replace('LINUX_DEFAULT="', 'LINUX_DEFAULT="vfio-pci.ids=' + ','.join(pci_dev))
            print(line,end="")
