var express = require('express'), app = express();
var http = require('http'), https = require("https");
var fs = require("fs");

var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: true }));

var server = require('./server');
server.init();

function onlyHttp(){
    return process.argv.length > 2 && process.argv[2] == "--http-only";
}

if (!onlyHttp()){
    var options = {
        key: fs.readFileSync('/etc/letsencrypt/live/movies.matzmatz.se/privkey.pem', 'utf8'),
        cert: fs.readFileSync('/etc/letsencrypt/live/movies.matzmatz.se/fullchain.pem', 'utf8')
    };
}


app.use(express.static('public'));

//Fix file redirections
app.get('/', function(req, res, next){ res.sendFile(__dirname+'/index.html'); });
app.use('/imgs', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/pages', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/scripts', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/styles', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/service/:service/', function(req, res, next){
    server.handleRequest(req.params.service, req.query.cmd, function(result){
        
        if(result.error){
            res.status(400).send(result.error);
        }else{
            res.send(JSON.stringify(result));
        }
    });
});


var port = (process.argv.length>2?parseInt(process.argv[process.argv.length-1]):80);
http.createServer(app).listen(port, function(){
    console.log("Running HTTP on port "+port);
});

if(!onlyHttp()){
    https.createServer(options, app).listen(port+1, function(){
         console.log("Running HTTPS on port "+(port+1));
    });
}
