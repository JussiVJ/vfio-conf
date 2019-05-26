import fileinput
def toggle():
    for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
        if "GRUB_CMDLINE_LINUX_DEFAULT" in line and "iommu" not in line:
            line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="amd_iommu=on intel_iommu=on iommu=pt ')
            line = line.replace(' "\n', '"\n')
            result = True
        elif "GRUB_CMDLINE_LINUX_DEFAULT" in line and "iommu" in line:
            linelist = []
            for item in ''.join(line.split('"')).split(' '):
                if 'iommu' not in item and 'GRUB_CMDLINE_LINUX_DEFAULT' not in item:
                    linelist.append(item)
            if len(linelist) == 0:
                linelist.append('\n')
            linelist[len(linelist)-1] = linelist[len(linelist)-1].replace('\n', '"' + '\n')
            line = 'GRUB_CMDLINE_LINUX_DEFAULT="' + ' '.join(linelist)
            result = False
        print(line,end="")
    return result
