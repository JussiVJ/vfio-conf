import gi
import fileinput
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk

files = str(subprocess.check_output(['ls', '/etc/modprobe.d/']))
files = files.replace("b'", '')
fileslist = files.split('\\n')
del fileslist[len(fileslist) - 1]
if "vfioconf.conf" not in fileslist:
    subprocess.call(["cp", "resources/vfioconf_modprobe.conf", "testfilemodprobe"])
if "vfioconf.conf" not in str(subprocess.check_output(['ls', '/etc/modules'])):
    subprocess.call(["cp", "resources/vfioconf_modules.conf", "/etc/modules/vfioconf.conf"])

pci_ids = {}
vfio_int = False

for line in fileinput.FileInput("testfilemodprobe", inplace=1):
    if "options vfio-pci" in line:
        linelist = line.split("=")
        linelist = linelist[1].split(",")
        for item in linelist:
            item = item.replace('\n', "")
    elif "vfio_int" in line:
        vfio_int = True
    if "blacklist nvidia-current" in line:
        self.NVIDIAmodprobe = True
    if "blacklist nouveau" in line:
        self.NOUVEAUmodprobe = True
    if "blacklist amdgpu" in line:
        self.AMDGPUmodprobe = True
    print(line,end="")


#Get PCI data
if "IOMMU enabled" not in str(subprocess.check_output(['sh', 'resources/IOMMU-check.sh'])):
    IOMMUSTATE = False
    lspci = subprocess.check_output(["lspci", "-nn"])
    ListPci = str(lspci).split("\\n")
    del ListPci[0]
    del ListPci[len(ListPci) - 1]

    #Filter out the Domain and Bus IDs
    ListPciDomain = []
    for item in ListPci:
        item = item.split(" ")
        ListPciDomain.append(item[0])

    #Filter out the names of the PCI-devices
    ListPciName = []
    for item in ListPci:
        itemlist = item.split(" ")
        del(itemlist[0])
        item = ' '.join(itemlist)
        item = item.replace(":", " [")
        itemlist = item.split(" [")
        ListPciName.append(str(itemlist[0] + ":" + itemlist[2]))

    #Filter out the IDs of the PCI-derrortoggle == 0evices
    ListPciIDs = []
    for item in ListPci:
        item = item.replace('[', ']')
        item = item.split("]")
        while ":" not in item[0] or len(item[0]) != 9:
            del item[0]
        while len(item) > 1:
            del item[1]
        ListPciIDs.extend(item)
        pci_ids[item[0]] = False

    #Filter out the revisons of the PCI-devices
    ListPciRev = []
    for item in ListPci:
        item = item.replace(')', '(')
        item = item.split("(")
        del item[0]
        if len(item) > 0:
            del item[1]
        else:
            item = ['N/A']
        ListPciRev.extend(item)


    if vfio_int == False:
        for line in fileinput.FileInput("testfilemodprobe", inplace=1):
            if "options vfio-pci" in line:
                linetemp = line.replace('\n', "")
                linelist = linetemp.split("=")
                linelist = linelist[1].split(",")
                for item in linelist:
                    pci_ids[item] = True
            print(line,end="")
    else:
        vfio_linelist = []
        for line in fileinput.FileInput("testfilegrub", inplace=1):
            if "vfio" in line:
                vfio_linelist = line.split('"')
                for item in vfio_linelist:
                    if "vfio" in item:
                        vfio_linelist = item.split(' ')
                        for item in vfio_linelist:
                            if "vfio" in item:
                                vfio_linelist = item.split("=")
                                vfio_linelist = vfio_linelist[1].split(',')
            print(line,end="")
        for item in vfio_linelist:
            pci_ids[item] = True

    #Put the filtered data into one list
    PciView = [[ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0], pci_ids[ListPciIDs[0]]],
                [ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1], pci_ids[ListPciIDs[1]]]]

    while len(PciView) < len(ListPci):
        if len(PciView) <= len(ListPci):
            PciView.append("")
        PciView[len(PciView)-1] = [ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1], pci_ids[ListPciIDs[len(PciView)-1]]]

