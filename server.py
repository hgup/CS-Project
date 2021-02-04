#=================== MODULES ====================#
import socket
import _thread
import sys
import pickle
from settings import Settings
import mapLoader
import time

inputs = sys.argv

def printStart():
    print(r'''
__     _______ ____ _____ _______  __
\ \   / / ____|  _ \_   _| ____\ \/ /
 \ \ / /|  _| | |_) || | |  _|  \  /
  \ V / | |___|  _ < | | | |___ /  \
   \_/  |_____|_| \_\|_| |_____/_/\_\

Server 2.0 for Vertex 2020
-----------------------------
Dedicated at Thy lotus feet
Don't play during study hours
-----------------------------
    ''')
class Server:

    def __init__(self, peers, port = None, level = 1):
        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'localhost'
        self.mapPath = r'./WorldData/Level ' + str(level) +'/' 
        self.level = level
        self.port = 9999 if port is not None else port
        if len(inputs) == 2:
            self.port = int(inputs[1])
        self.server_ip = socket.gethostbyname(self.server)
        self.bind()
        self.peers = peers
        self.socket.listen(self.peers)
        self.settings = Settings()
        self.vertex = []
        self.index = { 'pos' : 0, 'draw' : 1, 'name' : 2}
        self.available = [i for i in range(self.peers)]
        self.connected = []
        self.initVertex()
        _thread.start_new_thread(self.sleepingAnimation,())
        self.acceptRequest()

    def bind(self):
        try:
            self.socket.bind((self.server, self.port))
        except socket.error as err:
            print(str(err))

    def getAvailableId(self):
        if len(self.available) != 0:
            self.available.sort()
            i = self.available[0]
            del self.available[0]
            self.connected.append(i)
            self.showAvailableId()
            return i
        self.showAvailableId()


    def setAvailableId(self,theId):
        self.available.append(theId)
        self.connected.remove(theId)
        self.showAvailableId()

    def showAvailableId(self):
        print('available:',self.available)
        print('connected:',self.connected)

    def initVertex(self):
        """ initialize vertex here """
        # [(x,y) 0, draw? 1, name  2]
        self.vertex = [
                [(50,50),0,'p1'],
                [(250,100),0,'p2'],
                [(450,150),0,'p3']
                ][:self.peers]

    def threadedClient(self,conn,initData):
        myId = self.getAvailableId()
        if myId is not None:
            x,y = self.vertex[myId][0] # init Rect
            # available myId is actually the game.net.id
            conn.send(pickle.dumps([myId,x,y,self.peers]))
            print(conn.recv(32).decode())
            self.sendFile(self.mapPath + 'map.dat', conn)
            self.sendFile(self.mapPath + 'bg.png', conn)
            self.mainloop(conn, myId,initData)
            self.vertex[myId][1] = 0
            # now conn is useless
            self.setAvailableId(myId)
            print(f"id {myId} will now be available")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        else:
            conn.send(str.encode(str('Game is Full')))
        self.showAvailableId()

    def gameloop(self):
        while self.running:
            pass

    def sleepingAnimation(self):
        self.zzz = ''
        while self.running:
            self.zzz += 'z'
            if len(self.zzz) > 3:
                self.zzz = 'z'
            time.sleep(0.4)


    def mainloop(self, conn, myId,initData):
        running = True
        self.vertex[myId][1] = 1
        lastData = initData # [ name , paused ]
        while running:
            try:
                data = conn.recv(2048)
                received = pickle.loads(data) # [ id, rect, paused ]
                tempData = received[2:]
                if received[2]: # if paused
                    self.vertex[received[0]][self.index['name']] = self.zzz
                else:
                    self.vertex[received[0]][self.index['name']] = initData[0]
                    lastData = tempData
                if data:
                    self.vertex[received[0]][self.index['pos']] = received[1] # id[pos] = vec
                    conn.sendall(pickle.dumps(self.vertex))
                else:
                    conn.send(pickle.dumps(str(myId) + ' left the game'))
    
            except Exception as err:
                print(self.connections[myId][1],'left the game')
                self.vertex[myId][1] = 1
                running = False
                break

    def acceptRequest(self):
        self.connections = []
        c = 0
        print(f'[SERVER] OPEN AT PORT {self.port}')
        while self.running:
                c += 1
                print(f'[{c}] Waiting')
                conn,addr = self.socket.accept()
                initData = pickle.loads(conn.recv(32)) # [ name, paused ]
                self.connections.append((conn,addr))
                a = _thread.start_new_thread(self.threadedClient,(conn,initData))
        self.mapFile.close()
        self.mapBg.close()

    def sendFile(self,fileName,sock):
        with open(fileName,'rb') as f:
            d = f.read()
            sock.sendall(d)
        if sock.recv(32).decode() == 'Received:123':
            print(f'Received {fileName}')

if __name__ == "__main__":
    printStart()
    run = True
    while run:
        try:
            n = int(input('\tNUMBER OF PEERS: '))
            print("""
SERVER STARTED!
---------------""")
        except:
            print('By how many Peers I meant, specify a number...')
            continue
        Server(n,8888,1)
        run = True if input("restart server? (y/n) : ") == 'y' else False

# received = [id, vec]
