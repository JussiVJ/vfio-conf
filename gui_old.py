


for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
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
        for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
            if "options vfio-pci" in line:
                linetemp = line.replace('\n', "")
                linelist = linetemp.split("=")
                linelist = linelist[1].split(",")
                for item in linelist:
                    pci_ids[item] = True
            print(line,end="")
    else:
        vfio_linelist = []
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
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

    for item in PciView:
        if "PCI bridge" not in item[0] and "Host bridge" not in item[0] and "ISA bridge" not in item[0]:
            PciViewFin.append(item)

else:
    IOMMUSTATE = True

class MainWindow(Gtk.Window):
    def __init__(self):

        #Distro detection
         #Debian

            print(line,end="")
        if self.distro == 0:
            subprocess.call(["cp", "resources/vfioconf_modules.conf", "testfiles/testfilemodprobe"])

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

        for item in PciViewFin:
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



    #Completiondialogs



main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
