### NBA

This is my personal hobby project to learn web scraping in python. It's a command line tool to access NBA scores, box-score and standings. Data is scraped from [yahoo](www.yahoo.com/sports/nba). 

It uses [lxml](http://lxml.de/) for web scraping. I found another more interesting package called [scrapy](https://github.com/scrapy/scrapy) for web scraping. Underneath scrapy also depends on lxml. So I decided to try out using lxml first. 

### How to run?

It uses `python3`, and relies on few libraries. Recommended way to try it is by installing python3 via [virtualenv](https://virtualenv.pypa.io/en/stable/installation/)

#### Install pip
[pip](https://pip.readthedocs.io/en/stable/installing/) is available if you install python using `brew` in mac. If it doesn't work, you can try followings:
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```
#### Using virtualenv
Installation and Activation
```
pip install virtualenv
virtualenv <DIR>
source <DIR>/bin/activate
````
to deactivate:
```
deactivate
```

#### Dependencies
* [requests](https://github.com/kennethreitz/requests)
* [lxml](http://lxml.de/)
* [tabulate](https://bitbucket.org/astanin/python-tabulate)

#### Running NBA
* To get Today's scores:
```
python nba.py
```

* To get box score of a match
```
python nba.py -b MATCHID
```

* To get standings
```
python nba.py -s
```
* To get help
```
python nba.py -h

Usage: nba.py [options]

Options:
  -h, --help            show this help message and exit
  -s, --standings       Show NBA standings
  -b BOXID, --boxscore=BOXID
                        Show box score of a match ID
```

## About

If you found this little tool useful, I'd love to hear about it. You can also follow me on Twitter at [@iosCook](https://twitter.com/ioscook)
