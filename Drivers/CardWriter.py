'''
    @author: Vussy Dube
'''
import hashlib
import math
import os
import socket
import sqlite3
import struct
import sys
from threading import Thread
import time
from matplotlib import pyplot as plt
from PyQt4 import QtCore, QtGui, uic, Qwt5, Qt
from PyQt4.Qt import QObject, QCheckBox
from PyQt4.QtGui import *
from cdecimal import Decimal
import serial
import serial.tools.list_ports

from Databases import ACCOUNTDATABASE


Ui_CardWriter, QtBaseClass = uic.loadUiType('cardWriter.ui')

CMD_ROOT = 0x00
CMD_CARD_WRITE = 'W'

app_id_card_rage = [ 0x3B, 0xDC, 0x00, 0x58,
                     0x40, 0x4F, 0x23, 0x70, 
                     0xDE, 0xCA, 0xBA, 0x2D, 
                     0xF0, 0x3E, 0x99, 0x3C]
app_id_card_love = [0xFE, 0xF7, 0xA9, 0xC0, 0x13, 0xF2, 0x0E, 0xB3, 0xD2, 0x44, 0xCC, 0x3F, 0x8A, 0xD7, 0x2D, 0x25]
app_id_card_hate = [0xC0, 0x38, 0xA9, 0xCB, 0x19, 0xC6, 0x0C, 0x30, 0xE5, 0xD4, 0x64, 0xDA, 0xA4, 0x8A, 0x55, 0x8B]
app_id_card_time = [0x39, 0x59, 0xB1, 0x10, 0xFB, 0x07, 0x33, 0x3E, 0x60, 0xA6, 0xAF, 0xA0, 0x04, 0x74, 0xC3, 0xBA]
app_id_card_fear = [0xB3, 0xDE, 0xAA, 0x64, 0x39, 0x35, 0xC4, 0xAE, 0xB2, 0x85, 0xB7, 0x8D, 0x1C, 0xE6, 0x42, 0xBE]


def plot(bitR, mean):
    plt.plot(bitR, 'o', color='g')
    plt.title("Card Reader Read Speed, AVG=%dkbps"%(mean/1000))
    plt.ylabel("Read Speed (bps)")
    plt.xlabel("Sample")
    #plt.ylim([0, 7e5])
    plt.plot([0,99], [mean, mean], 'r-')
    plt.show()

class Card(QObject):
    
    def __init__(self, data=None):
        super(Card, self).__init__(None)
        if data is None:
            data = [0xFF]*256
        self.data = data
        
        
    def __len__(self):
        return 256
    
    def get_card_id(self):
        """Gets A string Representation Of the cards ID
        """
        return str(bytearray(self['CardID']))
    
    def __getitem__(self, item):
        if type(item) is slice:
            return self.data[item]
        if type(item) is int:
            return self.data[item] 
        if item is "ATR":
            return self.data[0:4]
        elif item is "ManID":
            return self.data[4:8]
        elif item is "CardID":
            return self.data[8:0x14]
        elif item is "App1":
            return self.data[0x20:0x40]
        elif item is "App2":
            return self.data[0x40:0x60]
        elif item is "App3":
            return self.data[0x60:0x80]
        elif item is "App4":
            return self.data[0x80:0xA0]
        elif item is "App5":
            return self.data[0xA0:0xC0]
        elif item is "App6":
            return self.data[0xC0:0xE0]
        elif item is "Pins":
            return self.data[0xE0:0x100]
        
        
    def set_card_id(self, cardID):
        self['CardID'] = cardID
        return self['CardID']
        
    def __setitem__(self, item, data):
        if type(item) is slice:
            self.data[item] = data
        if type(item) is int:
            self.data[item] = data
        if type(data) is str:
            data = [ord(x) for x in data]
        if item is "ATR":
            self.data[0:4] = data
        elif item is "ManID":
            self.data[4:8] = data
        elif item is "CardID":
            self.data[8:0x14] = data
        elif item is "App1":
            self.data[0x20:0x40] = data
        elif item is "App2":
            self.data[0x40:0x60] = data
        elif item is "App3":
            self.data[0x60:0x80] = data
        elif item is "App4":
            self.data[0x80:0xA0] = data
        elif item is "App5":
            self.data[0xA0:0xC0] = data
        elif item is "App6":
            self.data[0xC0:0xE0] = data
        elif item is "Pins":
            self.data[0xE0:0x100] = data
        return self.__getitem__(item)
    
    
        
    def getkeys(self):
        return ["ATR","ManID","CardID","App1","App2","App3","App4","App5","App6","Pins"]
        
    def __repr__(self, *args, **kwargs):
        
        return """Card Summary
%s
ATR>\t%s
ManID>\t%s
CardID>\t%s
App1>\t%s
App2>\t%s
App3>\t%s
App4>\t%s
App5>\t%s
App6>\t%s
Pins>\t%s"""%tuple([bytearray(self.data)]+[as_hex_str_list(self.__getitem__(x)) for x in self.getkeys()])

    _ATR = property(None, None,None, None)
    _ManID = _ATR = property(None, None,None, None)
    _cardID =  property(get_card_id, set_card_id, None, "The ID for the given card") 
    
