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

        CheckVfio = Gtk.CheckButton("Vfio is compiled in")
        CheckVfio.connect("toggled", self.vfio_integrated_checked)
        BoxBasic.add(CheckVfio)

        PanedBasic = Gtk.HPaned()
        BoxBasic.add(PanedBasic)

        ButtonVfioEnable = Gtk.Button.new_with_label("Enable Vfio")
        ButtonVfioEnable.connect("clicked", self.enable_vfio)
        PanedBasic.add(ButtonVfioEnable)

        ButtonVfioDisable = Gtk.Button.new_with_label("Disable Vfio")
        ButtonVfioDisable.connect("clicked", self.disable_vfio)
        PanedBasic.add(ButtonVfioDisable)

        ButtonEnableIommu = Gtk.Button.new_with_label("Enable Iommu")
        ButtonEnableIommu.connect("clicked", self.enable_iommu)
        PanedBasic.add(ButtonEnableIommu)

    def vfio_integrated_checked(self, CheckVfio):
        vfio_integrated = CheckKey.get_active()

    def disable_vfio(self, ButtonVfioDisable):
        mkinitcpio_config = '/etc/mkinitcpio.conf'
        for line in fileinput.FileInput(mkinitcpio_config,inplace=1):
            if 'vfio' in line:
                line = line.replace(' vfio_pci vfio vfio_iommu_type1 vfio_virqfd', '')
            print(line, end=" ")

    def enable_vfio(self, ButtonVfioEnable):
        word = 'keyboard'
        mkinitcpio_config = '/etc/mkinitcpio.conf'
        for line in fileinput.FileInput(mkinitcpio_config,inplace=1):
            if 'vfio' in line:
                print(line, end=" ")
            else:
                if word in line:
                    line = line.replace(word,word+' vfio_pci vfio vfio_iommu_type1 vfio_virqfd')
                print(line, end=" ")

    def disable_iommu(self, ButtonDisableIommu):
        word = 'intel_iommu=on amd_iommu=on iommu=on iommu=pt '
        grub_config = '/etc/default/grub'
        for line in fileinput.FileInput(grub_config, inplace=1):
            if word in line:
                line = line.replace(word,'')
            print(line,end=" ")

    def enable_iommu(self, ButtonEnableIommu):
        word = 'GRUB_CMDLINE_LINUX_DEFAULT="'
        grub_config = '/etc/default/grub'
        for line in fileinput.FileInput(grub_config, inplace=1):
            if 'iommu=on' in line:
                print(line,end=" ")
            else:
                if word in line:
                    line = line.replace(word,word+'intel_iommu=on amd_iommu=on iommu=on iommu=pt ')
                    print(line,end=" ")


main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
