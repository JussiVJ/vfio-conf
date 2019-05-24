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
        elif "#vfio-int" in line:
            results["vfio-int"] = True
        elif "vfio-pci options" in line:
            for item in line.split("=")[1].split(","):
                results["ids"].append(item)
        print(line,end="")

    if results["vfio-int"] == True:
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
            if "vfio-pci.ids=" in list:
                for item in line.split(" "):
                    if "vfio-pci.ids=" in item:
                        results["ids"] = line.split("=")[len(line.split("="))].split(",")
    return results
