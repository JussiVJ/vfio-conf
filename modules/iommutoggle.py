import fileinput
def toggle():
    for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
        if "GRUB_CMDLINE_LINUX_DEFAULT" in line and "iommu" not in line:
            line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="amd_iommu=on intel_iommu=on iommu=pt ')
            result = True
        elif "GRUB_CMDLINE_LINUX_DEFAULT" in line and "iommu" in line:
            linelist = []
            for item in ''.join(line.split('"')).split(' '):
                if 'iommu' not in item and 'GRUB_CMDLINE_LINUX_DEFAULT' not in item:
                    linelist.append(item)
            line = 'GRUB_CMDLINE_LINUX_DEFAULT="' + ' '.join(linelist[len(linelist)-1].replace('\n', '"' + '\n'))
            result = False
        print(line,end="")
    return result
