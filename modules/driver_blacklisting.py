import fileinput

def amd(blacklist=None):
    result = None
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if blacklist == True:
            if "amdgpu" in line:
                line = "#amdgpu" + "\n"
                result = False
        else:
            if "amdgpu" in line:
                line = "blacklist amdgpu" + "\n"
                result = True
        print(line,end="")
    return result


def nvidia(blacklist=None):
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if blacklist == True:
            if "blacklist nvidia-current" in line:
                line = "#nvidia-current" + "\n"
                result = False
        else:
            if "nvidia-current" in line:
                line = "blacklist nvidia-current" + "\n"
                result = True
        print(line,end="")
    return result

def nouveau(blacklist=None):
    nextline = False
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if nextline == True:
            line = ""
            nextline = False
        elif blacklist == True:
            if "blacklist nouveau" in line:
                line = "#nouveau" + '\n'
                nextline = True
                result = False
        else:
            if "#nouveau" in line:
                line = "blacklist nouveau" + '\n' + "options nouveau modeset=0" + "\n"
                result = True
        print(line,end="")
    return result
