# =========================================================================
#                               ERD 320 PC APPLICATION
# =========================================================================
# GUI Code Edited by    V.T.    Dube        13221796
#
#
import sys
import time
import serial
import serial.tools.list_ports
from PyQt4 import QtCore, QtGui, uic, Qwt5
from PyQt4.QtGui import *

# qtCreatorFile = "main.ui" # Enter file here.
#
# Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
# class MainWindow(QMainWindow, Ui_MainWindow):
#
#     def __init__(self, Hidden=False):
#         super(MainWindow, self).__init__()
#         Ui_MainWindow.__init__(self)
#         self.setupUi(self)


def hexPrint(str):
    for c in str:
        print "%X "%int(c)

choice_port = []
ports = []
device = None
for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
    print portname
    print desc
    print hwid
    print hwid[4:21]
    if (hwid[4:21] == "VID:PID=067B:2303") and ("55" in portname):
        device = portname

print portname, device
ser = serial.Serial(
        port=device,
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )
print ser
print ser.isOpen()
input= 1
out = ""







while 1 :
    # get keyboard input
    input = raw_input( ">> ")
    if "ATR" in input:
        while ser.inWaiting() > 0:
            out += ser.read(1)
        print [hex(ord(u)) for u in out]
        print out
    elif "" in input:
        pass

    out = ""

out = "hello"

