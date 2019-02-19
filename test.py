import fileinput
distro = 0
#Debian:0 Redhat:1 Arch:2
if self.CheckVfio.get_active() == False:
    if distro == 2:
        for line in fileinput.FileInput("testfileinitcpio",inplace=1):
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
    elif distro == 0:
        for line in fileinput.FileInput("testfilemodload", inplace=1):
            if "vfio" in line:
                if "vfio_pci" in line:
                    self.vfio_already_enabled(self.ButtonVfioEnable)
                else:
                    line = line.replace('#vfio', 'vfio_pci vfio vfio_iommu_type1 vfio_virqfd')
            print(line, end="")
                    self.vfio_enabled(self.ButtonVfioEnable)
        if self.genrtoggle == 0:
            self.invalid_mkinitcpio_conf(self.ButtonVfioEnable)
