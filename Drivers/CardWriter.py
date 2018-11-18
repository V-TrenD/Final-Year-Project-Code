'''
    @author: Vussy Dube
'''
import socket
import os
import sqlite3
import sys
from threading import Thread
import time
import math

from PyQt4 import QtCore, QtGui, uic, Qwt5, Qt
from PyQt4.QtGui import *
import serial
import serial.tools.list_ports
from PyQt4.Qt import QObject

Ui_CardWriter, QtBaseClass = uic.loadUiType('cardWriter.ui')

CMD_ROOT = 0x00
CMD_CARD_WRITE = 'W'

class CardWriter(QDialog, Ui_CardWriter):
    '''
    
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(CardWriter, self).__init__(parent)
        self.setWindowTitle("Card Writer")
        self.setupUi(self)
        self.s = serial.Serial(
            port='COM72',
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        self.savingsvalue = None
        self.chequevalue = None
        self.creditvalue = None
        self.tokenvalue = None
        self.save.pressed.connect(self.saveUP_PAYValues)
        
    
    def saveUP_PAYValues(self):
        cardID = 'UPBANK\0\0'+str(self.cardID.text())
        UP_APPID = [0xA1, 0x9A, 0x70, 0x86, 0xD4, 0x0F, 0x05, 0x45, 0xD8, 0xA1, 0x9D, 0xC9, 0x57, 0x69, 0xA0, 0xF8]
        if self.UP_PAY.isChecked():
            self.paypin = self.uppay_pin.text()
            if self.paysavings.isChecked():
                print "Checked"
                self.savingsvalue = float(self.paysavingsvalue.value())
            if self.paycheque.isChecked():
                self.chequevalue = float(self.paychequevalue.value())
            if self.paycredit.isChecked():
                self.creditvalue = float(self.paycreditvalue.value())
            if self.paytokens.isChecked():
                self.tokenvalue = float(self.paytokensvalue.value())
            print self.savingsvalue, self.paysavings.isChecked()
            
            print type(self.savingsvalue)
            WriteData = UP_APPID + \
                list(float_to_hex(self.savingsvalue))+ \
                list(float_to_hex(self.chequevalue))+ \
                list(float_to_hex(self.creditvalue))+ \
                list(float_to_hex(self.tokenvalue))
            print WriteData
            self.appSectionWrite(0x20, WriteData)
            
    def appSectionWrite(self, section, data):
        while True:
            print "Write Root"
            self.s.write([CMD_ROOT])
            flag = self.s.readline()
            print flag
            if "Reader>" in flag:
                print "Found Root"
                break
        print "Break Received"
        self.s.write([CMD_CARD_WRITE])# write command
        flag = self.s.readline()
        print flag
        print "TAG:", CMD_CARD_WRITE
        self.s.write(section)
        print "VALUE:",section
        self.s.write("%d"%len(data))   # write length
        print "Length:",len(data)
        self.s.write(data)
        print "Wrote", data
        
  
def main():
    """
    This is the main application code
    It runs everything in the main loop
    """
    app = QtGui.QApplication(sys.argv)
    window = CardWriter()
    window.show()
    window.saveUP_PAYValues()
    sys.exit(app.exec_())
    return 0

def float_to_hex(f):
    print "FF",f
    if f == None:
        return [0xff, 0xff, 0xff, 0xff]
    return bytearray(struct.pack("f", f))  
    
import struct
import string 
  

if __name__ == "__main__":
    value = 86858385778590.73*.75*.1 #example value
    value = float_to_hex(value)
    print([ "0x%02x" % b for b in value ])
    value =  struct.unpack('f',value)
    print value
    main()
    
