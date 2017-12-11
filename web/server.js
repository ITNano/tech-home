var io;
var buffers = {};
var net = require('net');
var msgStart = '[MSG] ';
var serviceData = {};

var setupData = [{'service':'lights', 'ip':'192.168.1.10', 'port':63137, 'readCommands':['get all states']},
                 {'service':'movies', 'ip':'192.168.1.20', 'port':63137, 'readCommands':['get list all', 'get seasons', 'get next episode'], 'enabled': true}];
                 
exports.init = function(){
    for(var i in setupData){
        if(setupData[i]['enabled']){
            service = setupData[i]['service'];
            serviceData[service] = {};
            serviceData[service]['trigger'] = service;
            serviceData[service]['datawaiters'] = [];
            serviceData[service]['connection'] = initConnection(io, setupData[i]['ip'], setupData[i]['port'], setupData[i]['service']);
            serviceData[service]['readCommands'] = setupData[i]['readCommands'];
        }
    }
};

exports.handleRequest = function(service, cmd, callback){
    console.log("REQUEST: "+service+"::'"+cmd+"'");
    expectRead = serviceData[service]['readCommands'].indexOf(cmd.split("::")[0]) >= 0;
    if(expectRead) serviceData[service]['datawaiters'].push(callback);
    serviceData[service]['connection'].write(msgStart + cmd.split("::").join(""));
    if(!expectRead) callback({});
};

function initConnection(io, ip, port, serviceName){
    socket = new net.Socket();
    socket.connect(port, ip, function(){
       console.log('Connected to server on '+ip+':'+port+' (service '+serviceName+')'); 
    });
    socket.on('data', function(data){
        var values = data.toString('utf-8').split(msgStart);
        for(var i = 0; i<values.length; i++){
            if(i > 0) buffers[serviceName] = "";
            var d = values[i];
            buffers[serviceName] = buffers[serviceName] + d;
            if(isJSONString(buffers[serviceName])){
                if(serviceData[serviceName]['datawaiters'].length > 0){
                    var callback = serviceData[serviceName]['datawaiters'].shift();
                    if(typeof callback == "function"){
                        callback(JSON.parse(buffers[serviceName]));
                    }
                }
                buffers[serviceName] = "";
            }
        }
    });
    socket.on('close', function(){
       console.log('Warning: Lost connection with the server'); 
    });
    socket.on('error', function(){
        console.log('Got an error from service '+serviceName);
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
