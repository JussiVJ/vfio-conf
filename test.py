import subprocess
import fileinput
testfile = '/home/jussi/koodit/vfio-conf/testfile'
for line in fileinput.FileInput(testfile,inplace=1):
    if ' \n ' in line:
        line = line.replace('\n',' xdlsd ')
    print(line, end=" ")
