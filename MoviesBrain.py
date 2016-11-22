import json
import Movies
from Subtitles import get_two_digit_num
import time
import os.path

def handle_command(msg):
    cmd = msg.get_message()
    if cmd == "get list all":
        msg.reply(json.dumps({"movies":Movies.get_movie_list(), "series":Movies.get_series_list()}))
    elif cmd == "show all":
        print("Want to show all stuffs on screen")
    elif cmd == "show movies":
        print("Want to show all movies on screen")
    elif cmd == "show series":
        print("Want to show all series on screen")
    elif cmd[:13] == "start series ":
        data = cmd[13:].split("#.#")
        if len(data) == 2:
            if data[1] == "next":
                series = data[0]
                (season, episode) = get_next_episode(series)
            elif data[1] == "restart":
                series = data[0]
                (season, episode) = get_next_episode(series, increment=False)
            else:
                msg.reply("Invalid syntax in the code. Contact system administrator")
                return
        elif len(data) == 3:
            series = data[0]
            season = int(data[1])
            episode = int(data[2])
        else:
            msg.reply("Invalid syntax in the code. Contact system administrator")
            return
        
        if Movies.start_episode(series, season, episode):
            watched_episode(series, season, episode)
    elif cmd[:12] == "start movie ":
        movie_name = Movies.start_movie(cmd[12:])
        if movie_name is not None:
            watched_movie(movie_name)
    else:
        msg.reply("Feature not implemented.")
        
def get_next_episode(series, increment = True):
    if watch_data.get(series, None) is None:
        # First time watching
        return (Movies.get_seasons_of_serie(series)[0], 1)
    else:
        for season in reversed(Movies.get_seasons_of_serie(series)):
            season_str = "S"+get_two_digit_num(season)
            if watch_data[series].get(season_str, None) is not None:
                episodes = Movies.get_nbr_of_episodes_in_season(series, season)
                for episode in reversed(range(1, episodes+1)):
                    episode_str = "E"+get_two_digit_num(episode)
                    if watch_data[series][season_str].get(episode_str, None) is not None:
                        if watch_data[series][season_str][episode_str]["seen"]:
                            if not increment:
                                return (season, episode)
                            else:
                                if episode == episodes:
                                    return (season+1, 1)
                                else:
                                    return (season, episode+1)
        
        return (Movies.get_seasons_of_serie(series)[0], 1)
    
def watched_movie(movie):
    if watch_data.get(movie) is None:
        counter = 0
    else:
        counter = watch_data[movie]["counter"]
    watch_data[movie] = {"type":"movie", "seen": True, "last_seen": time.strftime("%Y%m%d"), "counter":counter}
    save_watch_data()
    
def watched_episode(series, season, episode):
    season = "S"+get_two_digit_num(season)
    episode = "E"+get_two_digit_num(episode)
    if watch_data.get(series, None) is None:
        watch_data[series] = {"type":"series"}
        
    if watch_data[series].get(season, None) is None:
        watch_data[series][season] = {}
        
    watch_data[series][season][episode] = {"seen":True, "last_seen": time.strftime("%Y%m%d")}
    save_watch_data()
        
def load_watch_data():
    file = "movies_watch_data.json"
    if os.path.exists(file):
        with open(file) as f:
            return json.loads(''.join(f.readlines()))
    else:
        return {}

def save_watch_data():
    file = "movies_watch_data.json"
    with open(file, 'w') as f:
        f.write(json.dumps(watch_data))
 
watch_data = load_watch_data()