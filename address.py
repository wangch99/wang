from socket import *
import fcntl
import struct 
import threading
from time import sleep,ctime

class LanChat(threading.Thread):

    def __init__(self,name,Range,flag):
        threading.Thread.__init__(self)
        self.addr = self.get_ip_info('eth0','addr')
        self.mask = self.get_ip_info('eth0','mask')
        self.name=name
        self.socket=[]
        self.Range =Range
        self.flag =flag
    @staticmethod            
    def get_ip_info(ifname,flag):
        s = socket(AF_INET,SOCK_DGRAM)
        if flag == 'addr':
            return inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',ifname[:15]))[20:24])
        if flag == 'mask':
            return inet_ntoa(fcntl.ioctl(s.fileno(),0x891b,struct.pack('256s',ifname[:15]))[20:24])
    
    @staticmethod
    def network_segment(addr,mask):
        ''' return a tuple containing start_site and end_site (only for IPV4)'''
        field_addr=addr.split('.')
        field_mask=mask.split('.')
        start_site = []
        end_site = []
        temp_site = []
        standard_mask = [255,255,255,255]
        for i in range(4):
            temp=(int(field_addr[i]) & int(field_mask[i]))
            start_site.append(temp)
            field = standard_mask[i] - int(field_mask[i])
            temp_site.append(field)
        
        for i in range(4):
            end_site.append(temp_site[i]+start_site[i])

        return (start_site,end_site)


    def run(self):
        '''Only for 255  '''
        PORT = 17300
        BUFSIZE = 1024
        if self.flag == 'client':
            beg_site,end_site =self.Range
            base_site=''
            for i in range(3):
                base_site+=str(beg_site[i])+'.'
            s = socket(AF_INET,SOCK_STREAM)
            for site in range(beg_site[3],end_site[3]+1):
                ADDR = base_site+str(site)
                try:
                    print 'pass1'
                    s.connect((ADDR,PORT))
                    print 'pass'
                    s.send('I m:',self.name) 
                except error,e:
                    continue

        if self.flag == 'server':
            s = socket(AF_INET,SOCK_STREAM)
            ADDR = ('',PORT)
            s.bind(ADDR)
            s.listen(5)
            while True:
                remote_sock,addr= s.accept()
                print '...connected from ',addr
                data=s.recv(BUFSIZE)
                print data

