import gi
import fileinput
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk

#Variable initialization
vfio_int = False
distro = -1
iommustate = False
iommustate = False
startup = True
NVIDIAblacklist = False
NOUVEAUblacklist = False
AMDGPUblacklist = False

#Distro detection
for line in fileinput.FileInput("testfiles/testfileos", inplace=1):
    if "ID=arch" in line or "ID_LIKE=arch" in line:
        distro = 0
    elif "ID=debian" in line or "ID_LIKE=debian" in line:
        distro = 1
    elif "ID=redhat" in line or "ID_LIKE=redhat" in line or "ID=fedora" in line or "ID_LIKE=fedora" in line:
        distro = 2
    print(line,end="")

#Loading of custom modules
from modules import driver_blacklisting as blacklist
from modules import dialogs as dialog
from modules import loadconf as config
if iommustate == False:
    from modules import pci_data as pci
else:
    from modules import pci_data_iommu as pci
if distro == 0:
    from modules import vfio_arch as vfio

#Load previous configuration
config = config.load()
NVIDIAblacklist = config["nvidia"]
NOUVEAUblacklist = config["nouveau"]
AMDGPUblacklist = config["amd"]

#Get pci data
PciData = pci.data()

#IOMMU detection
if "IOMMU enabled" in str(subprocess.check_output(['sh', 'resources/IOMMU-check.sh'])):
    iommustate = True
else:
    iommustate = False

#Making sure configuration files exist
if distro == 1:
    if "vfioconf.conf" not in str(subprocess.check_output(['ls', '/etc/module-load.d'])):
        subprocess.call(["cp", "resources/vfioconf_modules.conf", "/etc/module-load.d/vfioconf.conf"])

