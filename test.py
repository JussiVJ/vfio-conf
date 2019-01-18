import fileinput
pci_ids = "8942:4j3i,2344:0vd9"
linelist = []
linelist2 = []
line2 = []
counter = 0
for line in fileinput.FileInput("testfilegrub",inplace=1):
    if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
        if "vfio_pci" in line:
            linelist = line.split(' ')
            linelist2 = linelist[0].split('"')
            linel = linelist2[0]
            linelist.insert(0, linel)
            linelist[1] = linelist2[1]
            for item in linelist:
                if "vfio_pci" not in item:
                    if counter == 0 or counter == len(linelist)-2:
                        line2.append(item)
                    else:
                        line2.append(item + " ")
                    counter = counter + 1
                else:
                    line2.append("vfio_pci" + pci_ids + " ")
            line2[0] = line2[0] + '"'
            linefin = ''.join(line2)
            line = linefin
    print(line,end="")
