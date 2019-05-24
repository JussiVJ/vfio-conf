import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk
def vfio_updated(self, widget, data=None):
    dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK, "Devices updated!")
    dialog.format_secondary_text(
        "Vfio is now enabled and devices updated")
    dialog.run()

    dialog.destroy()

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