else:
    IOMMUSTATE = True
    lspci = subprocess.check_output(["sh", "resources/IOMMU-group.sh"])
    ListPci = str(lspci).split("\\n")
    ListPci[0] = ListPci[0].replace("b'", "")
    del ListPci[len(ListPci) - 1]

    ListPci = str(subprocess.check_output(["sh", "resources/IOMMU-group.sh"])).split("\\n")
    ListPci[0] = ListPci[0].replace("b'", "")
    del ListPci[len(ListPci) - 1]

    #Filter out the IOMMU group
    ListPciIOMMU = []
    for item in ListPci:
        item = item.split(" ")
        ListPciIOMMU.append(item[2])

    #Filter out the Domain and Bus IDs
    ListPciDomain = []
    for item in ListPci:
        item = item.split(" ")
        ListPciDomain.append(item[3])

    #Filter out the names of the PCI-devices
    ListPciName = []
    for item in ListPci:
        itemlist = item.split(" ")
        del(itemlist[0])
        item = ' '.join(itemlist)
        item = item.replace(":", " [")
        itemlist = item.split(" [")
        item = ''.join(itemlist[1]) + ":" + ''.join(itemlist[3])
        itemlist = item.split(" ")
        del(itemlist[0])
        ListPciName.append(' '.join(itemlist))

    #Filter out the IDs of the PCI-derrortoggle == 0evices
    ListPciIDs = []
    for item in ListPci:
        item = item.replace('[', ']')
        item = item.split("]")
        while ":" not in item[0] or len(item[0]) != 9:
            del item[0]
        while len(item) > 1:
            del item[1]
        ListPciIDs.append(item[0])
        pci_ids[item[0]] = False

    #Filter out the revisons of the PCI-devices
    ListPciRev = []
    for item in ListPci:
        item = item.replace(')', '(')
        item = item.split("(")
        del item[0]
        if len(item) > 0:
            del item[1]
        else:
            item = ['N/A']
        ListPciRev.extend(item)

    if vfio_int == False:
        for line in fileinput.FileInput("testfilemodprobe", inplace=1):
            if "options vfio-pci" in line:
                linetemp = line.replace('\n', "")
                linelist = linetemp.split("=")
                linelist = linelist[1].split(",")
                for item in linelist:
                    pci_ids[item] = True
            print(line,end="")
    else:
        for line in fileinput.FileInput("testfilegrub", inplace=1):
            if "vfio" in line:
                vfio_linelist = line.split('"')
                for item in vfio_linelist:
                    if "vfio" in item:
                        vfio_linelist = item.split(' ')
                        for item in vfio_linelist:
                            if "vfio" in item:
                                vfio_linelist = item.split("=")
                                vfio_linelist = vfio_linelist[1].split(',')
            print(line,end="")
        for item in vfio_linelist:
            pci_ids[item] = True

    #Put the filtered data into one list
    PciView = [[ListPciIOMMU[0], ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0], pci_ids[ListPciIDs[0]]],
                [ListPciIOMMU[1], ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1], pci_ids[ListPciIDs[1]]]]

    while len(PciView) < len(ListPci):
        if len(PciView) <= len(ListPci):
            PciView.append("")
        PciView[len(PciView)-1] = [ListPciIOMMU[len(PciView)-1], ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1], pci_ids[ListPciIDs[len(PciView)-1]]]

