import gi
import fileinput
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk

#Variable initialization
vfio_int = False
distro = -1
iommustate = False
IOMMUSTATE = False
startup = False
NVIDIAblacklist = False
NOUVEAUblacklist = False
AMDGPUblacklist = True


#IOMMU detection
if "IOMMU enabled" in str(subprocess.check_output(['sh', 'resources/IOMMU-check.sh'])):
    iommustate = True
else:
    iommustate = False

#Distro detection
for line in fileinput.FileInput("testfiles/testfileos", inplace=1):
    if "ID=arch" in line or "ID_LIKE=arch" in line:
        distro = 0
    elif "ID=debian" in line or "ID_LIKE=debian" in line:
        distro = 1
    elif "ID=redhat" in line or "ID_LIKE=redhat" in line or "ID=fedora" in line or "ID_LIKE=fedora" in line:
        distro = 2

#Making sure configuration files exist
if distro == 1:
    if "vfioconf.conf" not in str(subprocess.check_output(['ls', '/etc/module-load.d'])):
        subprocess.call(["cp", "resources/vfioconf_modules.conf", "/etc/module-load.d/vfioconf.conf"])



#Loading of custom modules
from modules import driver_blacklisting as blacklist
if iommustate == False:
    from modules import pci_data as pci
else:
    from modules import pci_data_iommu as pci
if distro == 0:
    from modules import vfio_arch as vfio

#Get pci data
PciData = pci.data()

