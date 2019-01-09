import fileinput
for line in fileinput.FileInput("testfile",inplace=1):
    if "vfio_pci" in line:
        linelist = line.split('"')
        line2 = []
        linelist2 = []
        for item in linelist:
            if "vfio_pci" in item:
                linelist2 = item.split(' ')
                for item in linelist2:
                    if "vfio_pci" in item:
                        del item
                    else:
                        line2.extend(" "+item)
            else:
                line2.extend(" "+item)
        line2.extend('"')
        line2.extend('\n')
        line = ''.join(line2)
        line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT= ', 'GRUB_CMDLINE_LINUX_DEFAULT="')
        line = line.replace(" GRUB", "GRUB")
    print(line,end="")