class MainWindow(Gtk.Window):
    def __init__(self):

        #Distro detection
         #Debian:0 Redhat:1 Arch:2
        print(IOMMUSTATE)
        self.distro = 0
        self.startup = True
        for line in fileinput.FileInput("testfileos", inplace=1):
            if "ID=arch" in line or "ID_LIKE=arch" in line:
                self.distro = 2
            elif "ID=debian" in line or "ID_LIKE=debian" in line:
                self.distro = 0
            elif "ID=redhat" in line or "ID_LIKE=redhat" in line or "ID=fedora" in line or "ID_LIKE=fedora" in line:
                self.distro = 1

            print(line,end="")
        if self.distro == 0:
            subprocess.call(["cp", "resources/vfioconf_modules.conf", "testfilemodprobe"])

        self.NVIDIAmodprobe = False
        self.NOUVEAUmodprobe = False
        self.AMDGPUmodprobe = False

        Gtk.Window.__init__(self, title="Vfio-conf")
        self.comptoggle = 0
        self.genrtoggle = 0
        self.errortoggle = 0

        BoxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        BoxMain.set_margin_top(6)
        BoxMain.set_margin_left(6)
        BoxMain.set_margin_right(6)
        self.add(BoxMain)

        self.CheckVfio = Gtk.CheckButton(" Vfio is compiled into the kernel")
        self.CheckVfio.connect("toggled", self.vfio_integrated_checked)
        BoxMain.add(self.CheckVfio)

        BoxOptions = Gtk.Box()
        BoxMain.add(BoxOptions)

        BoxOptions2 = Gtk.Box()
        BoxMain.add(BoxOptions2)

        BoxOptions3 = Gtk.Box()
        BoxMain.add(BoxOptions3)

        BoxOptions4 = Gtk.Box()
        BoxMain.add(BoxOptions4)

        self.ButtonVfioEnable = Gtk.Button.new_with_label("Enable Vfio")
        self.ButtonVfioEnable.connect("clicked", self.enable_vfio)
        BoxOptions.add(self.ButtonVfioEnable)
        self.ButtonVfioEnable.set_size_request(120, 0)

        self.LabelVfioEnable = Gtk.Label("Enable the loading of the vfio kernel-module on startup")
        self.LabelVfioEnable.set_margin_left(5)
        BoxOptions.add(self.LabelVfioEnable)

        self.ButtonVfioDisable = Gtk.Button.new_with_label("Disable Vfio")
        self.ButtonVfioDisable.connect("clicked", self.disable_vfio)
        BoxOptions2.add(self.ButtonVfioDisable)
        self.ButtonVfioDisable.set_size_request(120, 0)

        self.LabelVfioDisable = Gtk.Label("Disable the loading of the vfio kernel-module on startup")
        self.LabelVfioDisable.set_margin_left(5)
        BoxOptions2.add(self.LabelVfioDisable)

        ButtonEnableIommu = Gtk.Button.new_with_label("Enable Iommu")
        ButtonEnableIommu.connect("clicked", self.enable_iommu)
        BoxOptions3.add(ButtonEnableIommu)
        ButtonEnableIommu.set_size_request(120, 0)

        LabelIommuEnable = Gtk.Label("Enable IOMMU-mapping")
        LabelIommuEnable.set_margin_left(5)
        BoxOptions3.add(LabelIommuEnable)

        ButtonDisableIommu = Gtk.Button.new_with_label("Disable Iommu")
        ButtonDisableIommu.connect("clicked", self.disable_iommu)
        BoxOptions4.add(ButtonDisableIommu)
        ButtonDisableIommu.set_size_request(120, 0)

        LabelIommuDisable = Gtk.Label("Disable IOMMU-mapping")
        LabelIommuDisable.set_margin_left(5)
        BoxOptions4.add(LabelIommuDisable)

        FrameBlacklist = Gtk.Frame(label = "Driver blacklisting:")
        FrameBlacklist.set_margin_top(3)
        BoxMain.add(FrameBlacklist)
        FrameBlacklist.set_margin_left(3)
        FrameBlacklist.set_margin_right(3)

        GridBlacklist = Gtk.Grid()
        FrameBlacklist.add(GridBlacklist)

        BoxBlacklist1 = Gtk.Box()
        BoxBlacklist1.set_margin_top(2)
        GridBlacklist.add(BoxBlacklist1)

        BoxBlacklist2 = Gtk.Box()
        BoxBlacklist2.set_margin_top(5)
        GridBlacklist.attach_next_to(BoxBlacklist2, BoxBlacklist1, Gtk.PositionType.BOTTOM, 1, 2)

        BoxBlacklist3 = Gtk.Box()
        BoxBlacklist3.set_margin_top(5)
        GridBlacklist.attach_next_to(BoxBlacklist3, BoxBlacklist2, Gtk.PositionType.BOTTOM, 1, 2)

        if self.NVIDIAmodprobe == False:
            self.ButtonBlacklistNvidia = Gtk.Button.new_with_label("Blacklist NVIDIA")
            self.LabelBlacklistNvidia = Gtk.Label("Blacklist propietary NVIDIA drivers")
        else:
            self.ButtonBlacklistNvidia = Gtk.Button.new_with_label("Unblacklist NVIDIA")
            self.LabelBlacklistNvidia = Gtk.Label("Unblacklist propietary NVIDIA drivers")
        self.LabelBlacklistNvidia.set_margin_left(5)
        self.ButtonBlacklistNvidia.connect("clicked", self.blacklist_nvidia)
        BoxBlacklist1.add(self.ButtonBlacklistNvidia)
        BoxBlacklist1.add(self.LabelBlacklistNvidia)

        if self.NOUVEAUmodprobe == False:
            self.ButtonBlacklistNouveau = Gtk.Button.new_with_label("Blacklist Nouveau")
            self.LabelBlacklistNouveau = Gtk.Label("Blacklist opensource NVIDIA drivers")
        else:
            self.ButtonBlacklistNouveau = Gtk.Button.new_with_label("Unblacklist Nouveau")
            self.LabelBlacklistNouveau = Gtk.Label("Unblacklist opensource NVIDIA drivers")
        self.LabelBlacklistNouveau.set_margin_left(5)
        self.ButtonBlacklistNouveau.connect("clicked", self.blacklist_nouveau)
        BoxBlacklist2.add(self.ButtonBlacklistNouveau)
        BoxBlacklist2.add(self.LabelBlacklistNouveau)

        if self.AMDGPUmodprobe == False:
            self.ButtonBlacklistAmdgpu = Gtk.Button.new_with_label("Blacklist Amdgpu")
            self.LabelBlacklistAmdgpu = Gtk.Label("Blacklist AMD drivers")
        else:
            self.ButtonBlacklistAmdgpu = Gtk.Button.new_with_label("Unblacklist Amdgpu")
            self.LabelBlacklistAmdgpu = Gtk.Label("Unblacklist AMD drivers")
        self.LabelBlacklistAmdgpu.set_margin_left(5)
        self.ButtonBlacklistAmdgpu.connect("clicked", self.blacklist_amdgpu)
        BoxBlacklist3.add(self.ButtonBlacklistAmdgpu)
        BoxBlacklist3.add(self.LabelBlacklistAmdgpu)

        FramePci = Gtk.Frame(label = "Available PCI-devices:")
        BoxMain.add(FramePci)
        FramePci.set_margin_left(3)
        FramePci.set_margin_right(3)

        if IOMMUSTATE == False:
            PciColumns = ["Name", "Product and Vendor IDs", "Bus ID              ", "Revision"]
            self.ListmodelPci = Gtk.ListStore(str, str, str, str, bool)
        else:
            PciColumns = ["IOMMU", "Name", "Product and Vendor IDs", "Bus ID              ", "Revision"]
            self.ListmodelPci = Gtk.ListStore(str, str, str, str, str, bool)

        for item in PciView:
            self.ListmodelPci.append(list(item))
        PciTreeView = Gtk.TreeView(model=self.ListmodelPci)

        renderer_text = Gtk.CellRendererText()
        renderer_toggle = Gtk.CellRendererToggle()
        renderer_toggle.connect("toggled", self.on_cell_toggled)

        for i, column_title in enumerate(PciColumns):
            column = Gtk.TreeViewColumn(column_title, renderer_text, text=i)
            PciTreeView.append_column(column)

        if IOMMUSTATE == True:
            column_toggle = Gtk.TreeViewColumn("Vfio", renderer_toggle, active=5)
        else:
            column_toggle = Gtk.TreeViewColumn("Vfio", renderer_toggle, active=4)
        PciTreeView.append_column(column_toggle)

        PciTreeView.set_margin_left(3)
        PciTreeView.set_margin_right(3)
        FramePci.add(PciTreeView)
        FramePci.set_margin_top(6)

        BoxApply = Gtk.Box()
        BoxMain.add(BoxApply)

        ButtonApplyPci = Gtk.Button.new_with_label("Apply configuration")
        ButtonApplyPci.connect("clicked", self.apply_pci)
        ButtonApplyPci.set_size_request(120, 0)
        ButtonApplyPci.set_margin_top(6)
        ButtonApplyPci.set_margin_bottom(6)
        ButtonApplyPci.set_margin_left(6)
        ButtonApplyPci.set_margin_right(6)
        BoxApply.add(ButtonApplyPci)

        LabelApplyPci = Gtk.Label("Confirm the selection of the devices you want to pass through")
        LabelApplyPci.set_margin_left(5)
        BoxApply.add(LabelApplyPci)

        self.CheckVfio.set_active(vfio_int)

        distro_store = Gtk.ListStore(str)
        distros = ["Debian-based", "Redhat-based", "Arch-based"]
        for item in distros:
            distro_store.append([item])

        ComboDistro = Gtk.ComboBox.new_with_model(distro_store)
        ComboDistro.connect("changed", self.on_ComboDistro_changed)
        renderer_text = Gtk.CellRendererText()
        ComboDistro.set_margin_bottom(6)
        ComboDistro.pack_start(renderer_text, True)
        ComboDistro.add_attribute(renderer_text, "text", 0)
        BoxApply.pack_end(ComboDistro, False, False, 0)
        self.on_ComboDistro_changed(ComboDistro)

    #Buttons
    def on_ComboDistro_changed(self, combo):
        tree_iter = combo.get_active()
        model = combo.get_model()
        if self.startup == True:
            combo.set_active(self.distro)
            self.startup = False
        elif tree_iter is not -1:
            self.distro = model[tree_iter][0]

    def blacklist_nvidia(self, ButtonBlacklist):
        for line in fileinput.FileInput("testfilemodprobe",inplace=1):
            if self.NVIDIAmodprobe == True:
                if "blacklist nvidia-current" in line:
                    line = "#nvidia-current" + "\n"
                    self.NVIDIAmodprobe = False
                    self.ButtonBlacklistNvidia.set_label("Blacklist NVIDIA")
                    self.LabelBlacklistNvidia.set_text("Blacklist propietary NVIDIA drivers")
            else:
                if "nvidia-current" in line:
                    line = "blacklist nvidia-current" + "\n"
                    self.NVIDIAmodprobe = True
                    self.ButtonBlacklistNvidia.set_label("Unblacklist NVIDIA")
                    self.LabelBlacklistNvidia.set_text("Unblacklist propietary NVIDIA drivers")
            print(line,end="")

    def blacklist_nouveau(self, ButtonBlacklist):
        nextline = False
        for line in fileinput.FileInput("testfilemodprobe",inplace=1):
            if self.NOUVEAUmodprobe == True:
                if "nouveau" in line:
                    line = "#nouveau" + '\n'
                    self.NOUVEAUmodprobe = False
                    self.ButtonBlacklistNouveau.set_label("Blacklist Nouveau")
                    self.LabelBlacklistNouveau.set_text("Blacklist opensource NVIDIA drivers")
                    nextline = True
            else:
                if nextline == True:
                    line = ""
                    nextline = False
                elif "#nouveau" in line:
                    line = "blacklist nouveau" + '\n' + "options nouveau modeset=0" + "\n"
                    self.NOUVEAUmodprobe = True
                    self.ButtonBlacklistNouveau.set_label("Unblacklist Nouveau")
                    self.LabelBlacklistNouveau.set_text("Unblacklist opensource NVIDIA drivers")
            print(line,end="")

    def blacklist_amdgpu(self, ButtonBlacklist):
        for line in fileinput.FileInput("testfilemodprobe",inplace=1):
            if self.AMDGPUmodprobe == True:
                if "amdgpu" in line:
                    line = "#amdgpu" + "\n"
                    self.AMDGPUmodprobe = False
                    self.ButtonBlacklistAmdgpu.set_label("Blacklist Amdgpu")
                    self.LabelBlacklistAmdgpu.set_text("Blacklist AMD drivers")
            else:
                if "amdgpu" in line:
                    line = "blacklist amdgpu" + "\n"
                    self.AMDGPUmodprobe = True
                    self.ButtonBlacklistAmdgpu.set_label("Unblacklist Amdgpu")
                    self.LabelBlacklistAmdgpu.set_text("Unblacklist AMD drivers")
            print(line,end="")

    def apply_pci(self, ButtonApplyPci):
        pci_ids2 = []
        for item in pci_ids:
            if pci_ids[item] == True:
                pci_ids2.append(item)
        if self.CheckVfio.get_active() == False:
            for line in fileinput.FileInput("testfilemodprobe",inplace=1):
                if 0 < len(pci_ids2):
                    if "vfio-pci" in line:
                        line = "options vfio-pci ids=" + ','.join(pci_ids2) + '\n'
                else:
                    if "vfio-pci" in line:
                        line = "#vfio-pci" + '\n'
                print(line,end="")
            self.vfio_devices_updated(ButtonApplyPci)
        else:
            linelist = []
            linelist2 = []
            line2 = []
            counter = 0
            for line in fileinput.FileInput("testfilegrub",inplace=1):
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    self.errortoggle = 1
                    if "vfio-pci" in line:
                        self.genrtoggle = 1
                        linelist = line.split(' ')
                        linelist2 = linelist[0].split('"')
                        linel = linelist2[0]
                        linelist.insert(0, linel)
                        linelist[1] = linelist2[1]
                        for item in linelist:
                            if "vfio-pci" not in item:
                                if counter == 0 or counter == len(linelist)-2:
                                    line2.append(item)
                                counter = counter + 1
                            else:
                                line2.append("vfio-pci.ids=" + ','.join(pci_ids2) + " ")
                        line2[0] = line2[0] + '"'
                        linefin = ''.join(line2)
                        line = linefin
                    else:
                        line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="' + "vfio-pci.ids=" + ','.join(pci_ids2) + " ")
                        self.comptoggle = 1
                print(line,end="")
            if self.errortoggle == 0:
                self.invalid_grub_conf(self.ButtonVfioEnable)
            elif self.genrtoggle == 0:
                self.vfio_enabled(self.ButtonVfioEnable)
            elif self.comptoggle == 0:
                self.vfio_enabled_devices_updated(self.ButtonVfioEnable)
        self.genrtoggle = 0
        self.comptoggle = 0
        self.errortoggle = 0

    def on_cell_toggled(self, widget, path):
        if IOMMUSTATE == False:
            self.ListmodelPci[path][4] = not self.ListmodelPci[path][4]
            pci_ids[self.ListmodelPci[path][1]] = not pci_ids[self.ListmodelPci[path][1]]
        else:
            self.ListmodelPci[path][5] = not self.ListmodelPci[path][5]
            pci_ids[self.ListmodelPci[path][2]] = not pci_ids[self.ListmodelPci[path][2]]

    def vfio_integrated_checked(self, CheckVfio):
        vfio_int = CheckVfio.get_active()
        self.ButtonVfioEnable.set_sensitive(not vfio_int)
        self.ButtonVfioDisable.set_sensitive(not vfio_int)
        if vfio_int == True:
            self.LabelVfioEnable.set_text('Select the PCI-devices you want to pass through and press "Apply" to enable vfio')
            self.LabelVfioDisable.set_text('Unselect all PCI-devices and press "Apply" to disable vfio')
        else:
            self.LabelVfioEnable.set_text("Enable the loading of the vfio kernel-module on startup")
            self.LabelVfioDisable.set_text("Disable the loading of the vfio kernel-module on startup")
        if vfio_int == True:
            for line in fileinput.FileInput("testfilemodprobe", inplace=1):
                if "vfio-pci" in line:
                    line = "#vfio_int" + '\n'
                print(line,end="")
        else:
            for line in fileinput.FileInput("testfilemodprobe", inplace=1):
                if "vfio_int" in line:
                    line = "#vfio-pci" + '\n'
                print(line,end="")
            linelist = []
            linelist2 = []
            line2 = []
            counter = 0
            for line in fileinput.FileInput("testfilegrub",inplace=1):
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    if "vfio-pci" in line:
                        linelist = line.split(' ')
                        linelist2 = linelist[0].split('"')
                        linel = linelist2[0]
                        linelist.insert(0, linel)
                        linelist[1] = linelist2[1]
                        for item in linelist:
                            if "vfio-pci" not in item:
                                if counter == 0 or counter == len(linelist)-2:
                                    line2.append(item)
                                else:
                                    line2.append(item + " ")
                                counter = counter + 1
                        line2[0] = line2[0] + '"'
                        linefin = ''.join(line2)
                        line = linefin
                print(line,end="")

    def disable_vfio(self, ButtonVfioDisable):
        if self.distro == 2:
            if self.CheckVfio.get_active() == False:
                for line in fileinput.FileInput("testfileinitcpio",inplace=1):
                    if "HOOKS=" in line:
                        self.errortoggle = 1
                        if 'vfio' in line:
                            line = line.replace(" vfio_pci vfio vfio_iommu_type1 vfio_virqfd", "")
                            self.genrtoggle = 1
                    print(line, end="")
                if self.errortoggle == 0:
                    self.invalid_mkinitcpio_conf(self.ButtonVfioDisable)
                elif self.genrtoggle == 0:
                    self.vfio_not_enabled(self.ButtonVfioDisable)
                else:
                    self.vfio_disabled(self.ButtonVfioDisable)

        elif self.distro == 0:
            for line in fileinput.FileInput("testfilemodload", inplace=1):
                if "vfio" in line:
                    if "vfio_pci" in line:
                        self.vfio_already_disabled(self.ButtonVfioDisable)
                    else:
                        line = line.replace('vfio_pci vfio vfio_iommu_type1 vfio_virqfd', '#vfio')
                        self.vfio_disabled(self.ButtonVfioDisable)
                print(line, end="")
            if self.genrtoggle == 0:
                self.invalid_modload_conf(self.ButtonVfioDisable)

    def enable_vfio(self, ButtonVfioEnable):
        if self.CheckVfio.get_active() == False:
            if self.distro == 2:
                for line in fileinput.FileInput("testfileinitcpio",inplace=1):
                    if "HOOKS=" in line:
                        if "vfio" in line:
                            print(line, end="")
                            self.genrtoggle = 1
                            self.vfio_already_enabled(self.ButtonVfioEnable)
                        elif "keyboard" in line:
                            line = line.replace("keyboard", "keyboard vfio_pci vfio vfio_iommu_type1 vfio_virqfd")
                            print(line, end="")
                            self.genrtoggle = 1
                            self.vfio_enabled(self.ButtonVfioEnable)
                        else:
                            print(line, end="")
                if self.genrtoggle == 0:
                    self.invalid_mkinitcpio_conf(self.ButtonVfioEnable)

            elif self.distro == 0:
                for line in fileinput.FileInput("testfilemodload", inplace=1):
                    if "vfio" in line:
                        if "vfio_pci" in line:
                            self.vfio_already_enabled(self.ButtonVfioEnable)
                        else:
                            line = line.replace('#vfio', 'vfio_pci vfio vfio_iommu_type1 vfio_virqfd')
                            self.vfio_enabled(self.ButtonVfioEnable)
                    print(line, end="")
                if self.genrtoggle == 0:
                    self.invalid_modload_conf(self.ButtonVfioEnable)

    def disable_iommu(self, ButtonDisableIommu):
        for line in fileinput.FileInput('testfilegrub', inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                if 'intel_iommu=on amd_iommu=on iommu=on iommu=pt ' in line:
                    line = line.replace('intel_iommu=on amd_iommu=on iommu=on iommu=pt ','')
                    self.iommu_disabled(ButtonDisableIommu)
                    self.genrtoggle = 1
                self.errortoggle = 1
            print(line,end="")

        if self.errortoggle == 0:
            self.invalid_grub_conf(ButtonDisableIommu)
        elif self.genrtoggle == 0:
            self.iommu_not_enabled(ButtonDisableIommu)
        self.genrtoggle = 0
        self.comptoggle = 0
        self.errortoggle = 0

    def enable_iommu(self, ButtonEnableIommu):
        for line in fileinput.FileInput("testfilegrub", inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                self.errortoggle = 1
                if "iommu" in line:
                    print(line,end="")
                    self.iommu_already_enabled(ButtonEnableIommu)
                else:
                    line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="','GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on amd_iommu=on iommu=on iommu=pt ')
                    print(line,end="")
                    self.iommu_enabled(ButtonEnableIommu)
            else:
                    print(line,end="")
        if self.errortoggle == 0:
            self.invalid_grub_config(ButtonEnableIommu)

        self.genrtoggle = 0
        self.comptoggle = 0
        self.errortoggle = 0

    #Completiondialogs
    def vfio_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio enabled!")
        dialog.format_secondary_text("Vfio is now enabled")
        dialog.run()

        dialog.destroy()

    def vfio_devices_updated(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio devices updated!")
        dialog.format_secondary_text("Vfio devices updated")
        dialog.run()

        dialog.destroy()

    def vfio_enabled_devices_updated(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio enabled devices updated!")
        dialog.format_secondary_text(
            "Vfio enabled and devices updated")
        dialog.run()

        dialog.destroy()

    def vfio_disabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio disabled!")
        dialog.format_secondary_text("Vfio is now disabled")
        dialog.run()

        dialog.destroy()

    def iommu_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU now enabled!")
        dialog.format_secondary_text("IOMMU mapping now enabled")
        dialog.run()

        dialog.destroy()

    def iommu_disabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU now disabled!")
        dialog.format_secondary_text("IOMMU mapping now disabled")
        dialog.run()

        dialog.destroy()


    #Errordialogs
    def unsupported_distro(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Unsupported distribution!")
        dialog.format_secondary_text("This distro is not supported.")
        dialog.run()

        dialog.destroy()

    def invalid_grub_conf(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Invalid GRUB config!")
        dialog.format_secondary_text("Please check your GRUB config file")
        dialog.run()

        dialog.destroy()

    def invalid_mkinitcpio_conf(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Invalid mkinitcpio config!")
        dialog.format_secondary_text("Please check your mkinitcpio config file")
        dialog.run()

        dialog.destroy()

    def vfio_already_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio already enabled!")
        dialog.format_secondary_text("Vfio is already be enabled")
        dialog.run()

        dialog.destroy()

    def vfio_not_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio already disabled!")
        dialog.format_secondary_text("Vfio is already disabled")
        dialog.run()

        dialog.destroy()

    def iommu_not_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU already disabled!")
        dialog.format_secondary_text("IOMMU mapping is already disabled")
        dialog.run()

        dialog.destroy()

    def iommu_already_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU already enabled!")
        dialog.format_secondary_text("IOMMU mapping is already be enabled")
        dialog.run()

        dialog.destroy()


main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
