import fileinput

word = 'GRUB_CMDLINE_LINUX_DEFAULT="'
grub_config = '/etc/default/grub'
for line in fileinput.FileInput(grub_config, inplace=1):
    if 'iommu=on' in line:
        print(line,end=" ")
    else:
        if word in line:
            line = line.replace(word,word+'intel_iommu=on amd_iommu=on iommu=on iommu=pt ')
        print(line,end=" ")
