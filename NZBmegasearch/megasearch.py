# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by pillone.
#~ 
#~ NZBmegasearch is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.
#~ 
#~ NZBmegasearch is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.
#~ 
#~ You should have received a copy of the GNU General Public License
#~ along with NZBmegasearch.  If not, see <http://www.gnu.org/licenses/>.
# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    

import decimal
import datetime
import time
import dateutil.relativedelta
from operator import itemgetter
from urllib2 import urlparse

try:
	from bs4 import BeautifulSoup
except Exception:
	from BeautifulSoup import BeautifulSoup # Older BS versions
	print 'Falling back to older BeautifulSoup version'

import SearchModule

def dosearch(strsearch, cfg):
	strsearch = strsearch.strip()
	webbuf_head = html_head()
	webbuf_body = ''
		
	if(len(strsearch)):
		results = SearchModule.performSearch(strsearch, cfg['enabledModules'])
		results = summary_results(results,strsearch)
		webbuf_body = html_output(results)
	webbuf_foot = html_foot()	
	webbuf_ret = webbuf_head+webbuf_body+webbuf_foot	
	return webbuf_ret

def sanitize_html(value):
	VALID_TAGS = []
	soup = BeautifulSoup(value.replace("<\/b>", ""))

	for tag in soup.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True
	
	return soup.renderContents()
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def summary_results(results,strsearch):
	#~ sanitize
	for provid in xrange(len(results)):
		for i in xrange(len(results[provid])):
			results[provid][i]['title'] = sanitize_html(results[provid][i]['title'])

	results2 =[]
	ptr = []
	#~ all in one array
	for provid in xrange(len(results)):
		for z in xrange(len(results[provid])):
			results2.append(results[provid][z])
			ptr.append([provid, z])
	
	strsearch1 = strsearch.replace(" ", ".")
	
	print "Processing data..."	
	results2 = sorted(results2, key=itemgetter('posting_date_timestamp'), reverse=True) 	
	for z in xrange(len(results2)):
		findone = 0
		if(results2[z]['title'].lower().find( strsearch.lower() ) != -1):
			findone = 1
		if(results2[z]['title'].lower().find( strsearch1.lower()) != -1 ):
			findone = 1 
	
		#~ check same name, == takes too much time
		results2[z]  ['ignore'] = 0			
		#~ then update
		if(findone==0):
			results2[z]  ['ignore'] = 1		

	return results2
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

# Generate page header HTML
def html_head(): 		
	buf = '<!DOCTYPE html>\n'
	buf = buf+'<html>\n'
	buf = buf+'<head>\n'
	buf = buf+'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
	buf = buf+'<title>NZB MegasearcH</title>\n'
	buf = buf+'<style type="text/css">\n'
	buf = buf+'<!--\n'
	buf = buf+'@import url("static/style.css");\n'
	buf = buf+'-->\n'
	buf = buf+'</style>\n'
	buf = buf+'<script src="/static/overlay.js"></script>'
	buf = buf+'</head>\n'
	buf = buf+'<body>\n'
	buf = buf+'<div id="container">\n'
	buf = buf+'<span id="loader" style="visibility:hidden;"><img src="static/loadingicon.gif" width="75" height="75" /></span>'
	buf = buf+'<form action="/s" method="get"  class="form-wrapper-01">'		
	buf = buf+'<input type="text" id="search" placeholder="Enter your keyword" name="q"><input type="submit" value="Search" id="submit" onclick="show_loader()">'
	buf = buf+'</form>'	
	buf = buf+ '<table id="results" summary="Search Results"><thead>\n'
	buf = buf+'<tr><th scope="col" class=titlecell>Title</th><th scope="col" class=sizecell>Size</th> <th scope="col" class=datecell>Age</th> <th scope="col" class=providercell>Provider</th> </tr></thead><tbody>\n'
	return buf	

# Generate page footer HTML
def html_foot():
	buf = '</tbody></table>'
	buf = buf+'</div>\n';
	buf = buf+'<div class="topright">'
	buf = buf+'<a href= "config">Configure</a></div>'
	buf = buf+'</body></html>\n'	
	
	return buf
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

# Generate HTML for the results
def html_output(results): 
	buf= ''
	#~ for provid in xrange(len(results)):
		#~ for i in xrange(len(results[provid])):
	
	for i in xrange(len(results)):
		if(results[i]['ignore'] == 0):
			# Convert sized to smallest SI unit (note that these are powers of 10, not powers of 2, i.e. OS X file sizes rather than Windows/Linux file sizes)
			szf = float(results[i]['size']/1000000.0)
			mgsz = ' MB '
			if (szf > 1000.0): 
				szf = szf /1000
				mgsz = ' GB '
			# Calculate the age of the post
			dt1 =  datetime.datetime.fromtimestamp(results[i]['posting_date_timestamp'])
			dt2 =  datetime.datetime.today()
			rd = dateutil.relativedelta.relativedelta(dt2, dt1)
			#~ approximated date, whatev
			totdays = rd.years * 365  + rd.months * 31  + rd.days
			#~ homemade lazy stuff
			hname = urlparse.urlparse(results[i]['provider']).hostname			
			hname = hname.replace("www.", "")
			
			buf = buf+'<tr>\n'
			buf = buf+'<td class="titlecell"> <a href= "'+ results[i]['url']+ '"> ' + results[i]['title'] + '</a>'		
			buf = buf+'<td class="sizecell"> %.1f' % szf + mgsz + ' </td>\n'
			buf = buf+'<td class="datecell">' + str(totdays) + ' days </td>\n'
			buf = buf+'<td class="providercell"> <a href= "' + results[i]['provider'] + '"> ' +hname + '</a></td>\n'
			buf = buf+'</tr>\n'
	return buf

#~ debug
if __name__ == "__main__":
	print 'Save to file'
	webbuf_ret = dosearch('Hotel.Impossible.S01E01')
	myFile = open('results.html', 'w')
	myFile.write(webbuf_ret)
	myFile.close()

