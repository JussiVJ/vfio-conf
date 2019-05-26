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
pci_ids = {}
NVIDIAblacklist = False
NOUVEAUblacklist = False
AMDGPUblacklist = False

startup = {}
startup["iommu"] = True
startup["distro"] = True

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
vfio_int = config["vfio-int"]

if NVIDIAblacklist == True:
    startup["nvidia"] = True
else:
    startup["nvidia"] = False

if NOUVEAUblacklist == True:
    startup["nouveau"] = True
else:
    startup["nouveau"] = False

if AMDGPUblacklist == True:
    startup["amd"] = True
else:
    startup["amd"] = False

if vfio_int == True:
    startup["vfio-int"] = True
else:
    startup["vfio-int"] = False

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

iommustart = iommustate

if iommustate == False:
    from modules import pci_data as pci
else:
    from modules import pci_data_iommu as pci

#Get pci data
PciData = pci.data()


for item in PciData:
    if iommustate == False:
        if item[1] in config["ids"]:
            item[4] = True
            pci_ids[item[1]] = True
        else:
            item[4] = False
            pci_ids[item[1]] = False
    else:
        if item[2] in config["ids"]:
            item[5] = True
            pci_ids[item[2]] = True
        else:
            item[5] = False
            pci_ids[item[2]] = False


for item in pci_ids:
    if pci_ids[item] == True:
        print(item)

#Making sure configuration files exist
if distro == 1:
    if "vfioconf.conf" not in str(subprocess.check_output(['ls', '/etc/module-load.d'])):
        subprocess.call(["cp", "resources/vfioconf_modules.conf", "/etc/module-load.d/vfioconf.conf"])

class MainWindow(Gtk.Window):

    #TreeView
    def on_cell_toggled(self, widget, path):
        if iommustart == False:
            self.ListmodelPci[path][4] = not self.ListmodelPci[path][4]
            pci_ids[self.ListmodelPci[path][1]] = not pci_ids[self.ListmodelPci[path][1]]
        else:
            self.ListmodelPci[path][5] = not self.ListmodelPci[path][5]
            pci_ids[self.ListmodelPci[path][2]] = not pci_ids[self.ListmodelPci[path][2]]

    #Driver Blacklisting functions
    def blacklist_nvidia(self, CheckBlacklistNvidia):
        global NVIDIAblacklist
        global startup
        if startup["nvidia"] != True:
            NVIDIAblacklist = blacklist.nvidia(NVIDIAblacklist)
        else:
            startup["nvidia"] = False

    def blacklist_nouveau(self, CheckBlacklistNouveau):
        global NOUVEAUblacklist
        global startup
        if startup["nouveau"] != True:
            NOUVEAUblacklist = blacklist.nouveau(NOUVEAUblacklist)
        else:
            startup["nouveau"] = False

    def blacklist_amdgpu(self, CheckBlacklistAmdgpu):
        global AMDGPUblacklist
        global startup
        if startup["amd"] != True:
            AMDGPUblacklist = blacklist.amd(AMDGPUblacklist)
        else:
            startup["amd"] = False


    #IOMMU toggled
    def toggle_iommu(self, CheckIommu):
        global iommustate
        global startup
        if startup["iommu"] == False:
            iommustate = iommutoggle.toggle()
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
        global startup
        global vfio_int

        if startup["vfio-int"] != True:

            if iommustart == True:
                for item in self.ListmodelPci:
                    item[5] = False
            else:
                for item in self.ListmodelPci:
                    item[4] = False
            for item in pci_ids:
                pci_ids[item] = False

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

        else:
            startup["vfio-int"] = False
        vfio_int = CheckVfio.get_active()



    #GUI
    def __init__(self):
        global iommustate

        Gtk.Window.__init__(self, title="Vfio-conf")

        BoxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=8, spacing=6)
        self.add(BoxMain)

        CheckVfio = Gtk.CheckButton(label=" Vfio is compiled into the kernel")
        CheckVfio.connect("toggled", self.vfio_integrated_checked)
        CheckVfio.set_active(vfio_int)
        BoxMain.add(CheckVfio)

        CheckIommu = Gtk.CheckButton(label="Enable Iommu")
        CheckIommu.connect("toggled", self.toggle_iommu)
        CheckIommu.set_active(iommustate)
        BoxMain.add(CheckIommu)
        CheckIommu.set_size_request(120, 0)

        FrameBlacklist = Gtk.Frame(label = "Driver blacklisting:", margin_left=3, margin_right=3)
        BoxMain.add(FrameBlacklist)

        GridBlacklist = Gtk.Grid(margin_top=3)
        FrameBlacklist.add(GridBlacklist)

        CheckBlacklistAmdgpu = Gtk.CheckButton(label="Blacklist AMDGPU drivers", margin_bottom=3)
        CheckBlacklistAmdgpu.connect("toggled", self.blacklist_amdgpu)
        CheckBlacklistAmdgpu.set_active(AMDGPUblacklist)
        GridBlacklist.add(CheckBlacklistAmdgpu)

        CheckBlacklistNvidia = Gtk.CheckButton(label="Blacklist protietary NVIDIA drivers", margin_bottom=3)
        CheckBlacklistNvidia.connect("toggled", self.blacklist_nvidia)
        CheckBlacklistNvidia.set_active(NVIDIAblacklist)
        GridBlacklist.attach_next_to(CheckBlacklistNvidia, CheckBlacklistAmdgpu, Gtk.PositionType.BOTTOM, 1, 1)

        CheckBlacklistNouveau = Gtk.CheckButton(label="Blacklist opensource NVIDIA drivers (nouveau)")
        CheckBlacklistNouveau.connect("toggled", self.blacklist_nouveau)
        CheckBlacklistNouveau.set_active(NOUVEAUblacklist)
        GridBlacklist.attach_next_to(CheckBlacklistNouveau, CheckBlacklistNvidia, Gtk.PositionType.BOTTOM, 1, 1)

        FramePci = Gtk.Frame(label="Available PCI-devices:", margin_left=3, margin_right=3)
        BoxMain.add(FramePci)

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
            active=5
        else:
            active=4
        column_toggle = Gtk.TreeViewColumn("Vfio", renderer_toggle, active=active)
        PciTreeView.append_column(column_toggle)
        FramePci.add(PciTreeView)

        BoxApply = Gtk.Box(spacing=5)
        BoxMain.add(BoxApply)

        ButtonApplyPci = Gtk.Button.new_with_label(label="Apply configuration")
        ButtonApplyPci.connect("clicked", self.apply_pci)
        ButtonApplyPci.set_size_request(120, 0)
        BoxApply.add(ButtonApplyPci)

        LabelApplyPci = Gtk.Label(label="Confirm the selection of the devices you want to pass through", margin_left=5)
        BoxApply.add(LabelApplyPci)

        distro_store = Gtk.ListStore(str)
        distros = ["Arch-based", "Debian-based", "Redhat-based"]
        for item in distros:
            distro_store.append([item])

        ComboDistro = Gtk.ComboBox.new_with_model(distro_store)
        ComboDistro.connect("changed", self.on_ComboDistro_changed)
        renderer_text = Gtk.CellRendererText()
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
