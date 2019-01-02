import subprocess

#Get PCI data
lspci = subprocess.check_output(["lspci", "-nn"])
ListPci = str(lspci).split("\\n")
del ListPci[0]
del ListPci[len(ListPci) - 1]

#Filter out the Domain and Bus IDs
ListPciDomain = []
for item in ListPci:
    item = item.split(" ")
    while len(item) > 1:
        del item[1]
    ListPciDomain.extend(item)

#Filter out the names of the PCI-devices
ListPciName = []
for item in ListPci:
    item = item.replace(": ", " [")
    item = str(item).split(" [")
    del item[0]
    del item[0]
    while len(item) > 1:
        del item[1]
    ListPciName.extend(item)

#Filter out the IDs of the PCI-devices
ListPciIDs = []
for item in ListPci:
    item = item.replace('[', ']')
    item = item.split("]")
    while ":" not in item[0] or len(item[0]) != 9:
        del item[0]
    while len(item) > 1:
        del item[1]
    ListPciIDs.extend(item)

#Filter out the revisons of the PCI-devices
ListPciRev = []
for item in ListPci:
    item = item.replace(')', '(')
    item = item.split("(")
    del item[0]
    del item[1]
    ListPciRev.extend(item)

#Put the filtered data into a ListStore
PciView = [[ListPciName[0], ListPciIDs[0], ListPciDomain[0], ListPciRev[0]],
            [ListPciName[1], ListPciIDs[1], ListPciDomain[1], ListPciRev[1]]]


while len(PciView) < len(ListPci):
    if len(PciView) <= len(ListPci):
        PciView.append("")
    PciView[len(PciView)-1] = [ListPciName[len(PciView)-1], ListPciIDs[len(PciView)-1], ListPciDomain[len(PciView)-1], ListPciRev[len(PciView)-1]]
print(PciView)
