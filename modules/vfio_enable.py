import fileinput
word = 'keyboard'
mkinitcpio_config = '/etc/mkinitcpio.conf'
for line in fileinput.FileInput(mkinitcpio_config,inplace=1):
    if 'vfio' in line:
        print(line, end=" ")
    else:
        if word in line:
            line = line.replace(word,word+' vfio_pci vfio vfio_iommu_type1 vfio_virqfd')
        print(line, end=" ")
