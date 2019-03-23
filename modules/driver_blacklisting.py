import fileinput

def amd(self, blacklist=None):
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if blacklist == True:
            blacklist = False
            print
        print(line,end="")


def nvidia():
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if NVIDIAblacklist == True:
            if "blacklist nvidia-current" in line:
                line = "#nvidia-current" + "\n"
                NVIDIAblacklist = False
                self.ButtonBlacklistNvidia.set_label("Blacklist NVIDIA")
                self.LabelBlacklistNvidia.set_text("Blacklist propietary NVIDIA drivers")
        else:
            if "nvidia-current" in line:
                line = "blacklist nvidia-current" + "\n"
                NVIDIAblacklist = True
                self.ButtonBlacklistNvidia.set_label("Unblacklist NVIDIA")
                self.LabelBlacklistNvidia.set_text("Unblacklist propietary NVIDIA drivers")
        print(line,end="")

def nouveau():
    nextline = False
    for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
        if NOUVEAUblacklist == True:
            if "nouveau" in line:
                line = "#nouveau" + '\n'
                NOUVEAUblacklist = False
                self.ButtonBlacklistNouveau.set_label("Blacklist Nouveau")
                self.LabelBlacklistNouveau.set_text("Blacklist opensource NVIDIA drivers")
                nextline = True
        else:
            if nextline == True:
                line = ""
                nextline = False
            elif "#nouveau" in line:
                line = "blacklist nouveau" + '\n' + "options nouveau modeset=0" + "\n"
                NOUVEAUblacklist = True
                self.ButtonBlacklistNouveau.set_label("Unblacklist Nouveau")
                self.LabelBlacklistNouveau.set_text("Unblacklist opensource NVIDIA drivers")
        print(line,end="")
