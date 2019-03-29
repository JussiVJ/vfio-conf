import fileinput

def load():
    results = {}
    results["nvidia"] = True
    results["amd"] = True
    results["nouveau"] = True

    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if "#nvidia-current" in line:
            results["nvidia"] = False
        elif "#amdgpu" in line:
            results["amd"] = False
        elif "#nouveau" in line:
            results["nouveau"] = False
        print(line,end="")

    return results
