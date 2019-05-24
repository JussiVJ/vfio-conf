import gi
import fileinput
import subprocess
from sys import exit
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#Variable initialization
vfio_int = False
distro = -1
iommustate = False
iommutest = False
startup = {}
startup["iommu"] = True
startup["distro"] = True
pci_ids = {}
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
from modules import iommutoggle
from modules import dialogs as dialog
from modules import loadconf as config
from modules import apply

#Load previous configuration
config = config.load()
NVIDIAblacklist = config["nvidia"]
NOUVEAUblacklist = config["nouveau"]
AMDGPUblacklist = config["amd"]

#IOMMU detection
try:
    if "IOMMU enabled" in str(subprocess.check_output(['sh', 'resources/IOMMU-check.sh'])):
        iommustate = True
    else:
        iommustate = False
except:
    iommutest = True

if iommutest == True:
    for line in fileinput.FileInput("testfiles/testfilegrub", inplace=1):
        if 'GRUB_CMDLINE_LINUX_DEFAULT' in line and "iommu" in line:
            iommutest = False
            iommustate = True
        print(line,end="")

print(iommustate)


if iommustate == False:
    from modules import pci_data as pci
else:
    from modules import pci_data_iommu as pci

#Get pci data
PciData = pci.data()

for item in PciData:
    if iommustate == False:
        pci_ids[item[1]] = False
    else:
        pci_ids[item[2]] = False


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

    #IOMMU toggled
    def toggle_iommu(self, CheckIommu):
        global iommustate
        global startup
        if startup["iommu"] == False:
            iommustate = iommutoggle.toggle()
            print("sacc")
        else:
            startup["iommu"] = False
            CheckIommu.set_active(iommustate)


    #Distro selector
    def on_ComboDistro_changed(self, combo):
        global startup
        global distro
        tree_iter = combo.get_active()
        model = combo.get_model()
        if startup["distro"] == True:
            combo.set_active(distro)
            startup["distro"] = False
        elif tree_iter is not -1:
            distro = model[tree_iter][0]


    #Apply button
    def apply_pci(self, ButtonApplyPci):
        global distro
        if distro == 0:  #Arch
            apply.arch(self, vfio_int, pci_ids)


    #vfio integrated check
    def vfio_integrated_checked(self, CheckVfio):
        if CheckVfio.get_active() == True:
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
            for line in fileinput.FileInput("testfiles/testfilegrub",inplace=1):
                if "GRUB_CMDLINE_LINUX_DEFAULT" in line and "vfio-pci" in line:
                        for item in ''.join(line.split('"')).split(' '):
                            if 'vfio-pci' not in item and 'GRUB_CMDLINE_LINUX_DEFAULT' not in item:
                                linelist.append(item)
                        linelist[len(linelist)-1] = linelist[len(linelist)-1].replace('\n', '"' + '\n')
                        line = 'GRUB_CMDLINE_LINUX_DEFAULT="' + ' '.join(linelist)
                        result = False
                print(line,end="")


    #GUI
    def __init__(self):
        global iommustate

        Gtk.Window.__init__(self, title="Vfio-conf")

        BoxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=8, spacing=6)
        self.add(BoxMain)

        self.CheckVfio = Gtk.CheckButton(label=" Vfio is compiled into the kernel")
        self.CheckVfio.connect("toggled", self.vfio_integrated_checked)
        BoxMain.add(self.CheckVfio)

        CheckIommu = Gtk.CheckButton(label="Enable Iommu")
        CheckIommu.connect("toggled", self.toggle_iommu)
        CheckIommu.set_active(iommustate)
        BoxMain.add(CheckIommu)
        CheckIommu.set_size_request(120, 0)

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
            self.ButtonBlacklistNvidia = Gtk.Button.new_with_label(label="Blacklist NVIDIA")
            self.LabelBlacklistNvidia = Gtk.Label(label="Blacklist propietary NVIDIA drivers")
        else:
            self.ButtonBlacklistNvidia = Gtk.Button.new_with_label(label="Unblacklist NVIDIA")
            self.LabelBlacklistNvidia = Gtk.Label(label="Unblacklist propietary NVIDIA drivers")
        self.LabelBlacklistNvidia.set_margin_left(5)
        self.ButtonBlacklistNvidia.connect("clicked", self.blacklist_nvidia)
        BoxBlacklist1.add(self.ButtonBlacklistNvidia)
        BoxBlacklist1.add(self.LabelBlacklistNvidia)

        if NOUVEAUblacklist == False:
            self.ButtonBlacklistNouveau = Gtk.Button.new_with_label(label="Blacklist Nouveau")
            self.LabelBlacklistNouveau = Gtk.Label(label="Blacklist opensource NVIDIA drivers")
        else:
            self.ButtonBlacklistNouveau = Gtk.Button.new_with_label(label="Unblacklist Nouveau")
            self.LabelBlacklistNouveau = Gtk.Label(label="Unblacklist opensource NVIDIA drivers")
        self.LabelBlacklistNouveau.set_margin_left(5)
        self.ButtonBlacklistNouveau.connect("clicked", self.blacklist_nouveau)
        BoxBlacklist2.add(self.ButtonBlacklistNouveau)
        BoxBlacklist2.add(self.LabelBlacklistNouveau)

        if AMDGPUblacklist == False:
            self.ButtonBlacklistAmdgpu = Gtk.Button.new_with_label(label="Blacklist Amdgpu")
            self.LabelBlacklistAmdgpu = Gtk.Label(label="Blacklist AMD drivers")
        else:
            self.ButtonBlacklistAmdgpu = Gtk.Button.new_with_label(label="Unblacklist Amdgpu")
            self.LabelBlacklistAmdgpu = Gtk.Label(label="Unblacklist AMD drivers")
        self.LabelBlacklistAmdgpu.set_margin_left(5)
        self.ButtonBlacklistAmdgpu.connect("clicked", self.blacklist_amdgpu)
        BoxBlacklist3.add(self.ButtonBlacklistAmdgpu)
        BoxBlacklist3.add(self.LabelBlacklistAmdgpu)

        FramePci = Gtk.Frame(label="Available PCI-devices:")
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
            self.ListmodelPci.append(item)
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

        ButtonApplyPci = Gtk.Button.new_with_label(label="Apply configuration")
        ButtonApplyPci.connect("clicked", self.apply_pci)
        ButtonApplyPci.set_size_request(120, 0)
        ButtonApplyPci.set_margin_top(6)
        ButtonApplyPci.set_margin_bottom(6)
        ButtonApplyPci.set_margin_left(6)
        ButtonApplyPci.set_margin_right(6)
        BoxApply.add(ButtonApplyPci)

        LabelApplyPci = Gtk.Label(label="Confirm the selection of the devices you want to pass through")
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

        if iommustate == False:
            self.toggle_iommu(CheckIommu)


main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
