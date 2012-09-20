from broadcast import *
from address import *
import json
from multhread import *
from Queue import Queue
import signal
import sys
import platform
class IM():

    def __init__(self):
        self.contact_dict={} 
        self.port = 17300
        self.broad_port = 2425
        self.local_ip = LanChat.get_ip_info('eth0','addr')
        self.addr_List = []
        self.Brd_Queue = Queue(128)
        self.Message_Queue = Queue(256)
        self.udp_send = socket(AF_INET,SOCK_DGRAM)
        self.udp_recv = socket(AF_INET,SOCK_DGRAM)
        self.threads= []
        self.alive = True
        self.brd = Broadcast()
        reload(sys)
        sys.setdefaultencoding('utf8')


    def showList(self):
        for i,addr in enumerate(self.addr_List):
            name=self.contact_dict[addr]['name']
            room=self.contact_dict[addr]['room']
            print i,'Address:',addr,'Name is:',name,'In rooms:',room
        print 'You Can communicate with ',len(self.addr_List),'people'
        
    def sendMsg(self,msg,addr):
        ADDR = (addr,self.port)
        self.udp_send.sendto(msg,ADDR)
    
    def recvMsg(self,queue,flag):
        ADDR = (self.local_ip,self.port)
        self.udp_recv.bind(ADDR)
        while self.alive:
            msg,addr=self.udp_recv.recvfrom(1024)
            message=unicode(msg)
            address,port = addr 
            data = self.contact_dict[address]['name']+' says: '+message
            queue.put(data,1)

    def readMsg(self,queue):

        data=queue.get(0)
        while data:
            print data
            try:

                data=queue.get(0)
            except Exception:
                break

    def NumOfRawMsg(self,queue):
        print 'You have ',queue.qsize(),'messages to read'

    def start(self):
        

        name=raw_input('Input Your Name:')
        room = raw_input('Input Your Room:')
        self.name=name
        self.room = room
        self.__Login()
        self.__Deamon_start()
        '''choose '''
        signal.signal(signal.SIGINT,self.__Deamon_join)
        self.__service_loop()
        self.__Exit()



    def __service_loop(self):
       
        sleep(1)
        self.showList()
        print """
            which on do u want to commu? 
            Input :f  to update the list
            Input :c to read your msg
            Input :bye to quit"""

        while True:
            

            self.NumOfRawMsg(self.Message_Queue)
            choice=raw_input('Your Option: ')

            if choice.lower() == ':f':

                self.showList()
            
            elif choice.isdigit():
                try:
                    
                    ADDR = self.addr_List[int(choice)]
                    while True:
                        msg=raw_input('>>>')
                        if msg == ':q':
                            break
                        self.sendMsg(msg,ADDR)
                except:
                    
                    print 'Not That Guy'

            elif choice.lower() == ':c':
                
                self.readMsg(self.Message_Queue)
                   
            elif choice.lower() == ':bye':
                break;
            else:
                print 'Input Error!!!'
         
    
    def __Deamon_start(self):
        args = (self.Brd_Queue,1)
        '''recv login or exit from Lan  '''
        recv_brd_t=MulThread(self.brd.recvBroadCast,args)
        recv_brd_t.start()
        self.threads.append(recv_brd_t)

        '''send login or exit to Lan'''
        message = self.__getOnlineMsg()
        arg_1 = (message,True,1)
        send_brd_t=MulThread(self.brd.sendBroadCast,arg_1)
        send_brd_t.start()
         
        self.threads.append(send_brd_t)
        arg_2 = (self.Message_Queue,1)
        recv_msg_t = MulThread(self.recvMsg,arg_2)
        recv_msg_t.start()

        self.threads.append(recv_msg_t)
        arg_3 = (self.Brd_Queue,1)
        up_list_t = MulThread(self.update_list,arg_3)
        up_list_t.start()
        self.threads.append(up_list_t)
        

    def __Deamon_join(self):
        self.brd.stopBroadCast()
        self.alive =False

    def update_list(self,queue,flag):
        '''add or remove'''
        data=queue.get(1)
        while data:
            entry_dict=json.loads(data)
            if 'exit' in entry_dict['2']:
                if entry_dict['1']['address'] in self.addr_List:
                    self.addr_List.remove(entry_dict['1']['address'])
                    self.contact_dict.pop(entry_dict['']['address'],0)
            else:
                if entry_dict['1']['address'] not in self.addr_List:
                    key = entry_dict['1']['address']
                    value = entry_dict['2']['content']
                    new_entry={key:value}
                    self.contact_dict.update(new_entry)
                    self.addr_List.append(key)
            data=queue.get(1)



    def recv_message(self,queue):

        SerSock = socket(AF_INET,SOCK_DGRAM)
        ADDR = ('',self.port)
        SerSock.bind()
        while True:
            data,addr=SerSock.recvfrom(1024)
            queue.put(data,1)
        
    
    def __Login(self):
        
        broad_cast = Broadcast()
        message = self.__getOnlineMsg()
        broad_cast.sendBroadCast(message,False,0)
        
    def __getOnlineMsg(self):
        
        address = {'address':self.local_ip}
        sub_content = {'name':self.name,'room':self.room}
        content = {'content':sub_content}
        '''
        content = {'address':self.local_ip,'name':self.name,'room':self.room}
        '''
        raw_message = {1:address,2:content}
        message=json.JSONEncoder().encode(raw_message)
        return message

    def __Exit(self):

        broad_cast = Broadcast()
        message = self.__getExitMsg()
        broad_cast.sendBroadCast(message,False,0)

    def __getExitMsg(self):

        address = {'address':self.local_ip}
        content = {'exit':' '}
        raw_message = {1:address,2:content}
        message = json.JSONEncoder().encode(raw_message)
        return message
        


        

