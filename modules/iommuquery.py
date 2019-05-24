import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk

result = None

def ask():
    global result
    main = MainWindow()
    main.connect("destroy", Gtk.main_quit)
    main.show_all()
    Gtk.main()
    return result
    Gtk.main_quit()
    
class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Is IOMMU enabled?")

        BoxMain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(BoxMain)
        BoxMain.set_size_request(100, 20)

        label = Gtk.Label("Vfio-conf couldn't read IOMMU state from dmesg or grub config." + '\n' + "Is IOMMU enabled?")
        BoxMain.add(label)

        ButtonYes = Gtk.Button.new_with_label("Yes")
        ButtonYes.connect("clicked", self.yes)
        BoxMain.add(ButtonYes)

        ButtonNo = Gtk.Button.new_with_label("No")
        ButtonNo.connect("clicked", self.no)
        BoxMain.add(ButtonNo)

    def yes(self, ButtonYes):
        global result
        result = True
        Gtk.main_quit()

    def no(self, ButtonNo):
        global result
        result = False
        Gtk.main_quit()
