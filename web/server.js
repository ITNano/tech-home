var io;
var net = require('net');
var msgStart = '[MSG] ';
var serviceData = {};
var setupData = [{'service':'lights', 'ip':'192.168.1.10', 'port':63137, 'readCommands':['get all states']},
                 {'service':'movies', 'ip':'192.168.1.20', 'port':63137, 'readCommands':['get movies']}];

exports.Server = function(http){
	this.http = http;
	io = require('socket.io')(http);
    
    for(var i in setupData){
        service = setupData[i]['service'];
        serviceData[service] = {};
        serviceData[service]['trigger'] = service;
        serviceData[service]['datawaiters'] = [];
        serviceData[service]['connection'] = initConnection(io, setupData[i]['ip'], setupData[i]['port'], setupData[i]['service']);
        serviceData[service]['readCommands'] = setupData[i]['readCommands'];
    }
	
	io.on('connection', function(socket){
        for(serviceName in serviceData){
            socket.on(serviceData[serviceName]['trigger'], getMessageHandler(socket, serviceName));
        }
		/*socket.on('error', function(error){
			console.log('An error occured: '+error);
		});*/
	});
};

function getMessageHandler(socket, serviceName){
    return function(cmd){
        service = serviceData[serviceName];
        if(service['readCommands'].indexOf(cmd) >= 0){
            serviceData[serviceName]['datawaiters'].push(socket);
        }
        service['connection'].write(msgStart + cmd);
    };
}

function initConnection(io, ip, port, serviceName){
    socket = new net.Socket();
    socket.connect(port, ip, function(){
       console.log('Connected to server on '+ip+':'+port+' (service '+serviceName+')'); 
    });
    socket.on('data', function(data){
        messages = data.toString('utf-8').split(msgStart);
        for(var index in messages){
            message = messages[index];
            if(isJSONString(message)){
                message = JSON.parse(message);
            }
            
            if(message.length != 0){
                if(serviceData[serviceName]['datawaiters'].length > 0){
                    serviceData[serviceName]['datawaiters'].shift().emit(serviceData[serviceName]['trigger']+'data', message);
                }else{
                    io.emit(serviceData[serviceName]['trigger']+'data', message);
                }
            }
        }
    });
    socket.on('close', function(){
       console.log('Warning: Lost connection with the server'); 
    });
    
    return socket;
}

function isJSONString(json){
    try{
        JSON.parse(json);
        return true;
    }catch(e){
        return false;
    }
}