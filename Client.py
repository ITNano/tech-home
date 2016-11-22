import socket
import time
import threading
import sys

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
        
    def is_connected(self):
        return self.sock is not None
        
    def send(self, msg):
        if self.sock is not None:
            try:
                msg = ClientConnection.msg_start + msg
                bytes_sent = 0
                while bytes_sent < len(msg):
                    sent = self.sock.send(msg[bytes_sent:].encode('utf-8'))
                    if sent == 0:
                        print("Warning: An error might have occured on send")
                    bytes_sent += sent
            except:
                print("Got a connection error, closing socket.")
                self.close()
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
                    raise Exception("Disconnected")
            except:
                print("Got a connection error, closing socket.")
                self.close()
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
    
if __name__ == "__main__":    
    def handle_read(conn, cmd):
        print("Got response: "+cmd)
    client = ClientConnection('192.168.1.35', 63137)
    client.start_recv_thread(handle_read)
    while True:
        data = input("> ")
        if data == "exit":
            client.close()
            break
        else:
            client.send(data)