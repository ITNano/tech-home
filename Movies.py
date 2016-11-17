from Subtitles import get_series_subtitle,get_movie_subtitle,get_two_digit_num
import os
import sys
from subprocess import call

# ---------------------------- OVERALL DOCUMENTATION -------------------------- #
# It is kind of hard to parse arbitrary movie and series names, especially if   #
# the structure of folders etc. can be arbitrary as well. Therefore, there are  #
# some restrictions. Please follow these, or the program will be unable to      #
# locate your video files.                                                      #
#                                                                               #
# Movies:                                                                       #
#   The folder can be named anything. The program will use the folder name when #
#   searching for the video. Dots (.) will be interpreted as spaces.            #
#   The program looks for a file with any of the file formats ['mp4', 'mov',    #
#   'mkv', 'avi']. If your file has another file format, please add it in the   #
#   find_movie_file function.                                                   #
#   When multiple video files are found, the program will grab the first one    #
#   that it founds. Make sure that this is the actual video file and not a      #
#   trailer etc.                                                                #
#                                                                               #
# Series:                                                                       #
#   The root folder should be named exactly as the series.                      #
#   Each season should be located as a subfolder with the name 'Season '+season #
#   where season is the season number (e.g. 'Season 3', NOT 'Season 03')        #
#   Each episode file name should contain two_digit_num(episode), with or       #
#   without a leading E (optional). E.g. 03 or E03 for episode 3.               #
#                                                                               #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#


# Change this if needed.
movies_folder = "G:"

# Retrieves a list of all available movies
def get_movie_list():
    movies = []
    for f in os.listdir(movies_folder):
        if os.path.isdir(movies_folder + "/" + f) and find_movie_file(f) is not None:
            movies.append(f.upper())
    return movies
    
# Retrieves a list of all available series.
def get_series_list():
    series = []
    for f in os.listdir(movies_folder):
        full_path = movies_folder + "/" + f
        if os.path.isdir(full_path) and is_series_folder(full_path):
            series.append(f.upper())
    return series
    
# Retrieves a list of all seasons of the given series
# param series: The exact name of the series
def get_seasons_of_serie(series):
    series_folder = movies_folder + "/" + series
    seasons = []
    for file in os.listdir(series_folder):
        if file.startswith('Season ') and os.path.isdir(os.path.join(series_folder, file)):
            seasons.append(file[7:])
    return seasons
    
# Retrieves the amount of episodes in a specific season of a series
# param series: The exact name of the series
# param season: The season number
def get_nbr_of_episodes_in_season(series, season):
    season_folder = movies_folder + "/" + series + "/Season " + str(season)
    for i in range(1, 50):
        found = False
        episode = get_two_digit_num(i)
        for file in os.listdir(season_folder):
            if episode in file:
                found = True
                break
        
        if not found:
            return i - 1
    return 50
    
# Checks whether the given folder follows the format of a series folder
# param folder: The folder to check
def is_series_folder(folder):
    try:
        for file in os.listdir(folder):
            if file.startswith('Season ') and os.path.isdir(os.path.join(folder, file)):
                return True
        return False
    except PermissionError:
        # Ignore folder, since permission denied.
        return False
    
# Starts the first movie that matches the searchword in vlc with subtitles
# if any subtitle file could be found, either locally or online.
# param movie: Searchword for the movie (e.g. on stranger tides)
def start_movie(movie):
    movie_file = find_movie_file(movie)
    if movie_file is not None:
        subtitle_path = get_movie_subtitle(movie_file[movie_file.rfind("/")+1:movie_file.rfind('.')])
        run_vlc(movie_file, subtitle_path)
    else:
        print("Movie not found")

# Starts the specified episode of the given series
# param series: The exact name of the series
# param season: The season number
# param episode: The episode number
def start_episode(series, season, episode):
    movie_file = find_series_file(series, season, episode)
    if movie_file is not None:
        subtitle_path = get_series_subtitle(series, season, episode)
        run_vlc(movie_file, subtitle_path)
    else:
        print("Series episode not found")
    
# Starts VLC with the given video and subtitle file
# param movie_file: Absolute path to the video file
# param subtitle_file: Absolute path to the subtitle file
def run_vlc(movie_file, subtitle_file):
    params = ['vlc']
    print("Using movie : " + movie_file)
    params.append("file:///"+movie_file)
    if not subtitle_file is None:
        print("Using subtitles : " + subtitle_file)
        params.append('--sub-file='+subtitle_file)
    params.append('--play-and-exit')
    params.append('--playlist-autostart')
    params.append('--no-random')
    
    call(params)

# Locates the video file of an episode of a series
# param series: The exact name of the series
# param season: The season number
# param episode: The episode number
def find_series_file(series, season, episode):
    try:
        folder = movies_folder + "/" + series + "/" + "Season " + str(season)
        keyword = "E" + get_two_digit_num(episode)
        file = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and keyword in f.upper()]
        if len(file) == 1:
            return folder + "/" + file[0]
        elif len(file) == 0:
            keyword = get_two_digit_num(episode)
            file = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and keyword in f.upper()]
            if len(file) == 1:
                return folder + "/" + file[0]
    except FileNotFoundError:
        print("Err: Series folder not found. Please place it at '"+folder+"'")

# Locates the video file of a movie
# param movie: Searchword for the movie (e.g. on stranger tides)
def find_movie_file(movie):
    movie = movie.upper()
    fileformats = ['.mp4', '.mov', '.mkv', '.avi']
    for folder in os.listdir(movies_folder):
        if movie in folder.upper() or movie in folder.upper().replace(".", " "):
            try:
                for file in os.listdir(movies_folder + "/" + folder):
                    for fileformat in fileformats:
                        if file.endswith(fileformat):
                            return movies_folder + "/" + folder + "/" + file
            except PermissionError:
                pass
            except FileNotFoundError:
                pass
    return None
    
# Wrapper for print(), handles exceptions for non-unicode chars.
# param text: The text to print
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print("Unable to print entry.")
        
# Simple main program. Let's you do three things:
#   list:                               Lists all available movies and series
#   movie [movie]:                      Starts a movie that contains the given name 
#   series [name] [season] [episode]:   Starts the specified episode
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'movie':
            if len(sys.argv) < 3:
                print("Insufficient number of parameters: Missing movie name")
            else:
                start_movie(sys.argv[2])
        elif sys.argv[1] == 'series':
            if len(sys.argv) < 5:
                print("Insufficient number of parameters.\nUsage :: python Movies.py series [series] [season] [episode]")
            else:
                start_episode(sys.argv[2], sys.argv[3], sys.argv[4])
        elif sys.argv[1] == 'list':
            print("Movies:\n------------")
            for movie in get_movie_list():
                safe_print(movie)
            print("\nSeries:\n-------------")
            for series in get_series_list():
                safe_print(series)
                for season in get_seasons_of_serie(series):
                    print("\tSeason " + season + " [" + str(get_nbr_of_episodes_in_season(series, season)) + " episodes]")
        else:
            print("Invalid input! Usage:\n\tlist: Lists all movies and series\n\tmovie [movie]: Plays movie\n\tseries [name] [season] [episode]: Plays episode in series")