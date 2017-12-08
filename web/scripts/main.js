/************************************************* /
** NOTE: This file requires the socket.io module  **
**       and jQuery to be loaded by the html doc  **
/**************************************************/
	
var socket;
var lightsUpdatesArray;
var moviesUpdatesArray;
var buffers = {};

function registerDataMover(eventName){
    if(!socket){
        console.log('Warning: Tried to register data mover before socket was initialized!');
    }else{
        var listenerArray = [];
		buffers[eventName] = "";
        socket.on(eventName, function(data){
			if(typeof data == "object"){
				var callback = listenerArray.shift();
				if(typeof callback == "function"){
					callback(data);
				}
			}else{
				buffers[eventName] = buffers[eventName] + data;
				if(isJsonString(buffers[eventName])){
					var callback = listenerArray.shift();
					if(typeof callback == "function"){
						callback(JSON.parse(buffers[eventName]));
					}
					buffers[eventName] = "";
				}
			}
        });
        return listenerArray;
    }
}

function startConnection(callback){
    socket = io();
    socket.on('connect', function(socket){
        console.log('Connected to the server.');
        lightsUpdatesArray = registerDataMover('lightsdata');
        moviesUpdatesArray = registerDataMover('moviesdata');
        if(callback){
            callback();
        }
    });
}

/* -------------------------- BULBS ------------------------- */
function get_bulbs(callback){
    msg = 'get all states';
    socket.emit('lights', msg);
    lightsUpdatesArray.push(callback);
}

function deactivate_bulb(name, callback){
    msg = "deactivate bulbs "+name;
    socket.emit('lights', msg);
    lightsUpdatesArray.push(callback);
}

function activate_bulb(name, callback){
    msg = "activate bulbs "+name;
    socket.emit('lights', msg);
    lightsUpdatesArray.push(callback);
}

function set_bulb_color(name, color, callback){
    msg = "color bulbs "+color.join(' ')+' '+name;
    socket.emit('lights', msg);
    lightsUpdatesArray.push(callback);
}


/* -------------------------- MOVIES ------------------------- */
var apiKey = 'c3aa6df001e2ebb866994c0a829cd0dc';

function get_movies(callback){
    msg = 'get list all';
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
}

function getSeasons(series, callback){
    msg = 'get seasons '+series
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
}

function getNextEpisode(series, callback){
    msg = 'get next episode '+series
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
}

function playMovie(movie, callback){
    console.log('should start movie '+movie);
    msg = 'start movie '+movie;
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
}

function playEpisode(series, season, episode, callback){
    console.log('should start '+series+' s'+season+'e'+episode);
    msg = 'start series '+series+'#.#'+season+'#.#'+episode;
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
}

function playNextEpisode(series, callback){
    console.log('should start next episode of '+series);
    msg = 'start series '+series+'#.#next';
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
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