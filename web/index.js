var express = require('express'), app = express();
var http = require('http'), https = require("https");
var fs = require("fs");

var server = require('./server').Server(http);


var options = {
    key: fs.readFileSync('/etc/letsencrypt/live/matzmatz.se/privkey.pem', 'utf8'),
    cert: fs.readFileSync('/etc/letsencrypt/live/matzmatz.se/fullchain.pem', 'utf8')
};


app.use(express.static('public'));

//Fix file redirections
app.get('/', function(req, res, next){ res.sendFile(__dirname+'/index.html'); });
app.use('/imgs', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/pages', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/scripts', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/styles', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });


var port = (process.argv.length>2?parseInt(process.argv[2]):80);
http.createServer(app).listen(port+1, function(){
    console.log("Running HTTP on port "+(port+1));
});

https.createServer(options, app).listen(port, function(){
    console.log("Running HTTPS on port "+port);
});
