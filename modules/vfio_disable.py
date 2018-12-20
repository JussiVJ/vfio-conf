import fileinput
mkinitcpio_config = '/etc/mkinitcpio.conf'
for line in fileinput.FileInput(mkinitcpio_config,inplace=1):
    if 'vfio' in line:
        line = line.replace(' vfio_pci vfio vfio_iommu_type1 vfio_virqfd', '')
    print(line, end=" ")
