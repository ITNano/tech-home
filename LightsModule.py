from Client import ClientConnection
import re
from time import sleep
    
operation_successful = None
operation_wait_aborted = False
    
def handle_network_msg(connection, msg):
    global operation_successful
    print("Got message: "+msg)
    if not operation_wait_aborted:
        if msg == 'success':
            operation_successful = True
        else:
            operation_successful = False

def handle(text, mic, profile):
    if not conn.is_connected():
        print("Reconnecting")
        conn.connect()
        conn.start_recv_thread(handle_network_msg)
        
    cmd = text.replace('LIGHTS', '').replace('BULBS', '').strip().split()
    if cmd[0] == 'EXTERMINATE':
        handle_bulb_cases(cmd, 'deactivate')
        handle_response(mic)
    elif cmd[0] == 'ILLUMINATE':
        handle_bulb_cases(cmd, 'activate')
        handle_response(mic)
    elif cmd[0] == 'COLOR':
        if len(cmd) > 1 and cmd[1].lower() in colors.keys():
            color_data = colors.get(cmd[1].lower())
            if len(cmd) > 2:
                if cmd[2] == 'ROOM':
                    if len(cmd) > 3:
                        conn.send('color room '+color_data+' '+(' '.join(cmd[3:])).lower())
                    else:
                        mic.say('You have to specify a room!')
                        return
                elif cmd[2] in translator.keys():
                    conn.send('color bulbs '+color_data+' '+translator.get(cmd[2]))
                else:
                    mic.say('Invalid bulb name')
            else:
                conn.send('color room '+color_data+' all')
        else:
            mic.say('You have to specify an existant color!')
    else:
        mic.say("Unknown keyword detected")
        
def handle_response(mic):
    global operation_successful
    global operation_wait_aborted
    operation_wait_aborted = False
    counter = 0
    while(operation_successful is None and counter < 200):
        sleep(0.1)
        counter += 1
        
    if operation_successful is None:
        mic.say('The operation takes too long time.')
    elif not operation_successful:
        mic.say('Something not good happened. Try again.')
    else:
        return
    
    operation_wait_aborted = True
    operation_successful = None     # reset var.

def handle_bulb_cases(cmd, keyword):
    if len(cmd) > 2 and cmd[1] == 'ROOM':
        conn.send(keyword + ' room '+(' '.join(cmd[2:]).lower()))
    elif len(cmd) > 1 and cmd[1] in translator.keys():
        conn.send(keyword + ' bulbs '+translator.get(cmd[1]))
    else:
        conn.send(keyword + ' room all')
        
def isValid(text):
    return bool(re.search(r'\b(lights|bulbs)\b', text, re.IGNORECASE))
    
    
conn = ClientConnection("192.168.1.48", 63137)
conn.start_recv_thread(handle_network_msg)

WORDS = ['BULBS', 'LIGHTS', 'ILLUMINATE', 'EXTERMINATE', 'ROOM', 'LIVING', 'BEDROOM', 'WINDOW', 'KITCHEN', 'COLOR', 'WHITE', 'RED', 'GREEN', 'BLUE', 'YELLOW']
translator = {'WINDOW':'CL_CFD4FA', 'KITCHEN':'CL_CFD4BA'}
colors = {'white':'0 0 0 230 0', 'red':'255 0 0 0 0', 'green':'0 255 0 0 0', 'blue':'0 0 255 0 0', 'yellow':'255 255 0 0 0'}