class MainWindow(Gtk.Window):
    def __init__(self):

        IOMMUSTATE = False
        self.startup = False
        NVIDIAblacklist = False
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

        BoxOptions = Gtk.Box(spacing=9)
        BoxMain.add(BoxOptions)

        BoxOptions2 = Gtk.Box(spacing=9)
        BoxMain.add(BoxOptions2)

        BoxOptions3 = Gtk.Box(spacing=9)
        BoxMain.add(BoxOptions3)

        BoxOptions4 = Gtk.Box(spacing=9)
        BoxMain.add(BoxOptions4)

        self.ButtonVfioEnable = Gtk.Button.new_with_label("Enable Vfio")
        self.ButtonVfioEnable.connect("clicked", self.enable_vfio)
        BoxOptions.add(self.ButtonVfioEnable)
        self.ButtonVfioEnable.set_size_request(120, 0)

        self.LabelVfioEnable = Gtk.Label("Enable the loading of the vfio kernel-module on startup")
        BoxOptions.add(self.LabelVfioEnable)

        self.ButtonVfioDisable = Gtk.Button.new_with_label("Disable Vfio")
        self.ButtonVfioDisable.connect("clicked", self.disable_vfio)
        BoxOptions2.add(self.ButtonVfioDisable)
        self.ButtonVfioDisable.set_size_request(120, 0)

        self.LabelVfioDisable = Gtk.Label("Disable the loading of the vfio kernel-module on startup")
        BoxOptions2.add(self.LabelVfioDisable)

        ButtonEnableIommu = Gtk.Button.new_with_label("Enable Iommu")
        ButtonEnableIommu.connect("clicked", self.enable_iommu)
        BoxOptions3.add(ButtonEnableIommu)
        ButtonEnableIommu.set_size_request(120, 0)

        LabelIommuEnable = Gtk.Label("Enable IOMMU-mapping")
        BoxOptions3.add(LabelIommuEnable)

        ButtonDisableIommu = Gtk.Button.new_with_label("Disable Iommu")
        ButtonDisableIommu.connect("clicked", self.disable_iommu)
        BoxOptions4.add(ButtonDisableIommu)
        ButtonDisableIommu.set_size_request(120, 0)

        LabelIommuDisable = Gtk.Label("Disable IOMMU-mapping")
        BoxOptions4.add(LabelIommuDisable)

        FrameBlacklist = Gtk.Frame(label = "Driver blacklisting:")
        FrameBlacklist.set_margin_top(3)
        BoxMain.add(FrameBlacklist)
        FrameBlacklist.set_margin_left(3)
        FrameBlacklist.set_margin_right(3)

        GridBlacklist = Gtk.Grid()
        FrameBlacklist.add(GridBlacklist)

        BoxBlacklist1 = Gtk.Box(spacing=5)
        BoxBlacklist1.set_margin_top(2)
        GridBlacklist.add(BoxBlacklist1)

        BoxBlacklist2 = Gtk.Box(spacing=5)
        BoxBlacklist2.set_margin_top(5)
        GridBlacklist.attach_next_to(BoxBlacklist2, BoxBlacklist1, Gtk.PositionType.BOTTOM, 1, 2)

        BoxBlacklist3 = Gtk.Box(spacing=5)
        BoxBlacklist3.set_margin_top(5)
        GridBlacklist.attach_next_to(BoxBlacklist3, BoxBlacklist2, Gtk.PositionType.BOTTOM, 1, 2)

        if NVIDIAblacklist == False:
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

        for item in PciData:
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



    def vfio_disable(self, ButtonVfioDisable):
        result = vfio.disable()
        if result == "invalid_mkinitcpio_conf":
            self.invalid_mkinitcpio_conf(self.ButtonVfioDisable)
        elif result == "vfio_not_enabled":
            self.vfio_not_enabled(self.ButtonVfioDisable)
        elif result == "vfio_disabled":
            self.vfio_disabled(self.ButtonVfioDisable)
        else:
            self.vfio_arch_disable_error(self.ButtonVfioDisable)

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
        for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
            NVIDIAblacklist = blacklist.nvidia(self, NVIDIAblacklist)
            if NVIDIAblacklist == True:
                self.ButtonBlacklistNvidia.set_label("Unblacklist Nvidia")
                self.LabelBlacklistNvidia.set_text("Unblacklist propietary NVIDIA drivers")

            else:
                self.ButtonBlacklistNvidia.set_label("Blacklist Nvidia")
                self.LabelBlacklistNvidia.set_text("Blacklist propietary NVIDIA drivers")

    def blacklist_nouveau(self, ButtonBlacklist):
        NOUVEAUblacklist = blacklist.nouveau(self, NOUVEAUblacklist)
        if NOUVEAUblacklist == True:
            self.ButtonBlacklistNouveau.set_label("Unblacklist Nouveau")
            self.LabelBlacklistNouveau.set_text("Unblacklist opensource NVIDIA drivers")

        else:
            self.ButtonBlacklistNouveau.set_label("Blacklist Nouveau")
            self.LabelBlacklistNouveau.set_text("Blacklist opensource NVIDIA drivers")

    def blacklist_amdgpu(self, ButtonBlacklist):
        AMDGPUblacklist = blacklist.amd(self, AMDGPUblacklist)
        if AMDGPUblacklist == True:
            self.ButtonBlacklistAmdgpu.set_label("Unblacklist Amdgpu")
            self.LabelBlacklistAmdgpu.set_text("Unblacklist AMD drivers")

        else:
            self.ButtonBlacklistAmdgpu.set_label("Blacklist Amdgpu")
            self.LabelBlacklistAmdgpu.set_text("Blacklist AMD drivers")

    def apply_pci(self, ButtonApplyPci):
        pci_ids2 = []
        for item in pci_ids:
            if pci_ids[item] == True:
                pci_ids2.append(item)
        if self.CheckVfio.get_active() == False:
            for line in fileinput.FileInput("testfiles/testfilemodprobe",inplace=1):
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
            for line in fileinput.FileInput("testfiles/testfilegrub",inplace=1):
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
            for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
                if "vfio-pci" in line:
                    line = "#vfio_int" + '\n'
                print(line,end="")
        else:
            for line in fileinput.FileInput("testfiles/testfilemodprobe", inplace=1):
                if "vfio_int" in line:
                    line = "#vfio-pci" + '\n'
                print(line,end="")
            linelist = []
            linelist2 = []
            line2 = []
            counter = 0
            for line in fileinput.FileInput("testfiles/testfilegrub",inplace=1):
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
            print("foobar")

        elif self.distro == 0:
            for line in fileinput.FileInput("testfiles/testfilemodload", inplace=1):
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
                for line in fileinput.FileInput("testfiles/testfileinitcpio",inplace=1):
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
                for line in fileinput.FileInput("testfiles/testfilemodload", inplace=1):
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
        for line in fileinput.FileInput('testfiles/testfilegrub', inplace=1):
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
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
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