def as_hex_str_list(data):
    if 'U' not in data:
        return ["%02X"%d for d in data]
    return data
    
        

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
        self.s = None
        self.savingsvalue = float('nan')
        self.chequevalue = float('nan')
        self.creditvalue = float('nan')
        self.tokenvalue = float('nan')
        self.save.pressed.connect(self.storeTOCSV)
        self.save.pressed.connect(self.saveSpeed)
        self.load.pressed.connect(self.readCardIn)
        self.loadspeed.pressed.connect(self.readSpeed)
        self.unlock.pressed.connect(self.unlockCard)
        self.reset.pressed.connect(self.resetCard)
        self.off.clicked.connect(self.setChangeCardClass)
        self.classA.clicked.connect(self.setChangeCardClass)
        self.classB.clicked.connect(self.setChangeCardClass)
        self.readerlink.pressed.connect(self.readerConnect)
        self.readerunlink.pressed.connect(self.readerDisconnect)
        self.pinbutton.pressed.connect(self.getPIN)
        self.STORE.pressed.connect(self.saveToDatabase)
        
        
        
        
    def str_to_list(self, data):
        return [ord(c) for c in data]
    
    def list_to_str(self, data):
        result = ""
        for s in data:
            result += str(s)
        return result
    
    def saveCard(self):
        c = Card()
        c["ATR"] = [0xA2, 0x13,0x10, 0x91]
        c["ManID"] = [0xFF, 0xFF, 0x81, 0x15]
        c["CardID"] = "UPBANK\0\0"+str(self.cardID.text())
        ######
        # UP Pay Section
        c['App1'] = self.getUP_PAY(app_id_card_rage)
        # APP 2
        c['App2'] = [0xFF]* 32
        # APP 3
        c['App3'] = [0xFF]* 32
        # APP 4
        c['App4'] = [0xFF]* 32
        # APP 5
        c['App5'] = [0xFF]* 32
        # APP 6
        c['App6'] = [0xFF]* 32
        # Security
        c['PINS'] = [0xFF]*32#eval('0x'+str(self.uppay_pin.text()))+[0xFF]*29
        return c
        
    def storeTOCSV(self):
        print "Saving CSV"
        CARD = self.saveCard()
        print len(CARD)
        print CARD
        for b in range(len(CARD)):
            if b % 16 == 0 :
                print "\n%0X\t"%(b/16),
            print "0x%02X"%CARD[b],
        print ''
        self.flashCARD(CARD)
        #self.readSpeed()
        #self.LCD_write(0, 0, "Hello World\nThis is a Message");
        #self.saveToDatabase()
        
    def getSerial(self):
        if self.s is None:
            self.s = serial.Serial(
                port='COM72',
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
        return self.s
    
    def getPIN(self):
        self.LCD_clear()
        self.LCD_write(0, 0, "Please Enter PIN")
        self.LCD_write(0, 4, "A:Abort  B:Back")
        self.LCD_write(0, 5, "C:Cancel D:Done")
        pin = []
        while True:
            keyPress = self.getKeyPress()
            if keyPress == 0xD or keyPress == 0xA:
                break
            elif keyPress == 0xB and len(pin) > 0:
                pin.pop()
            else:
                pin.append(keyPress)
            self.LCD_write(0,2, " "*(len(pin)+1))
            self.LCD_write(0,2, "*"*len(pin))
            print pin
        print "Entered pin is", pin
        self.LCD_clear()
        
        
    def getKeyPress(self):
        self.getSerial()
        self.break_root()
        self.s.write(['K'])
        print "KEYPAD", self.readline()
        pressed = ord(self.s.read(1))
        print "Pressed %X"%pressed
        return pressed
        
    def LCD_clear(self):
        self.getSerial()
        self.break_root()
        self.s.write(['!'])
        print "CLEAR", self.readline()
        
        
    def LCD_write(self, x,y,message):
        self.getSerial()
        self.break_root()
        self.s.write(['P'])
        print "Print",x, y, len(message),self.readline()
        self.s.write([x, y, len(message)])
        print "Printing",self.readline()
        self.s.write(message)
        self.break_root()
        
    def setChangeCardClass(self):
        self.value = -1
        if self.off.isChecked():
            self.value = 0
            self.setCardClass('0')
            print "setChangeCardClass", value
        elif self.classA.isChecked():
            self.value = 1
            self.setCardClass('3')
            print "setChangeCardClass", value
        elif self.classB.isChecked():
            self.value = 2
            self.setCardClass('5')
            print "setChangeCardClass", value
        
        
    def setCardClass(self, ccc):
        self.break_root()
        self.s.write(['C'])# Card Voltage command
        b = self.s.read(1)
        while b != 'V':
            b = self.s.read(1)
            print b
        self.s.write(ccc)
        print "Set to 5V"
        
    def resetCard(self):
        self.break_root()
        self.s.write(['#'])
        print 'ATR-',self.readline()   # MUST BE ATR
        atr = self.s.read(4)
        print 'ATR>',atr
        
    def unlockCard(self):
        unlocked = '!'
        maxTires = 21
        while unlocked != 'OK' and maxTires > 0:
            maxTires-= 1
            self.break_root()
            self.s.write(['A'])     # write Unlock String
            print "UNLOCK[%d]"%((20-maxTires)+1),self.readline(), 
            unlocked = self.readline()
            print unlocked
        
    def readCardIn(self):
        self.getSerial()
        self.setCardClass('5')
        self.resetCard()
        self.break_root()
        self.s.write('R')
        print 'FULL READ>',self.readline()   # MUST BE READCARD
        ALLDATA = self.s.read(256)
        print ALLDATA
        c = Card([ord(x) for x in ALLDATA])
        #c[0x30:0x33] = [0x00, 0x00, 0x7a, 0x43]
        print c
        self.cardID.setText(c.get_card_id()[-4:])
        values = self.unpackUPPAY(c['App1'])
        self.label_AppKey.setText(to_hex_str(c['App1'][0:0x10]))
        print values, math.isnan(values['SAVINGS']), math.isnan(float('nan'))
        self.paysavings.setChecked(not math.isnan(values['SAVINGS']))
        self.paysavingsvalue.setValue(values['SAVINGS'])
        self.paycheque.setChecked(not math.isnan(values['CHEQUE']))
        self.paychequevalue.setValue(values['CHEQUE'])
        self.paycredit.setChecked(not math.isnan(values['CREDIT']))
        self.paycreditvalue.setValue(values['CREDIT'])
        self.paytokens.setChecked(not math.isnan(values['TOKENS']))
        self.paytokensvalue.setValue(values['TOKENS'])
        #self.saveToDatabase()
        
    def readerConnect(self):
        self.getSerial()
            
    def readerDisconnect(self):
        if self.s is not None:
            self.s.close()
            self.s = None

    def saveSpeed(self):
        pass    
    
        
    def readSpeed(self):
        if self.s is None:
            self.s = serial.Serial(
                port='COM72',
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
        self.break_root()
        
        self.s.write(['C'])# Card Voltage command
        b = self.s.read(1)
        while b != 'V':
            b = self.s.read(1)
            print b
        self.s.write(['5'])
        print "Set to 5V"
        self.break_root()
        self.s.write(['#'])
        print 'ATR-',self.readline()   # MUST BE ATR
        atr = self.s.read(4)
        print 'ATR>',atr
        
        times = []
        data = []
        counter = 100
        self.break_root()
        self.s.write(['X']) # X for card Read Speed, Y for interface read speed
        while counter > 0:
            start = time.time()
            #l = self.s.read(255)   # MUST BE READCARD
            l = self.s.readline()
            times += [time.time() - start]
            # ALLDATA = self.s.read(256)
            data += [l]
            counter -= 1
        
        print times
        for d in data:
            print d
        total = 0
        bitR = []
        for t in times:
            datarate = 1.0/(t/((3+1)*256))
            print datarate, datarate*8
            total += datarate*8
            bitR.append(datarate*8)
        mean = sum(bitR)/len(bitR)
        print mean, "kbps"
        #savefile = file("ReadData-%dkpbs"%(total/10000), 'w')
        savefile = file("ReadCardX-%dkpbs"%(mean/1000), 'w')
        savefile.write(str(times)+"\n")
        for d in data:
            savefile.write(d)
        savefile.flush()
        savefile.close()
        
        plot(bitR, mean)
        
            
    def flashCARD(self, card_data):
        if self.s is None:
            self.s = serial.Serial(
                port='COM72',
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
        self.break_root()
        
        self.s.write(['C'])# Card Voltage command
        b = self.s.read(1)
        while b != 'V':
            b = self.s.read(1)
            print b
        self.s.write(['5'])
        print "Set to 5V"
        self.break_root()
        self.s.write(['#'])
        print 'ATR-',self.readline()   # MUST BE ATR
        atr = self.s.read(4)
        print 'ATR>',atr
        self.break_root()
        self.s.write(['R'])
        print 'FULL READ>',self.readline()   # MUST BE READCARD
        ALLDATA = self.s.read(256)
        print 'PAST>',ALLDATA
        print 'HEX>', self.str_to_list(ALLDATA)
        
        self.unlockCard()
        
        self.break_root()
        print "Writing Data"
        self.s.write(['w'])     # write write binary to card
        time.sleep(0.2)
        self.s.write([0x00, 250])
        time.sleep(0.2)
        self.s.write(card_data[0:250])
        self.break_root()
        print "Wrote Data"
        self.s.write(['R'])
        print 'FULL READ>',self.readline()   # MUST BE READCARD
        ALLDATA = self.s.read(256)
        print 'PAST>',ALLDATA
        print 'HEX>', self.str_to_list(ALLDATA)
        self.break_root()
        print "Wrote Data"
        self.s.write(['R'])
        print 'FULL READ>',self.readline()   # MUST BE READCARD
        ALLDATA = self.s.read(256)
        print 'PAST>',ALLDATA
        print 'HEX>', self.str_to_list(ALLDATA)
        
    def saveToDatabase(self):
        db = ACCOUNTDATABASE("type2.db")
        check = db.checkCard(eval(to_hex_str('UPBANK\0\0'+str(self.cardID.text()))))
        if check['ID'] is not None:
            print "Updating A cards Data"
            self.saveCard()
            db.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=%d"%check['ID'], (str({"UP_PAY":self.packUPPAY()}), ))
            db.db.commit()
        else:
            print "Adding A new Card"
            c = self.saveCard()
            m = hashlib.md5()
            m.update(str(bytearray(c['CardID'])))
            m.update("UP Pay")
            db.insert(ACCOUNTDATABASE.__table_name__,
              ACCOUNTDATABASE.__columns__[1:],
              (
                  #             1| Primary KEY            | INT*
                str(bytearray(c['CardID'])),  #                  2| PYSICAL CARD ID        | CHAR[12]*
                m.digest(),  # [-95, -102, 112, -122, -44, 15, 5, 69, -40, -95, -99, -55, 87, 105, -96, -8],  #           3| CARDAPPLICATION KEY    | CHAR[16]*
                "%d" % 0x76488651,  #          4| USERID                 | INT*
                str(self.holder.text()),  #     5| USER Name and Surname  | TEXT
                "%d" % 0,  #                   6| The Type of account    | INT
                "%f" % 0.0,  #   7| How Much is left in the| DECIMAL(10,2)
                "%f" % 0.0,  # 8| How much Can be used   | DECIMAL(10,2)
                str({"UP_PAY":self.packUPPAY()})  #    9| Other Info             | TEXT
        ))
        
        
    def readline(self):
        line = self.s.readline()
        #print len(line), ord(line)
        while line == '\n':
            #print line, len(line)
            line = self.s.readline()
        return line.replace('\n', '')
            
    def getUP_PAY(self, UP_APPID):
        if self.UP_PAY.isChecked():
            self.paypin = self.uppay_pin.text()
            self.savingsvalue = self.chequevalue =  self.creditvalue = self.tokenvalue = float('NaN')
            if self.paysavings.isChecked():
                self.savingsvalue = float(self.paysavingsvalue.value())
            if self.paycheque.isChecked():
                self.chequevalue = float(self.paychequevalue.value())
            if self.paycredit.isChecked():
                self.creditvalue = float(self.paycreditvalue.value())
            if self.paytokens.isChecked():
                self.tokenvalue = float(self.paytokensvalue.value())
            print self.savingsvalue, self.paysavings.isChecked()
            return UP_APPID + \
                list(float_to_hex(self.savingsvalue))+ \
                list(float_to_hex(self.chequevalue))+ \
                list(float_to_hex(self.creditvalue))+ \
                list(float_to_hex(self.tokenvalue))
        else:
            return [0xFF] * 32
        
    
    def saveUP_PAYValues(self):
        self.appSectionWrite(0x00, [0xA2, 0x13,0x10, 0x91, 0xFF, 0xFF, 0x81, 0x15])
        cardID = 'UPBANK\0\0R@G3'#+str(self.cardID.text())
        print cardID
        self.appSectionWrite(0x08, cardID)
        UP_APPID = app_id_card_rage#[0x3B, 0xDC, 0x00, 0x58, 0x40, 0x4F, 0x23, 0x70, 0xDE, 0xCA, 0xBA, 0x2D, 0xF0, 0x3E, 0x99, 0x3C]#[0xA1, 0x9A, 0x70, 0x86, 0xD4, 0x0F, 0x05, 0x45, 0xD8, 0xA1, 0x9D, 0xC9, 0x57, 0x69, 0xA0, 0xF8]
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
        #self.appSectionWrite(0x20, [0xff]*50)
        
    def packUPPAY(self):
        result = {}
        result['CHEQUE'] = float_to_hex_str(self.chequevalue)
        result['CREDIT'] = float_to_hex_str(self.creditvalue)
        result['SAVINGS'] = float_to_hex_str(self.savingsvalue)
        result['TOKENS'] = float_to_hex_str(self.tokenvalue)
        print result
        return result   
     
    def unpackUPPAY(self, bytes):
        result = {}
        self.savingsvalue= result['SAVINGS'] = hex_to_float(bytearray(bytes[0x10:0x14]))
        self.chequevalue = result['CHEQUE'] = hex_to_float(bytearray(bytes[0x14:0x18]))
        self.creditvalue = result['CREDIT'] = hex_to_float(bytearray(bytes[0x18:0x1C]))
        self.tokenvalue = result['TOKENS'] = hex_to_float(bytearray(bytes[0x1C:0x20]))
        return result
    
    def break_root(self):
        print "ROOT>",
        while True:
            print '.',
            self.s.write([CMD_ROOT])
            flag = self.s.readline()
            #print flag
            if "Reader>" in flag:
                #print "Found Root"
                break
        time.sleep(0.2)
        self.s.read_all()
        print "@"
            
    def appSectionWrite(self, section, data):
        self.break_root()
        self.s.write(['A'])# write command
        time.sleep(0.50)
        self.s.write([CMD_CARD_WRITE])# write command
        time.sleep(0.20)
        print "TAG:", CMD_CARD_WRITE,"got",self.s.readline()
        self.s.write("%d\r"%section)
        time.sleep(0.10)
        print "VALUE:",section,"got",self.s.readline()
        self.s.write("%d\r"%len(data))   # write length
        print "Length:",len(data),"got",self.s.readline()
        time.sleep(0.10)
        for c in data:
            self.s.write([c])
        print "Wrote", data,"got",self.s.readline()
        time.sleep(0.10)
        self.break_root()
        self.s.write(['R'])
        print "Read Back",self.s.read_all()
        
        
  
def main():
    """
    This is the main application code
    It runs everything in the main loop
    """
    app = QtGui.QApplication(sys.argv)
    window = CardWriter()
    window.show()
    #window.saveUP_PAYValues()
    sys.exit(app.exec_())
    return 0

def float_to_hex(f):
    print ">",f
    if f == None:
        return [0xff, 0xff, 0xff, 0xff]
    return bytearray(struct.pack("f", f))  

def float_to_hex_str(f):
    value = float_to_hex(f)
    result = "0x"
    for x in value:
        result += "%02X"%x
    return result
    


def hex_to_float(data):
    return struct.unpack('f',data)[0]
    
    
  

if __name__ == "__main__":
    value = 250.0 #example value
    value = float_to_hex(value)
    print([ "0x%02x" % b for b in value ])
    print str(value)
    print "Try", struct.unpack('f',bytearray([0xe8, 0x97, 0xbd, 0x54]))
    value =  struct.unpack('f',value)
    print "Rebuilt",eval('0x10')
    print '1234', eval('0x1234'), hex(eval('0x1234'))
    print bytearray(struct.pack('b', 0x555042414e4b00004c305633&0xFF))
    print float('nan')
    m = hashlib.md5()
    m.update("UPBANK\0\0R@G3")
    m.update("UP Pay")
    print [x for x in m.digest()]
    print to_hex_str("UPBANK\0\0R@G3")
    db = ACCOUNTDATABASE("type2.db")
    check = db.checkCard(eval(to_hex_str("UPBANK\0\0R@G3")))
    print "Check>",check
    #db.drop()
    for r in db.getALL():
        print r
        
    data = [0xFF]*256
    data[0:5] = [10, 20, 50, 60, 70]
    
    print data, len(data)
    data[2:5] = [30, 40, 50]
    print data
    c = Card()
    c['ATR'] = [0xA2, 0x13,0x10, 0x91]
    c['CardID'] = "UPBANK\0\0R@G3"
    print c
    print c.data
    print len(c.data), c[0]
    c[0:4] = [0,0,0,0]
    print c[0:4]
    print c
    main()
    
