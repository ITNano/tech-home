import socket
import time
import threading

class ClientConnection(object):

    msg_start = "[MSG] "
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.connect()

    def connect(self):
        if(self.sock is None):
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        
    def send(self, msg):
        if self.sock is not None:
            msg = ClientConnection.msg_start + msg
            bytes_sent = 0
            while bytes_sent < len(msg):
                sent = self.sock.send(msg[bytes_sent:].encode('utf-8'))
                if sent == 0:
                    print("Warning: An error might have occured on send")
                bytes_sent += sent
        else:
            print("Warning: Could not send since socket is closed.")
            
    def start_recv(self, recv_handler):
        self.receiving = True
        while self.receiving:
            try:
                data = self.sock.recv(2048)
                if data:
                    for cmd in data.decode('utf-8').split(ClientConnection.msg_start):
                        if len(cmd) > 0:
                            recv_handler(self, cmd)
                else:
                    raise ConnectionResetError("Disconnected")
            except ConnectionResetError:
                self.stop_recv()
                return False
                
    def start_recv_thread(self, recv_handler):
        t = threading.Thread(target = self.start_recv, args = (recv_handler,))
        t.daemon = True
        t.start()
            
    def stop_recv(self):
        self.receiving = False
        
    def close(self):
        self.stop_recv()
        if self.sock is not None:
            self.sock.close()
            self.sock = None
            

def handle_read(conn, cmd):
    print("Got response: "+cmd)
    
client = ClientConnection('192.168.1.35', 63137)
client.start_recv_thread(handle_read)
client.send("hej")
client.send("lel")
time.sleep(5)
client.close()