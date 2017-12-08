import requests
from html.parser import HTMLParser
import os
import zipfile
import codecs
import string
import random

class ExtendedHTMLParser(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
    
    def get_attribute(self, attrs, attr):
        matches = [c[1] for c in attrs if c[0] == attr]
        if len(matches) == 1:
            return matches[0]
        else:
            return matches
            
    def has_attribute_value(self, attrs, attr, value):
        return len([c for c in attrs if c[0] == attr and c[1] == value]) > 0

# Parses the data from a Google search and finds the first search result link.
# The link will be stored in the instance variable link, if found.
# Use GoogleHTMLParser.feed(input) to insert the data to parse.
class GoogleHTMLParser(ExtendedHTMLParser):

    def __init__(self, eval_link):
        ExtendedHTMLParser.__init__(self)
        self.activated = False
        self.done = False
        self.link = None
        self.eval_link = eval_link

    def handle_starttag(self, tag, attrs):
        if not self.activated and tag == "div" and self.has_attribute_value(attrs, "class", "g"):
            self.activated = True
        elif self.activated and not self.done and tag == "a":
            link = self.get_attribute(attrs, "href")
            if link is not None and len(link) > 7:
                link = link[7:]
            if self.eval_link is None or self.eval_link(link):
                self.link = link
                self.done = True
            else:
                self.activated = False
                
class SubsceneHTMLParser(ExtendedHTMLParser):
    
    def __init__(self, eval_link):
        ExtendedHTMLParser.__init__(self)
        self.link = None
        
    def handle_starttag(self, tag, attrs):
        if tag == "a" and self.has_attribute_value(attrs, "id", "downloadButton"):
            self.link = "https://subscene.com" + self.get_attribute(attrs, "href")

# Retrieves the subtitle file of a series episode, either locally or from the
# internet (opensubtitles.com)
# param series: The exact name of the series
# param season: The season number
# param episode: The episode number
def get_series_subtitle(series, season, episode):
    target_file = series.replace(' ', '') + "_s" + get_two_digit_num(season) + "_e" + get_two_digit_num(episode) + ".srt"
    searchword = series + " s" + get_two_digit_num(season) + "e" + get_two_digit_num(episode)
    return get_subtitle(searchword, target_file)
    
# Retrieves the subtitle file of a movie, either locally or from the internet
# param movie: Searchword for the movie, the more exact the better.
def get_movie_subtitle(movie):
    target_file = movie + '.srt'
    return get_subtitle(movie, target_file)
    
# Retrieves a subtitle that matches the search word. If a file is already found
# on the given target file, this file is used and immediately returned.
# param searchword: The search word for the movie/series
# param target_filename: The wanted output filename of the result.
def get_subtitle(searchword, target_filename):
    target_dir = "subtitles"
    target_file = get_current_folder() + '/' + target_dir + "/" + target_filename
    if os.path.exists(target_file):
        return target_file
        
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    subtitle_path = get_subtitle_from_subscene(searchword, target_file)
    if subtitle_path is None:
        print("Using OpenSubtitles")
        subtitle_path = get_subtitle_from_opensubtitles(searchword, target_file)
    else:
        print("Using Subscene")
        
    return target_file
    
# Retrieves a subtitle file from opensubtitles and stores it in the given file
# location if possible.
# param subid: Opensubtitles subtitle ID for the wanted subtitle
# param filename: The path to store the subtitle to.
def get_subtitle_from_opensubtitles(searchword, filename):
    subid = get_opensubtitles_id(searchword)
    file_url = "http://dl.opensubtitles.org/en/download/vrf-108d030f/sub/"+subid
    return get_subtitle_from_zip(file_url, filename)
    
def get_subtitle_from_subscene(searchword, filename):
    base_url = "https://www.google.se/search?q="
    search_url = base_url + searchword.replace(' ', '+') + "+subtitles+\"subscene.com\"+english&ie=utf-8&oe=utf-8"
    def subscene_eval_link(link):
        return 'subscene.com' in link and 'english' in link
    subscene_link = get_google_result(search_url, subscene_eval_link)
    if subscene_link is not None:
        response = requests.get(subscene_link.split("&")[0])
        if not response.status_code == 200:
            print("Whoops, could not search for the file : Check internet connection")
            return None
        
        parser = SubsceneHTMLParser(subscene_eval_link)
        parser.feed(response.text)
        if parser.link is not None:
            downloadLink = parser.link
            return get_subtitle_from_zip(downloadLink, filename)
    
    return None
    
# Retrieve an opensubtitles subtitle id from a search word. This id can be used
# to specify a particular subtitle file.
# param searchword: The search word to find a specific subtitle file.
def get_opensubtitles_id(searchword):
    base_url = "https://www.google.se/search?q="
    search_url = base_url + searchword.replace(' ', '+') + "+subs+\"opensubtitles.org\"&ie=utf-8&oe=utf-8"
    def opensubtitles_eval_link(link):
        return 'opensubtitles.org' in link
    opensubtitles_link = get_google_result(search_url, opensubtitles_eval_link)
    if opensubtitles_link is not None:
        return opensubtitles_link.split("/")[-2]
    else:
        return None
    
def get_google_result(search_url, eval_link):
    response = requests.get(search_url)
    if not response.status_code == 200:
        print("Whoops, could not search for the file : Check internet connection")
        return None
    
    parser = GoogleHTMLParser(eval_link)
    parser.feed(response.text)
    
    if not parser.done or parser.link is None:
        print("Invalid input from the search : Check your internet connection")
        return None
    else:
        return parser.link
    
def get_subtitle_from_zip(file_url, filename):
    tmp_folder = get_random_string(16)
    tmp_file = tmp_folder + "/subtitle_tmp.zip"
    os.makedirs(tmp_folder)

    fetch_req = requests.get(file_url, stream=True)
    with open(tmp_file, 'wb') as tmp:
        for chunk in fetch_req.iter_content(chunk_size=512):
            if chunk:
                tmp.write(chunk)

    if not zipfile.is_zipfile(tmp_file):
        print("The subtitle could not be loaded!")
        return None
    
    zip = zipfile.ZipFile(tmp_file)
    members = zip.namelist()
    subtitle_file = None
    for member in members:
        if member[member.rfind('.'):] == ".srt":
            subtitle_file = member

    if subtitle_file is None:
        print("Invalid source file, could not find any subtitle file in it.")
        return None
        
    zip.extract(subtitle_file, path=tmp_folder)
    zip.close()
    
    os.rename(tmp_folder+"/"+subtitle_file, filename)
    os.remove(tmp_file)
    os.rmdir(tmp_folder)
    
    return filename
    
# Retrieves of a random string of the given length
# param length: The wanted length of the generated string.
def get_random_string(length):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))
    
# Retrieves the absolute path to the folder that the script is currently running in.
def get_current_folder():
    return os.path.dirname(os.path.realpath(__file__))
    
# Transforms the number so that is has two digits (and becomes a string). For example,
# 4 becomes 04 and 15 becomes 15. Values >= 100 will raise a ValueError.
# param num: The number to transform
def get_two_digit_num(num):
    if int(num) >= 0:
        if int(num) < 10:
            return "0"+str(num)
        elif int(num) < 100:
            return str(num)
        else:
            raise ValueError("Value must be less than 100")
    else:
        raise ValueError("Value must be greater than 0")
    