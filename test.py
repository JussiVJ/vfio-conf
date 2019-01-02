import subprocess

lspci = subprocess.check_output(["lspci", "-nn"])
ListPci = str(lspci).split("\\n")
del ListPci[0]
del ListPci[len(ListPci) - 1]

ListPciRev = []
for item in ListPci:
    item = item.replace(')', '(')
    item = item.split("(")
    del item[0]
    del item[1]
    ListPciRev.extend(item)
print(ListPciRev)
