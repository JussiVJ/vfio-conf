import gi
import fileinput
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Pango, Gdk

files = str(subprocess.check_output(['ls', '/etc/modprobe.d/']))
files = files.replace("b'", '')
fileslist = files.split('\\n')
del fileslist[len(fileslist) - 1]
print(fileslist)
if
