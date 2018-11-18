'''
Created on 20 Oct 2018

@author: Vussy Dube
'''
from socket import *
from PyQt4.QtCore import *



class Server(QObject):
    '''
    classdocs
    '''
    def __init__(self, params):
        '''
        Constructor
        '''
        
        

print "Server started"
host = "192.168.43.74"          #socket.gethostname()
port = 5630
print "Host", host,"Port:", port    

server_socket = socket()        #socket(AF_INET, SOCK_DGRAM)             # initialize the socket
#server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)   # prepare to broadcast a socket
#server_socket.sendto('this is testing',('255.255.255.255',12345))   # baradcasting to listening devices
server_socket.bind((host,port))
server_socket.listen(2)
conn,addr = server_socket.accept()
#help(conn)
print "Connection from"+str(addr)
conn.send("Server Is ready")

while True:
    data = conn.recv(256).decode()
    if not data:
        break
    print "message: "+str(data)

conn.close()
print host

while True:
    pass

