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
from flask import render_template

try:
	from BeautifulSoup import BeautifulSoup
except Exception:
	from bs4 import BeautifulSoup # BeautifulSoup 4

import SearchModule

def dosearch(strsearch, cfg=None):
	if cfg == None:
		cfg = {'enabledModules':['nzbX.co','NZB.cc']}
	strsearch = strsearch.strip()
		
	if(len(strsearch)):
		results = SearchModule.performSearch(strsearch, cfg['enabledModules'])
		results = summary_results(results,strsearch)
	else:
		return render_template('main_page.html')
	
	return cleanUpResults(results)

def sanitize_html(value):
	VALID_TAGS = []
	soup = BeautifulSoup(value.replace("<\/b>", ""))

	for tag in soup.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True
	
	return soup.renderContents()
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def summary_results(rawResults,strsearch):
	#~ sanitize
	for provid in xrange(len(rawResults)):
		for i in xrange(len(rawResults[provid])):
			rawResults[provid][i]['title'] = sanitize_html(rawResults[provid][i]['title'])

	results =[]
	ptr = []
	#~ all in one array
	for provid in xrange(len(rawResults)):
		for z in xrange(len(rawResults[provid])):
			results.append(rawResults[provid][z])
			ptr.append([provid, z])
	
	strsearch1 = strsearch.replace(" ", ".")
	
	results = sorted(results, key=itemgetter('posting_date_timestamp'), reverse=True) 	
	for z in xrange(len(results)):
		findone = 0
		if(results[z]['title'].lower().find( strsearch.lower() ) != -1):
			findone = 1
		if(results[z]['title'].lower().find( strsearch1.lower()) != -1 ):
			findone = 1 
	
		#~ check same name, == takes too much time
		results[z]  ['ignore'] = 0			
		#~ then update
		if(findone==0):
			results[z]  ['ignore'] = 1		

	return results
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

# Generate HTML for the results
def cleanUpResults(results):
	niceResults = []
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
			
			niceResults.append({
				'url':results[i]['url'],
				'title':results[i]['title'],
				'filesize':str(round(szf,1)) + mgsz,
				'age':totdays,
				'providerurl':results[i]['provider'],
				'providertitle':hname
			})
	
	return render_template('main_page.html',results=niceResults)

#~ debug
if __name__ == "__main__":
	print 'Save to file'
	webbuf_ret = dosearch('Hotel.Impossible.S01E01')
	myFile = open('results.html', 'w')
	myFile.write(webbuf_ret)
	myFile.close()

