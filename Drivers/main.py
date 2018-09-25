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
        print "%X " % int(c)

choice_port = []
ports = []
device = None
portname = None
for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
    print portname
    print desc
    print hwid
    print hwid[4:21]
    if (hwid[4:21] == "VID:PID=067B:2303") and ("55" in portname):
        device = portname

device = "COM63"
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

input = 1
out = ""

def TX1(Y0, B):
    Fi, Di = B'0000', B"0000"  # TA1 
    i1, Pi1 = 0, 0  # TB1
    N = 0  # TC1
    Y1, T = 0, 0  # TD1
    if Y0 & 0x01:
        TA1 = B.pop(0)
        Fi = (TA1 & 0XF0) >> 4 
        Di = (TA1 & 0X0F)
        print "TA1=%0X:\t\tFi=%X\tDi=%0X" % (TA1, Fi, Di)
    if Y0 & 0x02:
        TB1 = B.pop(0)
        i1 = (TB1 & 0XC0) >> 4 
        Pi1 = (TB1 & 0X3F)
        print "TB1=%0X:\t\ti1=%X\tPi1=%0X" % (TB1, i1, Pi1)
    if Y0 & 0x04:
        TC1 = B.pop(0)
        N = TC1 & 0xFF
        print "TC1=%0X:\t\tN=%d" % (TC1, N)
    if Y0 & 0x08:
        TD1 = B.pop(0)
        Y1 = (TD1 & 0xF0) >> 4
        T = TD1 & 0x0F
        print "TD1=%0X:\t\tY1=%0X" % (TD1, Y1, T)
    return Fi, Di, i1, Pi1, Y1, T

CatogoryStrings = { 0x00: 'A status indicator shall be present as the last three historical bytes (see 8.1.1.3)',
                    0x10: 'See 8.1.1.4',
                    0x80: 'A status indicator may be present in a COMPACT-TLV data object (one, two or three bytes, see 8.1.1.3)',
                    0x81: "to '8F' Reserved for future use"}

def HistoricalBytes(B):
    print "Historical Bytes"
    CATEGORY = B.pop(0)
    print "Category=%0X:\t\t%s" % (CATEGORY, CatogoryStrings[CATEGORY])
    
    
    return 0

def ATR(B):
    """
    bytes: list
    """
    TS = B.pop(0)
    if TS == 0x3B:
        print "TS=%0X:\t\tDirect mode" % TS
    elif TS == 0x3F:
        print "TS=%0X:\t\tInverse Mode" % TS
    else:
        print "TS=%0X:\t\tInvalid Mode Parameter" % TS
        return 
    T0 = B.pop(0)
    K = T0 & 0xF
    Y0 = (T0 & 0xF0) >> 4
    
    print "T0=%0X:\t\t[%s,%s]" % (T0, bin(Y0), bin(K))
    for i in range(4):
        if (Y0 >> i) & 0x01 == 1:
            print "\t\tT%c1 is present" % (0x41 + i)
        else:
            print "\t\tT%c1 is absent" % (0x41 + i)
    print "  K=%d\t\tThere are %d Historical Bytes" % (K, K)
    Fi, Di, Vpp, N, Y1, T = TX1(Y0, B)
    print """Parameters Part 1
    Fi = %s\tFrequency is MHz
    Di = %s\t
    Vpp= %s\tProgramming Voltage is
    N  = %d\tGaurd Time is
    T  = %d\tProtocal is
    Y1 = %0X\t""" % (Fi, Di, Vpp, N, T , Y1)
    for i in range(4):
        if (Y1 >> i) & 0x01 == 1:
            print "\t\tT%c2 is present" % (0x41 + i)
        else:
            print "\t\tT%c2 is absent" % (0x41 + i)
    
    return 0
# The PSE Way...
EMV_SELECT_PSE = [0x00, 0xA4 , 0x04 , 0x00 , 0x0E , 0x31 , 0x50 , 0x41 , 0x59 , 0x2E , 0x53 , 0x59 , 0x53 , 0x2E , 0x44 , 0x44 , 0x46 , 0x30 , 0x31 , 0x00]
    

if  False:
    while 1 :
        # get keyboard input
        input = raw_input(">> ")
        if "ATR" in input:
            while ser.inWaiting() > 0 :
                out += ser.read(1)
            convert = [hex(ord(u)) for u in out]
            print convert
            print out
            if len(out) > 20:
                ATR(convert)
        elif "PTS" in input:
            ser.write([0xFF, 0x10, 0x11, 0xFE])
            # ser.write("HelloWorld\0")
            # ser.write(0x10)
            # ser.write(0x11)
            # ser.write(0xFE)
    
        out = ""
else:
    ATR_DUMMY = [0x3b, 0x6e, 0x00, 0x00, 0x80, 0x31,
                 0x80, 0x66, 0xb0, 0x84, 0x0c, 0x01,
                 0x6e, 0x01 , 0x83 , 0x00 , 0x90 , 0x00]
    print "Writing ", EMV_SELECT_PSE
    i = 0
    j = 0
    while(j < len(EMV_SELECT_PSE)):
        while(i < 50000):
            i += 1
        
        ser.write([EMV_SELECT_PSE[j % len(EMV_SELECT_PSE)]])  # EMV_SELECT_PSE)
        j += 1
        i = 0
        print "P", EMV_SELECT_PSE[j % len(EMV_SELECT_PSE)], "%c"%EMV_SELECT_PSE[j % len(EMV_SELECT_PSE)]
    print "Done     "
    # ATR(ATR_DUMMY)
    # HistoricalBytes(ATR_DUMMY)


out = "hello"

