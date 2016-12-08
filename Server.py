import socket
import threading
import sys
import netifaces
from Brain import handle_command

class ThreadedServer(object):
    def __init__(self, host, port, client_func):
        self.host = host
        self.port = port
        self.client_func = client_func
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.running = True
        self.sock.listen(5)
        while self.running:
            client, address = self.sock.accept()
            if self.running:
                client.settimeout(None)
                t = threading.Thread(target = self.client_func,args = (client,address))
                t.daemon = True
                t.start()
            else:
                print("Ignored a connection")

    def stop_listen(self):
        self.running = False
        
class NetworkMessage:
    
    def __init__(self, sock, msg, msg_start=""):
        self.sock = sock
        self.msg = msg
        self.msg_start = msg_start
        
    def get_message(self):
        return self.msg
    
    def reply(self, msg):
        self.sock.send((self.msg_start + msg).encode('utf-8'))
        

def handle_client(client, address):
    print("Got a connection from "+str(address))
    
    msg_start = "[MSG] "
    while True:
        try:
            data = client.recv(2048)
            if data:
                for msg in data.decode('utf-8').split(msg_start):
                    if len(msg) > 0:
                        handle_command(NetworkMessage(client, msg, msg_start))
            else:
                raise ConnectionResetError("Client disconnected")
        except ConnectionResetError:
            client.close()
            print("Closed connection to "+str(address))
            return False
    
def run_server(port):
    available_ip = available_ip_addresses()
    print("Available IPv4 addresses:")
    for ip in available_ip.get("ipv4"):
        print("\t" + ip + ":" + str(port))
    print("Available IPv6 addresses:")
    for ipv6 in available_ip.get("ipv6"):
        if "%" in ipv6:
            ipv6 = ipv6[:ipv6.find("%")-1]
        print("\t[" + ipv6 + "]:" + str(port))
    server = ThreadedServer('', port, handle_client)
    t = threading.Thread(target = server.listen)
    t.daemon = True
    t.start()
    return server
    
def available_ip_addresses():
    ip_list = []
    ipv6_list = []
    for name in netifaces.interfaces():
        addr = netifaces.ifaddresses(name)
        if addr.get(23, None) is not None:
            ipv6_list.append(addr.get(23)[0]['addr'])
        if addr.get(2, None) is not None:
            ip_list.append(addr.get(2)[0]['addr'])
    
    return {'ipv4':ip_list, 'ipv6':ipv6_list}
    
if __name__ == "__main__":
    port = 63137
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server = run_server(port)
    while True:
        data = input("Enter command to run: ")
        if data == "exit":
            server.stop_listen()
            sys.exit(0)
        else:
            handle_command(NetworkMessage(None, data, '[MSG] '))