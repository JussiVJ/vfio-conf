import fileinput

word = 'intel_iommu=on amd_iommu=on iommu=on iommu=pt '
grub_config = '/etc/default/grub'
for line in fileinput.FileInput(grub_config, inplace=1):
    if word in line:
        line = line.replace(word,'')
    print(line,end=" ")
