# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by 0byte.
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
from operator import itemgetter
from urllib2 import urlparse
from flask import render_template
import SearchModule
import logging

log = logging.getLogger(__name__)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class DoParallelSearch:
	
	# Set up class variables
	def __init__(self, conf):
		self.results = []
		self.cfg = conf
		self.svalid = 0
		for i in xrange(len(self.cfg)):
			if(self.cfg[i]['valid'] == '1'):
				self.svalid = self.svalid + 1

	def dosearch(self, args):
		results = SearchModule.performSearch(args['q'], self.cfg )
		self.results = summary_results(results, args['q'])
		
	def renderit(self,params):
		return cleanUpResults(self.results, params['sugg'], params['ver'], params['args'], self.svalid, params)
	
	def renderit_empty(self,params):	
		return render_template('main_page.html', vr=params['ver'], nc=self.svalid, sugg = [], 
								trend_show = params['trend_show'], trend_movie = params['trend_movie'] )
		

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def summary_results(rawResults,strsearch):

	results =[]
	titles = []
	sptitle_collection =[]

	#~ all in one array
	for provid in xrange(len(rawResults)):
		for z in xrange(len(rawResults[provid])):
			rawResults[provid][z]['title'] = SearchModule.sanitize_html(rawResults[provid][z]['title'])
			title = SearchModule.sanitize_strings(rawResults[provid][z]['title'])
			titles.append(title)
			sptitle_collection.append(Set(title.split(".")))
			results.append(rawResults[provid][z])
			
	strsearch1 = SearchModule.sanitize_strings(strsearch)
	strsearch1_collection = Set(strsearch1.split("."))	
	
	rcount = [0]*2
	for z in xrange(len(results)):
		findone = 0 
		results[z]['ignore'] = 0			
		intrs = strsearch1_collection.intersection(sptitle_collection[z])
		if ( len(intrs) ==  len(strsearch1_collection)):			
			findone = 1
		else:
			results[z]['ignore'] = 1	

		if(findone):
			#~ print titles[z]
			for v in xrange(z+1,len(results)):
				if(titles[z] == titles[v]):
					sz1 = float(results[z]['size'])
					sz2 = float(results[v]['size'])
					if( abs(sz1-sz2) < 5000000):
						results[z]  ['ignore'] = 1
		#~ stats
		rcount[	results[z]  ['ignore'] ] += 1			

	mssg = '[' + strsearch1 + ']'+ ' [' + strsearch + '] ' + str(rcount[0]) + ' ' + str(rcount[1])
	print mssg
	log.info (mssg)

	return results
	
 
 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

# Generate HTML for the results
def cleanUpResults(results, sugg_list, ver_notify, args, svalid, params):
	niceResults = []
	existduplicates = 0
			
	#~ sorting
	if 'order' not in args:
		results = sorted(results, key=itemgetter('posting_date_timestamp'), reverse=True) 
	else:
		if	(args['order']=='t'):
			results = sorted(results, key=itemgetter('title'))
		if	(args['order']=='s'):
			results = sorted(results, key=itemgetter('size'), reverse=True)
		if	(args['order']=='p'):
			results = sorted(results, key=itemgetter('providertitle'))
		if	(args['order']=='d'):
			results = sorted(results, key=itemgetter('posting_date_timestamp'), reverse=True) 
		if	(args['order']=='c'):
			results = sorted(results, key=itemgetter('categ'), reverse=True) 
			
	#~ do nice 
	for i in xrange(len(results)):
		if(results[i]['ignore'] == 1):
			existduplicates = 1

		# Convert sized to smallest SI unit (note that these are powers of 10, not powers of 2, i.e. OS X file sizes rather than Windows/Linux file sizes)
		szf = float(results[i]['size']/1000000.0)
		mgsz = ' MB '
		if (szf > 1000.0): 
			szf = szf /1000
			mgsz = ' GB '
		totdays = (datetime.datetime.today() - datetime.datetime.fromtimestamp(results[i]['posting_date_timestamp'])).days + 1		
		category_str = '' 
		keynum = len(results[i]['categ'])
		keycount = 0
		for key in results[i]['categ'].keys():
			category_str = category_str + key
			keycount = keycount + 1
			if (keycount < 	keynum):
			 	 category_str =  category_str + ' - ' 

		niceResults.append({
			'url':results[i]['url'],
			'title':results[i]['title'],
			'filesize':str(round(szf,1)) + mgsz,
			'cat' : category_str,
			'age':totdays,
			'details':results[i]['release_comments'],
			'providerurl':results[i]['provider'],
			'providertitle':results[i]['providertitle'],
			'ignore' : results[i]['ignore']
		})

	return render_template('main_page.html',results=niceResults, exist=existduplicates, 
											vr=ver_notify, args=args, nc = svalid, sugg = sugg_list,
											trend_show = params['trend_show'], trend_movie = params['trend_movie'])
