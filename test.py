import fileinput
for line in fileinput.FileInput("testfile",inplace=1):
    if "vfio_pci" in line:
        linelist = line.split(" ")
        line2 = []
        for item in linelist:
            if "vfio_pci" in item:
                del item
            else:
                line2.extend(" "+item)
        line = ''.join(line2)
        line = line.replace(" GRUB", "GRUB")
    print(line,end="")
