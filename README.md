**NZBmegasearcH** 
======================

NZBmegasearcH is a meta-search engine that retreives data from your favourite NZB indeces.

It is configurable with N#wsnb-based, Spotw#b-based, an many others indeces. 
It natively supports CP and SB, retreives trending movies and shows, gives appropriate search suggestions.

It is written in Python and it works on linux, mac, win. Windows binaries are also available.

**Latest version is 0.31**

This project makes use of:

- Python 2.7
- [Flask] (http://flask.pocoo.org/)
- [Requests] (http://docs.python-requests.org/en/latest/)
- [BeautifulSoup] (http://www.crummy.com/software/BeautifulSoup/)
- [Mechanize] (http://wwwsearch.sourceforge.net/mechanize/)
- [PyOpenSSL] (https://launchpad.net/pyopenssl/)



Install
================

**Windows**

- Download latest available binary from [usntssearch-binaries/windows] (https://github.com/pillone/usntssearch-binaries/tree/master/windows)
- There are two binaries avaliable: 
 * win32_NZBMegasearcH_0.XX-noconsole.zip runs silently without console output
 * win32_NZBMegasearcH_0.XX-wconsole.zip runs with console output
- Unzip in a folder and click on mega2.exe
- Open browser to localhost:5000

**Linux**

- apt-get install python2.7 git python-openssl
- git clone https://github.com/pillone/usntssearch.git
- Enter in the usntssearch/NZBmegasearch directory and run "python mega2.py" to start 
- Open browser to localhost:5000


Updates
================

**Changes in v0.31**

- **Selectable IMDB suggestions, trends**
- **Selectable default search option**
- **Selectable Active/Non active NAB providers**
- **Silent, AJAX connected SABNZB connectivity**
- **Config user protection**
- **Deepsearch locale bug fixed**


Changes in v0.30

- Supports user-pass Newsznab indeces (in case API system not supported)
- Supports SB tv show discovery
- Supports HTTPS-SSL serving
- Supports sabnzbd integration (one-click send)
- Supports FTDworld authentication to enable download
- Added Wombie's index as built-in provider
- Many code and interface improvements
- Many bugs fixed


Changes in v0.28

- Finally logging with autorotation -- thanks PeterBeard
- Finally linux version automatically updates
- No more python lib dependencies. Everything is packed. No need to run setup.
- Windows binaries are available
- Unified graphics between Chrome and Firefox
- Many undocumented and obscure interplatform bugs fixed. Countless hours spent.

Changes in v0.271

- Superbug introduced and fixed. Sorry everybody.

Changes in v0.27

- COUCHPOTATO support added

Changes in v0.26

- Suggestions over search (only movies for now...)
- Display trending movies
- Display trending shows with autosearch current episodes
- Lots of coding and fixes

Changes in v0.252

- Improved search query sanitizing for better provider search 
- Improved SICKBEARD search queries for shows with duplicates, thanks judhat2

Changes in v0.251

- Big bug fixed in searches with many Newsznab providers (a bad one)
- Other fixes and improvements

Changes in v0.25

- SICKBEARD connectivity complete
- Improvements in search providers

Changes in v0.24

- Sort in title, age, size, provider

Changes in v0.23

- Change port
- Support username and pwd, thanks to userpasscombine
- Timeout for long responses
- Improved ver. checking


Changes in v0.21

- Added automatic notification of newer versions
- Improved searches (faster, better)
- bug fixes

Changes in v0.20

- Added support for FTDworld.net, Fanzub
- Findnzb does not need any API! thanks to the Findnzb team
- Merged modularization improvements, thanks to PeterBeard!
- Setup improvements, thanks to fxjkhr
- Too many bug fixes
- Search stability improvements
- Improved look and feel


<a title="website statistics" href="http://statcounter.com/"
target="_blank"><img
src="http://c.statcounter.com/8769563/0/45111251/0/"
alt="website statistics" style="border:none;"></a>
