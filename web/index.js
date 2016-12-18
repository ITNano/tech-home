var app = require('express')();
var http = require('http').Server(app);
var server = require('./server').Server(http);

//Start server
var port = (process.argv.length>2?parseInt(process.argv[2]):80);
http.listen(port, function(){
	console.log("Server started, listening on port "+port);
});

//Fix file redirections
app.get('/', function(req, res, next){ res.sendFile(__dirname+'/index.html'); });
app.use('/imgs', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/pages', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/scripts', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });
app.use('/styles', function (req, res, next) { res.sendFile(__dirname+req.originalUrl); });