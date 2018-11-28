import fileinput
grub_config = '/etc/mkinitcpio.conf'
for line in fileinput.FileInput(grub_config,inplace=3):
    if 'vfio' in line:
        line = line.rstrip()
        line = line.replace(' vfio_pci vfio vfio_iommu_type1 vfio_virqfd', '')
    print(line, end=" ")
