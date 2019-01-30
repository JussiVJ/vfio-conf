import gi
import fileinput
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk

#Get PCI data
if "IOMMU enabled" not in str(subprocess.check_output(['sh', 'IOMMU-check.sh'])):
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
        item = item.replace(": ", " [")
        item = str(item).split(" [")
        del item[0]
        del item[0]
        while len(item) > 1:
            del item[1]
        ListPciName.extend(item)

    #Filter out the IDs of the PCI-dself.errortoggle == 0evices
    ListPciIDs = []
    for item in ListPci:
        item = item.replace('[', ']')
        item = item.split("]")
        while ":" not in item[0] or len(item[0]) != 9:
            del item[0]
        while len(item) > 1:
            del item[1]
        ListPciIDs.extend(item)

    #Filter out the revisons of the PCI-devices
    ListPciRev = []
    for item in ListPci:
        item = item.replace(')', '(')
        item = item.split("(")
        del item[0]
        del item[1]
        ListPciRev.extend(item)

    #Put the filtered data into one list
    PciView = [[ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0], False],
                [ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1], False]]

    while len(PciView) < len(ListPci):
        if len(PciView) <= len(ListPci):
            PciView.append("")
        PciView[len(PciView)-1] = [ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1], False]

else:
    IOMMUSTATE = True
    lspci = subprocess.check_output(["sh", "IOMMU-group.sh"])
    ListPci = str(lspci).split("\\n")
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
        item = item.replace(": ", " [")
        item = str(item).split(" [")
        del item[0]
        del item[0]
        while len(item) > 1:
            del item[1]
        ListPciName.extend(item)

    #Filter out the IDs of the PCI-dself.errortoggle == 0evices
    ListPciIDs = []
    for item in ListPci:
        item = item.replace('[', ']')
        item = item.split("]")
        while ":" not in item[0] or len(item[0]) != 9:
            del item[0]
        while len(item) > 1:
            del item[1]
        ListPciIDs.extend(item)

    #Filter out the revisons of the PCI-devices
    ListPciRev = []
    for item in ListPci:
        item = item.replace(')', '(')
        item = item.split("(")
        del item[0]
        del item[1]
        ListPciRev.extend(item)

    #Put the filtered data into one list
    PciView = [[ListPciIOMMU[0], ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0], False],
                [ListPciIOMMU[1], ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1], False]]

    while len(PciView) < len(ListPci):
        if len(PciView) <= len(ListPci):
            PciView.append("")
        PciView[len(PciView)-1] = [ListPciIOMMU[len(PciView)-1], ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1], False]

