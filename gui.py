import gi
import vfio_enable
gi.require_version('Gtk', '3.0')
gi.require_version('XApp', '1.0')
from gi.repository import Gio, Gtk, Pango, Gdk, XApp

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Vfio-conf")




main = MainWindow()
main.connect("destroy", Gtk.main_quit)
main.show_all()
Gtk.main()
