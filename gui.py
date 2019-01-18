import gi
import fileinput
import subprocess
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gio, Gtk, Pango, Gdk, XApp

#Get PCI data
lspci = subprocess.check_output(["lspci", "-nn"])
ListPci = str(lspci).split("\\n")
del ListPci[0]
del ListPci[len(ListPci) - 1]

#Filter out the Domain and Bus IDs
ListPciDomain = []
for item in ListPci:
    item = item.split(" ")
    while len(item) > 1:
        del item[1]
    ListPciDomain.extend(item)

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

#Filter out the IDs of the PCI-devices
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
PciView = [[ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0]],
            [ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1]]]


while len(PciView) < len(ListPci):
    if len(PciView) <= len(ListPci):
        PciView.append("")
    PciView[len(PciView)-1] = [ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1]]

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Vfio-conf")
        self.comptoggle = 0
        self.genrtoggle = 0
        self.errortoggle = 0

        BoxBasic = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        BoxBasic.set_margin_top(6)
        BoxBasic.set_margin_left(6)
        BoxBasic.set_margin_right(6)
        self.add(BoxBasic)

        LabelMain = Gtk.Label("Basic configuration options:")
        BoxBasic.add(LabelMain)

        self.CheckVfio = Gtk.CheckButton(" Vfio is compiled in (unfinished)")
        self.CheckVfio.connect("toggled", self.vfio_integrated_checked)
        BoxBasic.add(self.CheckVfio)

        BoxOptions = Gtk.Box()
        BoxBasic.add(BoxOptions)

        BoxOptions2 = Gtk.Box()
        BoxBasic.add(BoxOptions2)

        BoxOptions3 = Gtk.Box()
        BoxBasic.add(BoxOptions3)

        BoxOptions4 = Gtk.Box()
        BoxBasic.add(BoxOptions4)

        BoxOptions5 = Gtk.Box()
        BoxBasic.add(BoxOptions5)

        BoxOptions6 = Gtk.Box()
        BoxBasic.add(BoxOptions6)

        BoxOptions7 = Gtk.Box()
        BoxBasic.add(BoxOptions7)

        ButtonVfioEnable = Gtk.Button.new_with_label("Enable Vfio")
        ButtonVfioEnable.connect("clicked", self.enable_vfio)
        BoxOptions.add(ButtonVfioEnable)
        ButtonVfioEnable.set_size_request(120, 0)

        LabelVfioEnable = Gtk.Label("Enable the loading of the vfio kernel-module on startup")
        LabelVfioEnable.set_margin_left(5)
        BoxOptions.add(LabelVfioEnable)

        ButtonVfioDisable = Gtk.Button.new_with_label("Disable Vfio")
        ButtonVfioDisable.connect("clicked", self.disable_vfio)
        BoxOptions2.add(ButtonVfioDisable)
        ButtonVfioDisable.set_size_request(120, 0)

        LabelVfioDisable = Gtk.Label("Disable the loading of the vfio kernel-module on startup")
        LabelVfioDisable.set_margin_left(5)
        BoxOptions2.add(LabelVfioDisable)

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
        BoxBasic.add(FramePci)
        BoxPci = Gtk.Box()
        FramePci.add(BoxPci)

    #Buttons
    def vfio_integrated_checked(self, CheckVfio):
        vfio_integrated = CheckVfio.get_active()
        print("vfio_integrated = "+str(CheckVfio.get_active()))

    def disable_vfio(self, ButtonVfioDisable):
        if self.CheckVfio.get_active() == False:
            for line in fileinput.FileInput("testfileinitcpio",inplace=1):
                if 'vfio' in line:
                    line = line.replace(" vfio_pci vfio vfio_iommu_type1 vfio_virqfd", "")
                    self.genrtoggle = 1
                print(line, end="")
            if self.genrtoggle == 0:
                self.vfio_not_enabled(ButtonVfioDisable)
            else:
                self.vfio_disabled(ButtonVfioDisable)
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
                self.invalid_grub_conf(ButtonVfioDisable)
            elif self.genrtoggle == 0:
                self.vfio_not_enabled(ButtonVfioDisable)
            elif self.comptoggle == 1:
                self.vfio_disabled(ButtonVfioDisable)
        self.genrtoggle = 0


    def enable_vfio(self, ButtonVfioEnable):
        if self.CheckVfio.get_active() == False:
            for line in fileinput.FileInput("testfileinitcpio",inplace=1):
                if "vfio" in line:
                    print(line, end="")
                    self.vfio_already_enabled(ButtonVfioEnable)
                    self.genrtoggle = 1
                elif "keyboard" in line:
                    line = line.replace("keyboard", "keyboard vfio_pci vfio vfio_iommu_type1 vfio_virqfd")
                    print(line, end="")
                    self.genrtoggle = 1
                    self.vfio_enabled(ButtonVfioEnable)
                else:
                    print(line, end="")
            if self.genrtoggle == 0:
                self.invalid_mkinitcpio_conf(ButtonVfioEnable)
        else:
            pci_ids = "8942:4j3i,2344:0vd9"
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
                                line2.append("vfio_pci" + pci_ids + " ")
                        line2[0] = line2[0] + '"'
                        linefin = ''.join(line2)
                        line = linefin
                    else:
                        line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="', 'GRUB_CMDLINE_LINUX_DEFAULT="' + "vfio_pci:" + pci_ids + " ")
                        self.comptoggle = 1
                print(line,end="")
            if self.errortoggle == 0:
                self.invalid_grub_conf(ButtonVfioEnable)
            elif self.genrtoggle == 0:
                self.vfio_enabled(ButtonVfioEnable)
            elif self.comptoggle == 0:
                self.vfio_enabled_devices_updated(ButtonVfioEnable)
        self.genrtoggle = 0
        self.comptoggle = 0

    def disable_iommu(self, ButtonDisableIommu):
        for line in fileinput.FileInput('testfilegrub', inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                if 'intel_iommu=on amd_iommu=on iommu=on iommu=pt ' in line:
                    line = line.replace('intel_iommu=on amd_iommu=on iommu=on iommu=pt ','')
                    self.iommu_disabled(ButtonDisableIommu)
                    self.genrtoggle = 1
                self.errortoggle = 1
            print(line,end="")
        if self.genrtoggle == 0:
            self.iommu_not_enabled(ButtonDisableIommu)
        if self.errortoggle == 0:
            self.invalid_grub_conf(ButtonDisableIommu)
        self.genrtoggle = 0
        self.errortoggle = 0

    def enable_iommu(self, ButtonEnableIommu):
        for line in fileinput.FileInput("testfilegrub", inplace=1):
            if "iommu" in line:
                print(line,end="")
                self.iommu_already_enabled(ButtonEnableIommu)
            else:
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="','GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on amd_iommu=on iommu=on iommu=pt ')
                    print(line,end="")
                    self.iommu_enabled(ButtonEnableIommu)
                    self.errortoggle = 1
                else:
                    print(line,end="")
        if self.errortoggle == 0:
            self.invalid_grub_config(ButtonEnableIommu)

    #Completiondialogs
    def vfio_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio enabled!")
        dialog.format_secondary_text(
            "Vfio is now enabled")
        dialog.run()

        dialog.destroy()

    def vfio_devices_updated(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio devices updated!")
        dialog.format_secondary_text(
            "Vfio devices updated")
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
        dialog.format_secondary_text(
            "Vfio is now disabled")
        dialog.run()

        dialog.destroy()

    def iommu_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU now enabled!")
        dialog.format_secondary_text(
            "IOMMU mapping now enabled")
        dialog.run()

        dialog.destroy()

    def iommu_disabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU now disabled!")
        dialog.format_secondary_text(
            "IOMMU mapping now disabled")
        dialog.run()

        dialog.destroy()


    #Errordialogs
    def invalid_grub_conf(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Invalid GRUB config!")
        dialog.format_secondary_text(
            "Please check your GRUB config file")
        dialog.run()

        dialog.destroy()

    def invalid_mkinitcpio_conf(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Invalid mkinitcpio config!")
        dialog.format_secondary_text(
            "Please check your mkinitcpio config file")
        dialog.run()

        dialog.destroy()

    def vfio_already_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio already enabled!")
        dialog.format_secondary_text(
            "Vfio is already be enabled")
        dialog.run()

        dialog.destroy()

    def vfio_not_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio already disabled!")
        dialog.format_secondary_text(
            "Vfio is already disabled")
        dialog.run()

        dialog.destroy()

    def iommu_not_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU already disabled!")
        dialog.format_secondary_text(
            "IOMMU mapping is already disabled")
        dialog.run()

        dialog.destroy()

    def iommu_already_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "IOMMU already enabled!")
        dialog.format_secondary_text(
            "IOMMU mapping is already be enabled")
        dialog.run()

        dialog.destroy()


main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
