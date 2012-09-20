from socket import *
import fcntl
import struct
from time import sleep
class Broadcast():
    def __init__(self):
        self.broadaddr=self.Get_BroadAddr('eth0')
        self.PORT = 2425
        self.alive = True
    
    @staticmethod
    def Get_BroadAddr(ifname):
        s=socket(AF_INET,SOCK_DGRAM)
        return inet_ntoa(fcntl.ioctl(s.fileno(),0x8919,struct.pack('64s',ifname[:8]))[20:24])

    def recvBroadCast(self,queue,flag):
       
       SerSock = socket(AF_INET,SOCK_DGRAM)
       SerSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
       SerSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
       ADDR = ('',self.PORT)
       SerSock.bind(ADDR)
       while self.alive:
           data,addr=SerSock.recvfrom(1024)
           queue.put(data,1)
             
           

        
    def sendBroadCast(self,message,loop,interval):

        CliSock = socket(AF_INET,SOCK_DGRAM)
        CliSock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        CliSock.setsockopt(SOL_SOCKET,SO_BROADCAST,1)
        DEST = (self.broadaddr,self.PORT)
        CliSock.sendto(message,DEST)
        while loop and self.alive:
            try:
                sleep(interval)
                CliSock.sendto(message,DEST)
            except KeyboardInterrupt:
                break

            
        CliSock.close()
        
    def stopBroadCast(self):
        self.alive = False