class MainWindow(Gtk.Window):

    #TreeView
    def on_cell_toggled(self, widget, path):
        if iommustate == False:
            self.ListmodelPci[path][4] = not self.ListmodelPci[path][4]
            pci_ids[self.ListmodelPci[path][1]] = not pci_ids[self.ListmodelPci[path][1]]
        else:
            self.ListmodelPci[path][5] = not self.ListmodelPci[path][5]
            pci_ids[self.ListmodelPci[path][2]] = not pci_ids[self.ListmodelPci[path][2]]

    #Driver Blacklisting functions
    def blacklist_nvidia(self, ButtonBlacklist):
        global NVIDIAblacklist
        NVIDIAblacklist = blacklist.nvidia(self, NVIDIAblacklist)
        if NVIDIAblacklist == True:
            self.ButtonBlacklistNvidia.set_label("Unblacklist Nvidia")
            self.LabelBlacklistNvidia.set_text("Unblacklist propietary NVIDIA drivers")

        else:
            self.ButtonBlacklistNvidia.set_label("Blacklist Nvidia")
            self.LabelBlacklistNvidia.set_text("Blacklist propietary NVIDIA drivers")

    def blacklist_nouveau(self, ButtonBlacklist):
        global NOUVEAUblacklist
        NOUVEAUblacklist = blacklist.nouveau(self, NOUVEAUblacklist)
        if NOUVEAUblacklist == True:
            self.ButtonBlacklistNouveau.set_label("Unblacklist Nouveau")
            self.LabelBlacklistNouveau.set_text("Unblacklist opensource NVIDIA drivers")

        else:
            self.ButtonBlacklistNouveau.set_label("Blacklist Nouveau")
            self.LabelBlacklistNouveau.set_text("Blacklist opensource NVIDIA drivers")

    def blacklist_amdgpu(self, ButtonBlacklist):
        global AMDGPUblacklist
        AMDGPUblacklist = blacklist.amd(self, AMDGPUblacklist)
        if AMDGPUblacklist == True:
            self.ButtonBlacklistAmdgpu.set_label("Unblacklist Amdgpu")
            self.LabelBlacklistAmdgpu.set_text("Unblacklist AMD drivers")

        else:
            self.ButtonBlacklistAmdgpu.set_label("Blacklist Amdgpu")
            self.LabelBlacklistAmdgpu.set_text("Blacklist AMD drivers")



    #Distro selector
    def on_ComboDistro_changed(self, combo):
        global startup
        global distro
        tree_iter = combo.get_active()
        model = combo.get_model()
        if startup == True:
            combo.set_active(distro)
            startup = False
        elif tree_iter is not -1:
            distro = model[tree_iter][0]


    #Apply button
    def apply_pci(self, ButtonApplyPci):
        genrtoggle = 0
        comptoggle = 0
        errortoggle = 0
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
                    errortoggle = 1
                    if "vfio-pci" in line:
                        genrtoggle = 1
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
                        comptoggle = 1
                print(line,end="")
            if errortoggle == 0:
                self.invalid_grub_conf(self.ButtonVfioEnable)
            elif genrtoggle == 0:
                self.vfio_enabled(self.ButtonVfioEnable)
            elif comptoggle == 0:
                self.vfio_enabled_devices_updated(self.ButtonVfioEnable)


    #vfio integrated check
    def vfio_integrated_checked(self, CheckVfio):
        genrtoggle = 0
        comptoggle = 0
        errortoggle = 0
        vfio_int = CheckVfio.get_active()
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


    #IOMMU buttons
    def disable_iommu(self, ButtonDisableIommu):
        genrtoggle = 0
        comptoggle = 0
        errortoggle = 0
        for line in fileinput.FileInput('testfiles/testfilegrub', inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                if 'intel_iommu=on amd_iommu=on iommu=on iommu=pt ' in line:
                    line = line.replace('intel_iommu=on amd_iommu=on iommu=on iommu=pt ','')
                    self.iommu_disabled(ButtonDisableIommu)
                    genrtoggle = 1
                errortoggle = 1
            print(line,end="")

        if errortoggle == 0:
            dialog.invalid_grub_conf(self, ButtonDisableIommu)
        elif genrtoggle == 0:
            dialog.iommu_not_enabled(self, ButtonDisableIommu)


    def enable_iommu(self, ButtonEnableIommu):
        genrtoggle = 0
        comptoggle = 0
        errortoggle = 0
        for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
            if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                errortoggle = 1
                if "iommu" in line:
                    print(line,end="")
                    self.iommu_already_enabled(ButtonEnableIommu)
                else:
                    line = line.replace('GRUB_CMDLINE_LINUX_DEFAULT="','GRUB_CMDLINE_LINUX_DEFAULT="intel_iommu=on amd_iommu=on iommu=on iommu=pt ')
                    print(line,end="")
                    self.iommu_enabled(ButtonEnableIommu)
            else:
                    print(line,end="")
        if errortoggle == 0:
            self.invalid_grub_config(ButtonEnableIommu)

    #GUI
    def __init__(self):

        Gtk.Window.__init__(self, title="Vfio-conf")
        comptoggle = 0
        genrtoggle = 0
        errortoggle = 0

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

        if NOUVEAUblacklist == False:
            self.ButtonBlacklistNouveau = Gtk.Button.new_with_label("Blacklist Nouveau")
            self.LabelBlacklistNouveau = Gtk.Label("Blacklist opensource NVIDIA drivers")
        else:
            self.ButtonBlacklistNouveau = Gtk.Button.new_with_label("Unblacklist Nouveau")
            self.LabelBlacklistNouveau = Gtk.Label("Unblacklist opensource NVIDIA drivers")
        self.LabelBlacklistNouveau.set_margin_left(5)
        self.ButtonBlacklistNouveau.connect("clicked", self.blacklist_nouveau)
        BoxBlacklist2.add(self.ButtonBlacklistNouveau)
        BoxBlacklist2.add(self.LabelBlacklistNouveau)

        if AMDGPUblacklist == False:
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

        if iommustate == False:
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

        if iommustate == True:
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
        distros = ["Arch-based", "Debian-based", "Redhat-based"]
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




main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
