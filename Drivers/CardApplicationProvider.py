'''

@author: Vussy Dube
'''

import socket
import os
import sqlite3
import sys
import sys
from threading import Thread
import time

from PyQt4 import QtCore, QtGui, uic, Qwt5
from PyQt4.QtGui import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from Databases import ACCOUNTDATABASE
import serial
import serial.tools.list_ports


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
        self.APPLICATION_PORT = 5631
    
    def run(self):
        self.sock = socket.socket()      # initialize the socket
        #server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)   # prepare to broadcast a socket
        #server_socket.sendto('this is testing',('255.255.255.255',12345))   # baradcasting to listening devices
        print "Binding Server To ", self.APPLICATION_IP, ":",self.APPLICATION_PORT
        self.sock.bind((self.APPLICATION_IP, self.APPLICATION_PORT))
        self.sock.listen(2)
        while True:
            print "Waiting for connections"
            conn,addr = self.sock.accept()
            print "Starting Instance For", addr
            client = ServerInstance(conn, addr)
            client.start()
    
    
def checkCARDID(CARDID):
    try:
        all = cardDB.getALL()
        print all, CARDID
        for card in all:
            if card["CARDID"] == CARDID:
                return True
    except Exception as e:
        print e
    return False
    
class ServerInstance(Thread):
    
    def __init__(self, connection, address):
        super(ServerInstance, self).__init__()
        self.conn = connection
        self.addr = address
        
        
    def read(self):
        """Read Data from the connection socket"""
        return self.conn.recv(256).decode()
        
    def write(self, msg):
        """Write Data to the connection socket"""
        print 'Writing>\t',msg
        self.conn.send(msg)
        
    def run(self):
        print "Executing", self.addr
        
        while True:
            data = self.read()
            print "Client[", self.addr,"]\t",data
            if len(data) == 0:
                print "Client Lost Connection!", self.addr
                break
            if data == "PING_ROOT":
                print "Returning to Root"
                self.write("AT_ROOT\n")
            elif data == "PING":
                self.write("PING_OK\n")
            elif data == "CHECKCARD": # Check If the card exits in the database
                self.write("OK\n")
                CARDID = self.read()
                if(checkCARDID(CARDID)):
                    self.write("True\n")
                else:
                    self.write("False\n")
        print "Disconnected", self.addr
        self.conn.close()
            
server = ApplicationServer()
print "Starting Server"
server.start()
cardDB = ACCOUNTDATABASE()
