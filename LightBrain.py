import json
from socket import *
import netifaces
from LightWifi import connect,get_current_connection,init_lightwifi
from time import sleep

def handle_command(msg):
    cmd = msg.get_message()
    print("Got cmd : " + cmd)
    if cmd == "get all states":
        msg.reply(json.dumps(get_all_bulbs()))
    elif cmd == "get rooms":
        msg.reply(json.dumps(rooms.keys()))
    elif cmd[:8] == "connect ":
        handle_response(msg, connect_to_bulb(get_bulb_by_name(cmd[8:])))
    elif cmd[:15] == "activate bulbs ":
        handle_response(msg, activate_bulbs(get_bulbs_by_names(cmd[15:].split())))
    elif cmd[:14] == "activate room ":
        handle_response(msg, activate_bulbs(get_bulbs_by_room(cmd[14:])))
    elif cmd[:17] == "deactivate bulbs ":
        handle_response(msg, deactivate_bulbs(get_bulbs_by_names(cmd[17:].split())))
    elif cmd[:16] == "deactivate room ":
        handle_response(msg, deactivate_bulbs(get_bulbs_by_room(cmd[16:])))
    elif cmd[:12] == "color bulbs ":
        data = cmd[12:].split()
        handle_response(msg, set_color(get_bulbs_by_names(data[5:]), int(data[0]), int(data[1]), int(data[2]), int(data[3]), int(data[4])))
    elif cmd[:11] == "color room ":
        data = cmd[11:].split()
        handle_response(msg, set_color(get_bulbs_by_room(' '.join(data[5:])), int(data[0]), int(data[1]), int(data[2]), int(data[3]), int(data[4])))
    else:
        print("Unknown command.")
        handle_response(msg, False)
        
def handle_response(msg, operation_success):
    if msg.sock is not None:
        if operation_success:
            msg.reply(json.dumps({'status':'success'}))
        else:
            msg.reply(json.dumps({'status':'failure'}))

def add_bulb(name, canonical_name):
    bulb = {}
    bulb["name"] = name
    bulb["canonical_name"] = canonical_name
    bulb["identifier"] = []
    for num in reversed([name[i:i+2] for i in range(3, len(name), 2)]):
        bulb["identifier"].append(int('0x'+num, 16))
    bulb["color"] = [0x00, 0x00, 0x00, 0xDD, 0x00]
    bulb["actual_color"] = None
    
    all_bulbs.append(bulb)
    
def get_all_bulbs():
    bulbs = []
    for bulb in all_bulbs:
        bulbs.append({"name":bulb["name"], "canonical_name":bulb["canonical_name"], "color":bulb["color"], "active":bulb["color"]==bulb["actual_color"], "rooms":get_rooms_of_bulb(bulb)})
    return bulbs
    
def get_bulb_by_name(name):
    for bulb in all_bulbs:
        if bulb["name"] == name:
            return bulb
    return None
    
def get_bulbs_by_names(names):
    bulbs = []
    for name in names:
        bulb = get_bulb_by_name(name)
        if bulb is not None:
            bulbs.append(bulb)
    return sorted(bulbs, key=bulb_sort_order)
    
def get_bulbs_by_room(room_name):
    return sorted(rooms.get(room_name, []), key=bulb_sort_order)
    
def get_rooms_of_bulb(bulb):
    bulb_rooms = []
    for (name, bulbs) in rooms.items():
        if bulb in bulbs:
            bulb_rooms.append(name)
    return bulb_rooms
    
def bulb_sort_order(bulb):
    return "" if bulb["name"] == get_current_connection() else bulb["name"]
    
def activate_bulbs(bulbs):
    success = True
    for bulb in bulbs:
        res = set_color([bulb], bulb["color"][0], bulb["color"][1], bulb["color"][2], bulb["color"][3], bulb["color"][4], False)
        success = success and res
    return success
    
def deactivate_bulbs(bulbs):
    return set_color(bulbs, 0x00, 0x00, 0x00, 0x00, 0x00, False)

def set_color(bulbs, red, green, blue, white, strength, save_result = True):
    data = [0xFB, 0xEB, red, green, blue, white, strength]
    for bulb in bulbs:
        data.extend(bulb["identifier"])
        data.append(0x00)
    packet_data = bytes(data)
            
    success = True
    for bulb in bulbs:
        if not bulb["actual_color"] == [red, green, blue, white, strength]:
            print("Handling "+bulb["name"])
            if connect_to_bulb(bulb):
                if save_result:
                    bulb["color"] = [red, green, blue, white, strength]
                bulb["actual_color"] = [red, green, blue, white, strength]
                send_message(packet_data)
            else:
                print("\tNo change due to connection errors.")
                success = False
        else:
            print("Color already set. Ignoring bulb "+bulb["name"])
    return success
    
def connect_to_bulb(bulb):
    success = connect(bulb["name"])
    global sock
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    return success
    
def send_message(content, retransmits=3):
    print("sending ",content," to sock ",sock)
    if sock is not None:
        for i in range(0, retransmits):
            sock.sendto(content, ("192.168.4.255", 30977))
            if i < retransmits-1:
                sleep(0.1)
    else:
        print("Error: Uninitialized socket!")
    
    
all_bulbs = []
add_bulb('CL_CFD4AA', 'Bedroom')
add_bulb('CL_CFD4BA', 'Kitchen')
add_bulb('CL_CFD4FA', 'Window')
rooms = {"all":all_bulbs, "bedroom":[all_bulbs[0]], "living room":[all_bulbs[1], all_bulbs[2]]}

init_lightwifi()

sock = None

