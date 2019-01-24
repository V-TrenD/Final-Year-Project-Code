'''

@author: Vussy Dube
'''

import os
import socket
import sqlite3
import struct
import sys
import sys
from threading import Thread
import time

from PyQt4 import QtCore, QtGui, uic, Qwt5
from PyQt4.QtGui import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import serial
import serial.tools.list_ports

from Databases import ACCOUNTDATABASE, toAccountPacket, getRawAccount, to_hex_str
from matplotlib import pyplot as plt

def plot(bitR, mean):
    plt.plot(bitR, 'o', color='g')
    plt.title("Card Reader Read Speed, AVG=%dkbps"%(mean/1000))
    plt.ylabel("Read Speed (bps)")
    plt.xlabel("Sample")
    #plt.ylim([0, 7e5])
    plt.plot([0,99], [mean, mean], 'r-')
    plt.savefig('temp.jpg')
    #plt.show()

class CardApplicationProvider(object):
    '''
    classdocs
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
        
class ApplicationServer(Thread):
    APPLICATION_ID = None
    APPLICATION_KEY = None
    APPLICATION_TABLE = None
    CARD_DATABASE = None
    __COLOUMS__ = "CARDID", "CARDKEY", "USERID", "USERINFO", "APPLICATIONDATA"
    
    def __init__(self):
        super(ApplicationServer, self).__init__()
        self.APPLICATION_IP = socket.gethostbyname(socket.gethostname())
        self.APPLICATION_PORT = 5630
    
    def run(self):
        self.sock = socket.socket()  # initialize the socket
        # server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)   # prepare to broadcast a socket
        # server_socket.sendto('this is testing',('255.255.255.255',12345))   # baradcasting to listening devices
        print "Binding Server To ", self.APPLICATION_IP, ":", self.APPLICATION_PORT
        self.sock.bind((self.APPLICATION_IP, self.APPLICATION_PORT))
        self.sock.listen(2)
        while True:
            print "Waiting for connections"
            conn, addr = self.sock.accept()
            # help(conn.recv)
            print "Starting Instance For", addr
            client = ServerInstance(conn, addr)
            client.start()
    
    
    
class ServerInstance(Thread):
    
    def __init__(self, connection, address):
        super(ServerInstance, self).__init__()
        self.conn = connection
        self.addr = address
        self.username = "ANDROID1"
        self.password = "DR0ID1"
        self.UUID = 400
        self.CUID = 400
        self.tloop=0
        
    def read(self):
        """Read Data from the connection socket"""
        return self.conn.recv(256).decode()
    
    
    def readline(self):
        """Read Data from the connection socket"""
        buffer = ""
        while True:
            c = self.conn.recv(1).decode()
            if c == '\n':
                return buffer
            buffer += c
            
        
    def write(self, msg):
        """Write Data to the connection socket"""
        print 'Writing>\t', msg
        self.conn.send(msg)
        
    def login(self, name, key):
        print "Login in as", name,
        if name == "ANDROID1" and key == "DR0ID1":
            self.UUID = 1
            print "True", "Root Level Login, Full access granted"
            return True, 400
        
        
        
    def run(self):
        print "Executing", self.addr
        cardDB = ACCOUNTDATABASE('type2.db')
        self.cardDB = cardDB
        breakCount = 10
        c = cardDB.checkCard(0x555042414e4b00004c305633)
        print c
        print cardDB.fetAccount(1, 0)
        
        while True:
            data = self.readline()
            print "Client[", self.addr, "]\t", data
            if len(data) == 0:
                print "Client Lost Connection!", self.addr
                breakCount -= 1
                if breakCount < 0:
                    break
            if data == "PING_ROOT":
                print "Returning to Root"
                self.write("AT_ROOT\n")
            elif data.startswith("CLIENT"):
                # LOGS IN A USER INTO THEIR ACCOUNT INSTANCE...
                # GIVES THEM THE ID NEEDED TO ACCESS THEIR ACCOUNT DATA IN THE FORM OF AN
                # APPLICATIONS INDEX
                res = data.split(":")
                print res
                username, password = eval(res[1])
                result, idenity = self.login(username, password)
                
                if result:
                    self.write("CLIENT:[%s %s %d ]\n" % (username, "true", idenity))
                else:
                    self.write("CLIENT:[%s %s %d ]\n" % (username, "false", -1))
            
            elif data == "PING":
                self.write("PING_OK\n")
            elif data.startswith("CHECKCARD"):  # Check If the card exits in the database
                res = data.split(":")
                params = eval(res[1])
                id = params[0]
                print id
                result = cardDB.checkCard(id)
                if result['CARDID'] != None:
                    self.write("CHECKCARD:[%d , %s]\n" % (id, "true"))
                else:
                    self.write("CHECKCARD:[%d , %s]\n" % (id, "false"))
            elif data.startswith("REGISTED"):
                # Checks if the Vendor ID is in the Vendor Database
                # This will log the tranaction under the vendors Data
                res = data.split(":")
                params = eval(res[1])
                id = params[0]
                print id
                if id == 4660:
                    self.write("REGISTED:[%d , %s]\n" % (id, "true"))
                else:
                    self.write("REGISTED:[%d , %s]\n" % (id, "false"))
            elif data.startswith("ACCOUNTS"):
                # Send the valid Accounts for the given Account ID
                # Gives all kinds of valid accounts accounts
                res = data.split(":")
                params = eval(res[1])  # integer number for account to check
                accountID = params
                accountData = cardDB.fetAccount(self.UUID, accountID)
                self.write("ACCOUNTS:%d\n%s"%(len(accountData),accountData))
                print 
            elif data.startswith("TRANSACTION"):
                # Transaction. Must be a transfer from the card holder account
                # to the current Users Account.. And must give new Updated
                # Card Infromation after the transaction
                print "Transaction"
                # get Card holders account from passed in appliaction data
                res = data.split(":")
                id, account,amount = eval(res[1])
                print "Card is",id," Account is", account,"Amount is", amount
                print to_hex_str(id)
                c = cardDB.transfer_card_to_account('UP_PAY', account, amount, self.UUID, id, account)
                print c
            elif data.startswith("Testing"):
                print "Reading test"
                readCount = 100
                times = []
                
                while readCount > 0:
                    start = time.time()
                    self.write("TIME\n")
                    #print self.read()
                    print self.readline()
                    dur = time.time() - start
                    if dur != 0.0:
                        readCount -= 1
                        times.append(dur)
                mean = sum(times)/len(times)
                print times, mean
                #plot(times, sum(times)/len(times))
                savefile = file("TransactionTime%d"%(mean/1000), 'w')
                savefile.write(str(times)+"\n")
                savefile.close()
            breakCount = 10
        print "Disconnected", self.addr
        self.conn.close()



server = ApplicationServer()
print "Starting Server"
server.start()



    
# dicr = eval("{'UP_PAY':{'VALID':0x1E,'CHEQUE':0x0000fa43,'CREDIT':0x0000c842,'SAVINGS':0x00007a44,'TOKENS':0x00007a43} }")
#ac = ACCOUNTDATABASE()
# ac.cursor.execute("UPDATE PAYMENTS set APPLICATIONINFO=? WHERE ID=1", 
#                  ("{'UP_PAY':{'VALID':0x1E,'CHEQUE':0x0000fa43,'CREDIT':0x0000c842,'SAVINGS':0x00007a44,'TOKENS':0x00007a43}}",))

# ac.db.commit()
# print dicr
# dicr = toAccountPacket(dicr)
# print dicr
# print getRawAccount(dicr['UP_PAY'])
# for key in dicr:
#     print key
#     for k2 in dicr[key]:
#         print k2, "%s"%dicr[key][k2]
#         
# print ([ "%02X"%b for b in bytearray(struct.pack("f", 500))])
# print ([ "%02X" % b for b in bytearray(struct.pack("f", 100))])
# print ([ "%02X" % b for b in bytearray(struct.pack("f", 1000))])
# print ([ "%02X" % b for b in bytearray(struct.pack("f", 250))])
