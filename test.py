import fileinput
sacc = False
for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
    if 'GRUB_CMDLINE_LINUX_DEFAULT' in line and "iommu" in line:
        sacc = True

    print(line,end="")

print(sacc)
