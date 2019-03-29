import fileinput
def rm(vf_int):
    linelist = []
    if vf_int == False:
        for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
            if "vfio-pci" in line:
                line = "#vfio-pci"
            print(line,end="")
    else:
        for line in fileinput.FileInput("testfiles/testfilegrub",inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                for item in line.split('"'):
                    if "vfio" not in item:
                        linelist.append(item)
                    else:
                        for x in item.split(" "):
                            if "vfio" not in x:
                                linelist.append(x)

                options = [linelist[0] + '"']

                for i in range(1,len(linelist)-2):
                    options.append(linelist[i] + " ")
                options.append(linelist[len(linelist)-2] + '"')
                options.append(linelist[len(linelist)-1])
                line = ''.join(options)
            print(line,end="")
