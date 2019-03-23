import fileinput

def amd(self, blacklist=False):
    for line in fileinput.FileInput("testfilemodprobe",inplace=1):
        if blacklist == True:
            if "amdgpu" in line:
                line = "#amdgpu" + "\n"
                return False
        else:
            if "amdgpu" in line:
                line = "blacklist amdgpu" + "\n"
                return True
        print(line,end="")


def nvidia(self, blacklist=False):
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if blacklist == True:
            if "blacklist nvidia-current" in line:
                line = "#nvidia-current" + "\n"
                return False
        else:
            if "nvidia-current" in line:
                line = "blacklist nvidia-current" + "\n"
                return True
        print(line,end="")

def nouveau(self, blacklist=False):
    nextline = False
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if blacklist == True:
            if "nouveau" in line:
                line = "#nouveau" + '\n'
                return False
                nextline = True
        else:
            if nextline == True:
                line = ""
                nextline = False
            elif "#nouveau" in line:
                line = "blacklist nouveau" + '\n' + "options nouveau modeset=0" + "\n"
                return True
        print(line,end="")
