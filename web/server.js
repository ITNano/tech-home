var io;
var net = require('net');
var waitingForData = [];
var msgStart = '[MSG] ';

exports.Server = function(http){
	this.http = http;
	io = require('socket.io')(http);
    
    var lightsConn = initLightsConnection(io, '192.168.1.10', 63137);
    var lightsReadCommands = ['get all states'];
	
	io.on('connection', function(socket){
		socket.on('lights', function(cmd){
            if(lightsReadCommands.indexOf(cmd) >= 0){
                waitingForData.push(socket);
            }
			lightsConn.write(msgStart + cmd);
		});
		/*socket.on('error', function(error){
			console.log('An error occured: '+error);
		});*/
	});
};

function initLightsConnection(io, ip, port){
    socket = new net.Socket();
    socket.connect(port, ip, function(){
       console.log('Connected to lights server on '+ip+':'+port); 
    });
    socket.on('data', function(data){
        messages = data.toString('utf-8').split(msgStart);
        for(var index in messages){
            message = messages[index];
            if(message.length != 0){
                if(waitingForData.length > 0){
                    waitingForData.shift().emit('lightsdata', JSON.parse(message));
                }else{
                    io.emit('lightsdata', JSON.parse(message));
                }
            }
        }
    });
    socket.on('close', function(){
       console.log('Warning: Lost connection with the server'); 
    });
    
    return socket;
}