def disable():
    if CheckVfio.get_active() == False:
        for line in fileinput.FileInput("testfiles/testfileinitcpio",inplace=1):
            if "HOOKS=" in line:
                errortoggle = 1
                if 'vfio' in line:
                    line = line.replace(" vfio_pci vfio vfio_iommu_type1 vfio_virqfd", "")
                    genrtoggle = 1
            print(line, end="")
        if errortoggle == 0:
            return "invalid_mkinitcpio_conf"
        elif genrtoggle == 0:
            return "vfio_not_enabled"
        else:
            return "vfio_disabled"


def enable():
    print("vfio enabled on arch")
