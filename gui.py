import gi
import fileinput
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gio, Gtk, Pango, Gdk, XApp

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Vfio-conf")

        BoxBasic = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        BoxBasic.set_margin_top(6)
        BoxBasic.set_margin_left(6)
        BoxBasic.set_margin_right(6)
        self.add(BoxBasic)

        LabelMain = Gtk.Label("Basic configuration options")
        BoxBasic.add(LabelMain)

        self.CheckVfio = Gtk.CheckButton("Vfio is compiled in")
        self.CheckVfio.connect("toggled", self.vfio_integrated_checked)
        BoxBasic.add(self.CheckVfio)

        PanedBasic = Gtk.HPaned()
        BoxBasic.add(PanedBasic)

        PanedBasic2 = Gtk.HPaned()
        BoxBasic.add(PanedBasic2)

        ButtonVfioEnable = Gtk.Button.new_with_label("Enable Vfio")
        ButtonVfioEnable.connect("clicked", self.enable_vfio)
        PanedBasic.add(ButtonVfioEnable)
        ButtonVfioEnable.set_size_request(120, 0)

        ButtonVfioDisable = Gtk.Button.new_with_label("Disable Vfio")
        ButtonVfioDisable.connect("clicked", self.disable_vfio)
        PanedBasic.add(ButtonVfioDisable)

        ButtonEnableIommu = Gtk.Button.new_with_label("Enable Iommu")
        ButtonEnableIommu.connect("clicked", self.enable_iommu)
        PanedBasic2.add(ButtonEnableIommu)

        ButtonDisableIommu = Gtk.Button.new_with_label("Disable Iommu")
        ButtonDisableIommu.connect("clicked", self.disable_iommu)
        PanedBasic2.add(ButtonDisableIommu)

        FramePci = Gtk.Frame()

#Buttons and other actions
    def vfio_integrated_checked(self, CheckVfio):
        vfio_integrated = CheckVfio.get_active()
        print("vfio_integrated = "+str(CheckVfio.get_active()))

    def disable_vfio(self, ButtonVfioDisable):
        if self.CheckVfio.get_active() == 'False':
            for line in fileinput.FileInput("/etc/mkinitcpio.conf",inplace=1):
                if 'vfio' in line:
                    line = line.replace(" vfio_pci vfio vfio_iommu_type1 vfio_virqfd", "")
                print(line, end=" ")
        elif pci_chosen == 'true':
            for line in fileinput.FileInput("etc/default/grub",inplace=1):
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    line = line.replace("GRUB_CMDLINE_LINUX_DEFAULT=","GRUB_CMDLINE_LINUX_DEFAULT="+" vfio_ids="+vfio_ids)
                else:
                    self.invalid_grub_conf()

    def enable_vfio(self, ButtonVfioEnable):
        if self.CheckVfio.get_active() == 'False':
            for line in fileinput.FileInput("/etc/mkinitcpio.conf",inplace=1):
                if "vfio" in line:
                    print(line, end=" ")
                    self.vfio_already_enabled()
                elif "keyboard" in line:
                    line = line.replace("keyboard"+"keyboard"" vfio_pci vfio vfio_iommu_type1 vfio_virqfd")
                    print(line, end=" ")
                else:
                    self.invalid_grub_conf()

    def disable_iommu(self, ButtonDisableIommu):
        word = 'intel_iommu=on amd_iommu=on iommu=on iommu=pt '
        grub_config = '/etc/default/grub'
        for line in fileinput.FileInput(grub_config, inplace=1):
            if word in line:
                line = line.replace(word,'')
            print(line,end=" ")

    def enable_iommu(self, ButtonEnableIommu):
        for line in fileinput.FileInput("/etc/default/grub", inplace=1):
            if "iommu" in line:
                print(line,end=" ")
            else:
                if "GRUB_CMDLINE_LINUX_DEFAULT=" in line:
                    line = line.replace("GRUB_CMDLINE_LINUX_DEFAULT=","GRUB_CMDLINE_LINUX_DEFAULT="+"intel_iommu=on amd_iommu=on iommu=on iommu=pt ")
                    print(line,end=" ")

#Errordialogs
    def invalid_grub_conf(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Invalid GRUB config!")
        dialog.format_secondary_text(
            "Please check your GRUB config file and if it's fine file create a new issue on github.")
        dialog.run()

        dialog.destroy()

    def vfio_already_enabled(self, widget, data=None):
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Vfio already enabled!")
        dialog.format_secondary_text(
            "Vfio should already be enable, but if it's not create a new issue on github.")
        dialog.run()

        dialog.destroy()



main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
