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
from sets import Set
import decimal
import datetime
import time
import dateutil.relativedelta
from operator import itemgetter
from urllib2 import urlparse
from flask import render_template

import SearchModule

def dosearch(strsearch, cfg, ver_notify):
	strsearch = strsearch.strip()
		
	if(len(strsearch)):
		results = SearchModule.performSearch(strsearch, cfg )
		results = summary_results(results,strsearch)
	else:
		return render_template('main_page.html', vr=ver_notify)
	
	return cleanUpResults(results, ver_notify)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


def sanitize_html(value):
	if(len(value)):
		value = value.replace("<\/b>", "")
		value = value.replace("<b>", "")
		value = value.replace("&quot;", "")	
	return value


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def summary_results(rawResults,strsearch):
	results =[]
	titles = []
	sptitle_collection =[]

	#~ sanitize
	for provid in xrange(len(rawResults)):
		for i in xrange(len(rawResults[provid])):
			rawResults[provid][i]['title'] = sanitize_html(rawResults[provid][i]['title'])

	#~ all in one array
	for provid in xrange(len(rawResults)):
		for z in xrange(len(rawResults[provid])):
			title = rawResults[provid][z]['title'].lower().replace(" ", ".")
			titles.append(title);
			sptitle_collection.append(Set(title.split(".")))
			results.append(rawResults[provid][z])
			
	strsearch1 = strsearch.lower().replace(" ", ".")
	strsearch1_collection = Set(strsearch1.split("."))	

	for z in xrange(len(results)):
		findone = 0 
		results[z]  ['ignore'] = 0			
		intrs = strsearch1_collection.intersection(sptitle_collection[z])
		if ( len(intrs) ==  len(strsearch1_collection)):
			findone = 1
		
		#~ print sptitle_collection[z]
		#~ print str(len(intrs)) + " " + str(len(strsearch1_collection))
		if(findone):
			#~ print titles[z]
			for v in xrange(z+1,len(results)):
				if(titles[z] == titles[v]):
					sz1 = float(results[z]['size'])
					sz2 = float(results[v]['size'])
					if( abs(sz1-sz2) < 5000000):
						results[z]  ['ignore'] = 1

	results = sorted(results, key=itemgetter('posting_date_timestamp'), reverse=True) 
					
	return results

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def summary_results2(rawResults,strsearch):
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
	strsearch1_low =strsearch1.lower()
	strsearch_low =strsearch.lower()
	
	results = sorted(results, key=itemgetter('posting_date_timestamp'), reverse=True) 	
	#~ remove only perfect duplicates 
	for z in xrange(len(results)):
		findone = 0
		res_low = results[z]['title'].lower()
		if(res_low.find(strsearch_low) != -1):
			findone = 1
		if(res_low.find(strsearch1_low) != -1 ):
			findone = 1 
	
		results[z]  ['ignore'] = 0			
		#~ then update
		if(findone==0):
			results[z]  ['ignore'] = 1		

	return results
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

# Generate HTML for the results
def cleanUpResults(results, ver_notify):
	niceResults = []
	existduplicates = 0
	for i in xrange(len(results)):
		if(results[i]['ignore'] == 1):
			existduplicates = 1

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
		
		niceResults.append({
			'url':results[i]['url'],
			'title':results[i]['title'],
			'filesize':str(round(szf,1)) + mgsz,
			'age':totdays,
			'providerurl':results[i]['provider'],
			'providertitle':results[i]['providertitle'],
			'ignore' : results[i]['ignore']
		})

	return render_template('main_page.html',results=niceResults,exist=existduplicates, vr=ver_notify )

#~ debug
if __name__ == "__main__":
	print 'Save to file'
	webbuf_ret = dosearch('Hotel.Impossible.S01E01')
	myFile = open('results.html', 'w')
	myFile.write(webbuf_ret)
	myFile.close()

