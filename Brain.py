

def handle_command(msg):
    print("Got data: " + msg.get_message())
    msg.reply("I got your message. Thx.")