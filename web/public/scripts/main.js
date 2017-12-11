/************************************************* /
** NOTE: This file requires the socket.io module  **
**       and jQuery to be loaded by the html doc  **
/**************************************************/

function doRequest(service, cmd, callback){
    page = "/service/"+service+"/?cmd="+cmd.split(" ").join("%20");
    console.log("Loading "+page);
    httpGetAsync(page, function(res){
        if(res.code == 200){
            callback(JSON.parse(res.response));
        }else{
            callback({error: res.response});
        }
    });
}

/* -------------------------- BULBS ------------------------- */
function get_bulbs(callback){
    doRequest("lights", "get all states", callback);
}

function deactivate_bulb(name, callback){
    doRequest("lights", "deactivate bulbs "+name, callback);
}

function activate_bulb(name, callback){
    doRequest("lights", "activate bulbs "+name, callback);
}

function set_bulb_color(name, color, callback){
    doRequest("lights", "color bulbs "+color.join(' ')+' '+name, callback);
}


/* -------------------------- MOVIES ------------------------- */
var apiKey = 'c3aa6df001e2ebb866994c0a829cd0dc';

function get_movies(callback){
    doRequest("movies", "get list all", callback);
}

function getSeasons(series, callback){
    doRequest("movies", "get seasons:: "+series, callback);
}

function getNextEpisode(series, callback){
    doRequest("movies", "get next episode:: "+series, callback);
}

function playMovie(movie, callback){
    console.log("Should start movie "+movie);
    doRequest("movies", "start movie "+movie, callback);
}

function playEpisode(series, season, episode, callback){
    console.log("Should start "+series+" s"+season+"e"+episode);
    doRequest("movies", "start series "+series+"#.#"+season+"#.#"+episode, callback);
}

function playNextEpisode(series, callback){
    console.log("Should start next episode of "+series);
    doRequest("movies", "start series "+series+"#.#next", callback);
}

function getSeasonData(series_id, season, callback){
    var req = "https://api.themoviedb.org/3/tv/"+series_id+"/season/"+season;
    $.ajax({
        "url":req,
        "type":"GET",
        "data":{"api_key":apiKey},
        "success": function(data){
            const extractEpisode = function(data){
                return {"episode":data.episode_number, "name":data.name};
            };
            callback({"episodes":data.episodes.map(extractEpisode)});
        }, "error": function(xhr){
            callback({"error":true, "message":"["+xhr.status+": "+xhr.responseText+"]"});
        }
    });
}

function getMovieInfo(movie, type, callback){
    var service = {'movie':'movie', 'series':'tv'}[type];
    if(service){
        var req = "https://api.themoviedb.org/3/search/"+service;
        $.get(req, {"api_key":apiKey, "query":fixMovieName(movie, type)}, function(data){
            if(data.total_results > 0){
                id = data.results[0].id;
                var infoReq = "https://api.themoviedb.org/3/"+service+"/"+id;
                $.get(infoReq, {"api_key":apiKey}, function(response){
                    const extractGenres = function(obj){
                        return obj.name;
                    };
                    if(type == 'movie'){
                        callback({"id":id, "title":response.title, "tagline":response.tagline, "rating":response.vote_average, "description":response.overview, "genres":response.genres.map(extractGenres), "time":response.runtime, "release":response.release_date});
                    }else if(type == 'series'){
                        callback({"id":id, "title":response.name, "seasons": response.number_of_seasons, "genres":response.genres.map(extractGenres), "rating":response.vote_average, "description":response.overview});
                    }else{
                        callback({"error":true, "message":"Unhandled type, please review code."});
                    }
                });
            }else{
                callback({"error":true, "message":"Could not find movie"});
            }
        });
    }else{
        callback({"error":true, "message":"Invalid call. Type "+type+" not accepted"});
    }
}

function fixMovieName(name, type){
    if(type == "series"){
        return name;
    }else{
        // Just read until you find the year.
        var match = /(\(|\[|\{|)\d{4}(\)|\]|\}|)/.exec(name);
        if(match){
            name = name.substring(0, match.index);
        }
        // Remove junk before the title
        var regex = /\[.*\]( |-)*/g;
        match = regex.exec(name);
        if(match && match.index == 0){
            name = name.substring(regex.lastIndex);
        }
        match = /( |\.)[a-zA-Z]*(sub|SUB)/.exec(name);
        if(match){
            name = name.substring(0, match.index);
        }
        // Remove at invalid words (distributor names, dvdrip etc.)
        var invalidWords = ["dvdrip", "bluray", "1080p", "720p", "ac3"];
        var firstInvalid = findFirstOccurence(name, invalidWords);
        if(firstInvalid >= 0){
            name = name.substring(0, firstInvalid);
        }
        //Replace dots with spaces.
        name = name.replace(/\./g, ' ');
        return name;
    }
}

function findFirstOccurence(str, comparisonArr){
    var min = str.length+1;
    var str_lower = str.toLowerCase();
    for(var i in comparisonArr){
        var index = str_lower.indexOf(comparisonArr[i].toLowerCase());
        if(index >= 0){
            min = Math.min(min, index);
        }
    }
    
    return (min == str.length+1 ? -1 : min);
}


/* ---------------------------- HELP FUNCTIONALITY ---------------------------- */
function two_digit(num){
    return (num<10?'0':'')+num;
}

function isJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}

function httpGetAsync(url, callback){
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4){
            callback({code: xmlHttp.status, response: xmlHttp.responseText});
        }
    }
    xmlHttp.open("GET", url, true); // true for asynchronous 
    xmlHttp.send(null);
}


// @source : http://stackoverflow.com/questions/7837456/how-to-compare-arrays-in-javascript
// Warn if overriding existing method
if(Array.prototype.equals)
    console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
// attach the .equals method to Array's prototype to call it on any array
Array.prototype.equals = function (array) {
    // if the other array is a falsy value, return
    if (!array)
        return false;

    // compare lengths - can save a lot of time 
    if (this.length != array.length)
        return false;

    for (var i = 0, l=this.length; i < l; i++) {
        // Check if we have nested arrays
        if (this[i] instanceof Array && array[i] instanceof Array) {
            // recurse into the nested arrays
            if (!this[i].equals(array[i]))
                return false;       
        }           
        else if (this[i] != array[i]) { 
            // Warning - two different object instances will never be equal: {x:20} != {x:20}
            return false;   
        }           
    }       
    return true;
}
// Hide method from for-in loops
Object.defineProperty(Array.prototype, "equals", {enumerable: false});