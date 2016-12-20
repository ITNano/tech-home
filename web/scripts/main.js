/************************************************* /
** NOTE: This file requires the socket.io module  **
**       and jQuery to be loaded by the html doc  **
/**************************************************/
	
var socket;
var lightsUpdatesArray;
var moviesUpdatesArray;

function registerDataMover(eventName){
    if(!socket){
        console.log('Warning: Tried to register data mover before socket was initialized!');
    }else{
        var listenerArray = [];
        socket.on(eventName, function(data){
            var callback = listenerArray.shift();
            if(typeof callback == "function"){
                callback(data);
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
function get_movies(callback){
    msg = 'get list all';
    socket.emit('movies', msg);
    moviesUpdatesArray.push(callback);
}


/* ---------------------------- HELP FUNCTIONALITY ---------------------------- */
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