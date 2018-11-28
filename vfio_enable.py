import fileinput
triggerword = 'keyboard'
grub_config = '/etc/mkinitcpio.conf'
for line in fileinput.FileInput(grub_config,inplace=3):
    if triggerword in line:
        line = line.rstrip()
        line = line.replace(triggerword,triggerword+' vfio_pci vfio vfio_iommu_type1 vfio_virqfd')
    print(line, end=" ")
