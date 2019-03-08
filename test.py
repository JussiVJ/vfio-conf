import fileinput
import subprocess

pci_ids = {}
vfio_int = False

if "IOMMU enabled" not in str(subprocess.check_output(['sh', 'resources/IOMMU-check.sh'])):
    IOMMUSTATE = False
    lspci = subprocess.check_output(["lspci", "-nn"])
    ListPci = str(lspci).split("\\n")
    del ListPci[0]
    del ListPci[len(ListPci) - 1]

    #Filter out the Domain and Bus IDs
    ListPciDomain = []
    for item in ListPci:
        item = item.split(" ")
        ListPciDomain.append(item[0])

    #Filter out the names of the PCI-devices
    ListPciName = []
    for item in ListPci:
        itemlist = item.split(" ")
        del(itemlist[0])
        item = ' '.join(itemlist)
        item = item.replace(":", " [")
        itemlist = item.split(" [")
        ListPciName.append(str(itemlist[0] + ":" + itemlist[2]))

    #Filter out the IDs of the PCI-derrortoggle == 0evices
    ListPciIDs = []
    for item in ListPci:
        item = item.replace('[', ']')
        item = item.split("]")
        while ":" not in item[0] or len(item[0]) != 9:
            del item[0]
        while len(item) > 1:
            del item[1]
        ListPciIDs.extend(item)
        pci_ids[item[0]] = False

    #Filter out the revisons of the PCI-devices
    ListPciRev = []
    for item in ListPci:
        item = item.replace(')', '(')
        item = item.split("(")
        del item[0]
        if len(item) > 0:
            del item[1]
        else:
            item = ['N/A']
        ListPciRev.extend(item)


    if vfio_int == False:
        for line in fileinput.FileInput("testfilemodprobe", inplace=1):
            if "options vfio-pci" in line:
                linetemp = line.replace('\n', "")
                linelist = linetemp.split("=")
                linelist = linelist[1].split(",")
                for item in linelist:
                    pci_ids[item] = True
            print(line,end="")
    else:
        vfio_linelist = []
        for line in fileinput.FileInput("testfilegrub", inplace=1):
            if "vfio" in line:
                vfio_linelist = line.split('"')
                for item in vfio_linelist:
                    if "vfio" in item:
                        vfio_linelist = item.split(' ')
                        for item in vfio_linelist:
                            if "vfio" in item:
                                vfio_linelist = item.split("=")
                                vfio_linelist = vfio_linelist[1].split(',')
            print(line,end="")
        for item in vfio_linelist:
            pci_ids[item] = True

    #Put the filtered data into one list
    PciView = [[ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0], pci_ids[ListPciIDs[0]]],
                [ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1], pci_ids[ListPciIDs[1]]]]

    while len(PciView) < len(ListPci):
        if len(PciView) <= len(ListPci):
            PciView.append("")
        PciView[len(PciView)-1] = [ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1], pci_ids[ListPciIDs[len(PciView)-1]]]

    for item in PciView:
        if "PCI bridge" in item[0] or "Host bridge" in item[0]:
            print(item[0])
            del item

else:
    IOMMUSTATE = True
    lspci = subprocess.check_output(["sh", "resources/IOMMU-group.sh"])
    ListPci = str(lspci).split("\\n")
    ListPci[0] = ListPci[0].replace("b'", "")
    del ListPci[len(ListPci) - 1]

    ListPci = str(subprocess.check_output(["sh", "resources/IOMMU-group.sh"])).split("\\n")
    ListPci[0] = ListPci[0].replace("b'", "")
    del ListPci[len(ListPci) - 1]

    #Filter out the IOMMU group
    ListPciIOMMU = []
    for item in ListPci:
        item = item.split(" ")
        ListPciIOMMU.append(item[2])

    #Filter out the Domain and Bus IDs
    ListPciDomain = []
    for item in ListPci:
        item = item.split(" ")
        ListPciDomain.append(item[3])

    #Filter out the names of the PCI-devices
    ListPciName = []
    for item in ListPci:
        itemlist = item.split(" ")
        del(itemlist[0])
        item = ' '.join(itemlist)
        item = item.replace(":", " [")
        itemlist = item.split(" [")
        item = ''.join(itemlist[1]) + ":" + ''.join(itemlist[3])
        itemlist = item.split(" ")
        del(itemlist[0])
        ListPciName.append(' '.join(itemlist))

    #Filter out the IDs of the PCI-derrortoggle == 0evices
    ListPciIDs = []
    for item in ListPci:
        item = item.replace('[', ']')
        item = item.split("]")
        while ":" not in item[0] or len(item[0]) != 9:
            del item[0]
        while len(item) > 1:
            del item[1]
        ListPciIDs.append(item[0])
        pci_ids[item[0]] = False

    #Filter out the revisons of the PCI-devices
    ListPciRev = []
    for item in ListPci:
        item = item.replace(')', '(')
        item = item.split("(")
        del item[0]
        if len(item) > 0:
            del item[1]
        else:
            item = ['N/A']
        ListPciRev.extend(item)

    if vfio_int == False:
        for line in fileinput.FileInput("testfilemodprobe", inplace=1):
            if "options vfio-pci" in line:
                linetemp = line.replace('\n', "")
                linelist = linetemp.split("=")
                linelist = linelist[1].split(",")
                for item in linelist:
                    pci_ids[item] = True
            print(line,end="")
    else:
        for line in fileinput.FileInput("testfilegrub", inplace=1):
            if "vfio" in line:
                vfio_linelist = line.split('"')
                for item in vfio_linelist:
                    if "vfio" in item:
                        vfio_linelist = item.split(' ')
                        for item in vfio_linelist:
                            if "vfio" in item:
                                vfio_linelist = item.split("=")
                                vfio_linelist = vfio_linelist[1].split(',')
            print(line,end="")
        for item in vfio_linelist:
            pci_ids[item] = True

    #Put the filtered data into one list
    PciView = [[ListPciIOMMU[0], ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0], pci_ids[ListPciIDs[0]]],
                [ListPciIOMMU[1], ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1], pci_ids[ListPciIDs[1]]]]

    while len(PciView) < len(ListPci):
        if len(PciView) <= len(ListPci):
            PciView.append("")
        PciView[len(PciView)-1] = [ListPciIOMMU[len(PciView)-1], ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1], pci_ids[ListPciIDs[len(PciView)-1]]]

    for item in PciView:
        if "PCI bridge" in item[1] or "Host bridge" in item[1]:
            print(item[1])
            del item

print(PciView)
print(IOMMUSTATE)
