from Client import ClientConnection
import time
import json
import string
import re

def get_movie_words():
    conn.media_dict = None
    conn.send("get list all")
    counter = 0
    while(conn.media_dict is None):
        if counter > 30:
            print("Could not load movie titles. [timeout]")
            return []
        time.sleep(.10)
        counter += 1
        
    words = []
    for title in conn.media_dict['movies'] + conn.media_dict['series']:
        for word in title.replace(".", " ").split():
            if not any(char in set(string.punctuation) for char in word):
                if word not in ["1080P", "720P", "SWESUB", "DVDRIP", "BRRIP", "BLURAY", "HDTV", "3D", "X264", "X265", "WWW", "COM"] and not bool(re.search(r'\b(19[0-9][0-9]|2[0-9][0-9][0-9])\b', word)):
                    words.append(word)
        
    return list(set(words))
    
def handle_network_msg(connection, msg):
    if not firstLoad:
        connection.media_dict = json.loads()
        firstLoad = True
    elif msg[:6] == "start ":
        print("Setting message to : '" + msg[6:] + "'")
        connection.cmd_status = msg[6:]
    else:
        print(msg)

def handle(text, mic, profile):
    if not conn.is_connected():
        print("Reconnecting")
        conn.connect()
        conn.start_recv_thread(handle_network_msg)

    if "MOVIES" in text or "SERIES" in text:
        mic.say("What do you want to see?")
        response = mic.activeListen()
        while response is None:
            mic.say("Please repeat the name.")
            response = mic.activeListen()
    elif 'WATCH' in text:
        response = text.replace('WATCH', '').strip(' ')
        
    if "NEXT" in response:
        series = response.replace('NEXT', '').strip(' ')
        conn.send('start series ' + series + '#.#next')
        handle_started_media(mic, profile)
    elif response == "CLOSE":
        conn.send('close')
    else:
        for series in conn.media_dict.get("series", []):
            if response == series:
                mic.say('What season?')
                season = get_number_from_mic(mic)
                if season < 0:
                    return
                elif season == 0:
                    handle("WATCH NEXT "+series, mic, profile)
                    return
                mic.say('What episode?')
                episode = get_number_from_mic(mic)
                if episode < 0:
                    return
                conn.send('start series '+series+'#.#'+str(season)+'#.#'+str(episode))
                handle_started_media(mic, profile)
                return
                
        conn.send('start movie '+response)
        handle_started_media(mic, profile)
    
def handle_started_media(mic, profile):
    if wait_for_response() == FAILED_TO_PLAY:
        mic.say("Could not find what you wanted.")
    
def wait_for_response():
    conn.cmd_status = None
    counter = 0
    while counter < 50:
        if conn.cmd_status is not None:
            if conn.cmd_status == "failed":
                return FAILED_TO_PLAY
            elif conn.cmd_status == "success":
                return SUCCESS_TO_PLAY
            else:
                return INVALID_INFORMATION
        time.sleep(0.01)
        counter += 1
    return NO_INFORMATION
    
def get_number_from_mic(mic):
    number = -1
    while True:
        response = mic.activeListen()
        number = get_number(response)
        if number >= 0:
            break
        if response == "ABORT":
            mic.say("Okay, aborting.")
            return -1
        mic.say("That is not a number! Try again")
    return number
    
def get_number(str):
    if str is None:
        return -1
    elif any(word not in NUMBERS for word in str.split()):
        if str == "NEXT":
            return 0
        else:
            return -1
        
    if len(str.split()) == 1:
        return NUMBERS.index(str)
    else:
        number = 0
        for part in str.split():
            number = number*10 + NUMBERS.index(str)
        return number
    
def isValid(text):
    return bool(re.search(r'\b(movies|series|watch)\b', text, re.IGNORECASE))
    
    
conn = ClientConnection("192.168.1.49", 63137)
conn.start_recv_thread(handle_network_msg)
firstLoad = False

FAILED_TO_PLAY = -1
SUCCESS_TO_PLAY = 0
NO_INFORMATION = -2
INVALID_INFORMATION = -3

NUMBERS = ['ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'TEN', 'ELEVEN', 'TWELVE', 'THIRTEEN', 'FOURTEEN', 'FIFTEEN', 'SIXTEEN', 'SEVENTEEN', 'EIGHTEEN', 'NINETEEN', 'TWENTY']
WORDS = ['MOVIE', 'MOVIES', 'SERIES', 'WATCH', 'NEXT', 'ABORT', 'YES', 'NO', 'CLOSE']
WORDS.extend(NUMBERS)
WORDS.extend(get_movie_words())