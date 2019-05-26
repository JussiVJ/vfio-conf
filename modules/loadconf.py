import fileinput

def load():
    results = {}
    results["nvidia"] = True
    results["amd"] = True
    results["nouveau"] = True
    results["vfio-int"] = False
    results["ids"] = []

    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if "#nvidia-current" in line:
            results["nvidia"] = False
        elif "#amdgpu" in line:
            results["amd"] = False
        elif "#nouveau" in line:
            results["nouveau"] = False
        elif "#vfio_int" in line:
            results["vfio-int"] = True
        elif "vfio-pci options" in line:
            for item in line.split("=")[1].split(","):
                results["ids"].append(item)
                results["ids"][len(results["ids"])-1] = results["ids"][len(results["ids"])-1].strip('\n')
        print(line,end="")


    if results["vfio-int"] == True:
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
            if 'vfio-pci.ids=' in line:
                for item in line.split('LINUX_DEFAULT="')[1].split(" "):
                    if "vfio-pci.ids" in item:
                        results["ids"] = item.lstrip("vfio-pci.ids=").split(",")
                        results["ids"][len(results["ids"])-1] = results["ids"][len(results["ids"])-1].strip('\n')
            print(line,end="")

    return results