class MainWindow(Gtk.Window):
    def __init__(self):
        self.pci_ids = []
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

        BoxOptions5 = Gtk.Box()
        BoxMain.add(BoxOptions5)

        self.ButtonBlacklist = Gtk.Button.new_with_label("Blacklist drivers")
        self.ButtonBlacklist.connect("clicked", self.driver_blacklist)
        BoxOptions5.add(self.ButtonBlacklist)
        self.ButtonBlacklist.set_size_request(120, 0)

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

        FramePci = Gtk.Frame(label = "Avaivable PCI-devices:")
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

        column_toggle = Gtk.TreeViewColumn("Toggle", renderer_toggle, active=4)
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

    #Buttons
    def driver_blacklist(self, ButtonBlacklist):
        print(" ")

    def apply_pci(self, ButtonApplyPci):
        if self.CheckVfio.get_active() == False:
            for line in fileinput.FileInput("testfilemodprobe",inplace=1):
                if 0 < len(self.pci_ids):
                    line = "options vfio-pci ids=" + ','.join(self.pci_ids)
                    print(line,end="")
                else:
                    line = "#placeholder"
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
                    if "vfio_pci" in line:
                        self.genrtoggle = 1
                        linelist = line.split(' ')
                        linelist2 = linelist[0].split('"')
                        linel = linelist2[0]
                        linelist.insert(0, linel)
                        linelist[1] = linelist2[1]
                        for item in linelist:
                            if "vfio_pci" not in item:
                                if counter == 0 or counter == len(linelist)-2:
                                    line2.append(item)
                                counter = counter + 1
                            else:
                                line2.append("vfio_pci" + self.pci_ids + " ")
                        line2[0] = line2[0] + '"'
                        linefin = ''.join(line2)
                        line = linefin
                    else:
                        line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="' + "vfio_pci:" + self.pci_ids + " ")
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
        self.ListmodelPci[path][4] = not self.ListmodelPci[path][4]
        if self.ListmodelPci[path][1] in self.pci_ids:
            for x in range(len(self.pci_ids)):
                if self.ListmodelPci[path][1] in self.pci_ids[x]:
                    del self.pci_ids[x]
                    break
        else:
            self.pci_ids.append(self.ListmodelPci[path][1])

    def vfio_integrated_checked(self, CheckVfio):
        vfio_integrated = CheckVfio.get_active()
        self.ButtonVfioEnable.set_sensitive(not vfio_integrated)
        self.ButtonVfioDisable.set_sensitive(not vfio_integrated)
        if vfio_integrated == True:
            self.LabelVfioEnable.set_text('Select the PCI-devices you want to pass through and press "Apply" to enable vfio')
            self.LabelVfioDisable.set_text('Unselect all PCI-devices and press "Apply" to disable vfio')
        else:
            self.LabelVfioEnable.set_text("Enable the loading of the vfio kernel-module on startup")
            self.LabelVfioDisable.set_text("Disable the loading of the vfio kernel-module on startup")

    def disable_vfio(self, ButtonVfioDisable):
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
        else:
            linelist = []
            linelist2 = []
            line2 = []
            counter = 0
            for line in fileinput.FileInput("testfilegrub",inplace=1):
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    self.errortoggle = 1
                    if "vfio_pci" in line:
                        self.genrtoggle = 1
                        linelist = line.split(' ')
                        linelist2 = linelist[0].split('"')
                        linel = linelist2[0]
                        linelist.insert(0, linel)
                        linelist[1] = linelist2[1]
                        for item in linelist:
                            if "vfio_pci" not in item:
                                if counter == 0 or counter == len(linelist)-2:
                                    line2.append(item)
                                    self.comptoggle = 1
                                else:
                                    line2.append(item + " ")
                                counter = counter + 1
                        line2[0] = line2[0] + '"'
                        linefin = ''.join(line2)
                        line = linefin
                print(line,end="")
            if self.errortoggle == 0:
                self.invalid_grub_conf(self.ButtonVfioDisable)
            elif self.genrtoggle == 0:
                self.vfio_not_enabled(self.ButtonVfioDisable)
            elif self.comptoggle == 1:
                self.vfio_disabled(self.ButtonVfioDisable)
        self.genrtoggle = 0
        self.comptoggle = 0
        self.errortoggle = 0

    def enable_vfio(self, ButtonVfioEnable):
        if self.CheckVfio.get_active() == False:
            for line in fileinput.FileInput("testfileinitcpio",inplace=1):
                if "HOOKS=" in line:
                    if "vfio" in line:
                        print(line, end="")
                        self.vfio_already_enabled(self.ButtonVfioEnable)
                        self.genrtoggle = 1
                    elif "keyboard" in line:
                        line = line.replace("keyboard", "keyboard vfio_pci vfio vfio_iommu_type1 vfio_virqfd")
                        print(line, end="")
                        self.genrtoggle = 1
                        self.vfio_enabled(self.ButtonVfioEnable)
                else:
                    print(line, end="")
            if self.genrtoggle == 0:
                self.invalid_mkinitcpio_conf(self.ButtonVfioEnable)
        else:
            linelist = []
            linelist2 = []
            line2 = []
            counter = 0
            for line in fileinput.FileInput("testfilegrub",inplace=1):
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    self.errortoggle = 1
                    if "vfio_pci" in line:
                        self.genrtoggle = 1
                        linelist = line.split(' ')
                        linelist2 = linelist[0].split('"')
                        linel = linelist2[0]
                        linelist.insert(0, linel)
                        linelist[1] = linelist2[1]
                        for item in linelist:
                            if "vfio_pci" not in item:
                                if counter == 0 or counter == len(linelist)-2:
                                    line2.append(item)
                                counter = counter + 1
                            else:
                                line2.append("vfio_pci" + ','.join(self.pci_ids) + " ")
                        line2[0] = line2[0] + '"'
                        linefin = ''.join(line2)
                        line = linefin
                    else:
                        line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="' + "vfio_pci:" + self.pci_ids + " ")
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
