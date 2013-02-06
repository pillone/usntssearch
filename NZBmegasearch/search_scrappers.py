# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by pillone.
#~ 
#~ NZBmegasearch is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.
#~ 
#~ Foobar is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.
#~ 
#~ You should have received a copy of the GNU General Public License
#~ along with NZBmegasearch.  If not, see <http://www.gnu.org/licenses/>.
# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    

import requests
import json
import datetime
import time
import xml.etree.cElementTree as ET
from threading import Thread

#~ gets reset every time
results_total_glob = []

def search_request(strtosearch, cfg):

	#~ lazy solution for threading
	global results_total_glob 
	results_total_glob = []
	providers_total = []
	threadlist = []
	print "=== Search threads start ==="	
	for index in xrange(len(cfg)):
		if(cfg[index]['valid']== '1'):
			try:
				t = Thread(target=search_request_thread, args=(strtosearch,cfg[index],index))
				t.start()
				threadlist.append(t)
			except Exception, errtxt:
				print errtxt        
	for t in threadlist:
		t.join()
	print "=== Search threads ended ==="	
	results_total = results_total_glob
	return results_total
        
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def search_request_thread(strtosearch, cfg, i ):
	
	results = []	
	if(cfg['type'] == 'NZX' ):
		print "Searching w nzbx"
		results = parse_nzbx(strtosearch, cfg['url'], cfg['api'])
	if(cfg['type'] == 'NZB' ):
		print "Searching w nzbcc"
		results = parse_nzbcc(strtosearch, cfg['url'], cfg['api'])
	if(cfg['type'] == 'NAB' ):
		print "Searching w nab"	
		results = parse_newznab(strtosearch, cfg['url'], cfg['api'])
	
	results_total_glob.append(results)	 

       
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def search_request_monothread(strtosearch, cfg):

	results_total = []
	providers_total = []
	
	for i in xrange(len(cfg)):
		if(cfg[i]['valid']== '1'):
			if(cfg[i]['type'] == 'NZX' ):
				print "Searching w nzbx"
				results = parse_nzbx(strtosearch)
				results_total.append(results)
				providers_total.append('NZBX.CO')
			if(cfg[i]['type'] == 'NZB' ):
				print "Searching w nzbcc"
				results = parse_nzbcc(strtosearch)
				results_total.append(results)
				providers_total.append('NZB.CC')
			if(cfg[i]['type'] == 'NAB' ):
				print "Searching w nab"	
				results = parse_newznab(strtosearch, cfg[i]['url'], cfg[i]['api'])
				results_total.append(results)
				providers_total.append('NAB%d' % i)
	 
	return results_total, providers_total

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
'''
def parse_nzbcc(strtosearch, url, api):
	
	urlbase = "https://nzb.cc"
	#~ valid for nzbx.co
	url = 'https://nzb.cc/q.php';

	params = dict(
		q=strtosearch
		#~ q='pino'
		#~ , #~ r= '1'
	)
	r = requests.get(url=url,params=params, verify=False)
	data = r.text

	#~ init
	cstart = 0
	cend = len(data)
	cstart = data.find("[", cstart, cend)+1

	#~ parse all members and put in parsed data
	parsed_data = []
	inc=1
	while 1:
	#~ for i in xrange(1):
		cstart = data.find("[", cstart, cend)+1
		if cstart == 0:
			break
			
		s1 = data.find(',', cstart, cend)
		id_nzb = data[cstart:s1]
		
		s2a = data.find('"', s1+1, cend)+1
		s2b = data.find('"', s2a, cend)
		name = data[s2a:s2b]
		
		s3a = data.find('"', s2b+1, cend)+1
		s3b = data.find('"', s3a, cend)
		poster_name = data[s3a:s3b]

		s4a = data.find('"', s3b+1, cend)+1
		s4b = data.find('"', s4a, cend)
		filelist_preview = data[s4a:s4b]
		
		s5a = data.find('"', s4b+1, cend)+1
		s5b = data.find('"', s5a, cend)
		group = data[s5a:s5b]

		s6a = data.find(',', s5b+1, cend)+1
		s6b = data.find(',', s6a, cend)
		filesize = int(data[s6a:s6b]) * 1000000

		s7a = data.find('"', s6b+1, cend)+1
		s7b = data.find('"', s7a, cend)
		age = data[s7a:s7b]

		s8a = data.find('"', s7b+1, cend)+1
		s8b = data.find('"', s8a, cend)
		release_comments = data[s8a:s8b]

		#~ absolute day of posting
		intage = int(age[0:age.find(' ')])
		today = datetime.datetime.now()
		dd = datetime.timedelta(days=intage)
		earlier = today - dd
		posting_date_timestamp = time.mktime(earlier.timetuple())
		#~ print posting_date_timestamp 

		#~ convert for total nzb url
		#~ GET /nzb.php?c=54132542
		url = "http://nzb.cc/nzb.php?c=" + id_nzb
		
		cstart = s8b+1
		d1 = {  'title': name,
				'poster': poster_name,
				'size': filesize,
				'url': url,
				'filelist_preview': filelist_preview,
				'group': group,
				'posting_date_timestamp': posting_date_timestamp,
				'release_comments': release_comments,
				'ignore':0,
				'provider':urlbase
				}
		
		parsed_data.append(d1)
		#~ print d1["url"]
		#~ inc = inc +1 
		#~ print "=======" +str(inc)

	return parsed_data
'''

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
'''
def parse_nzbx(strtosearch, url, api):
	urlbase = "https://nzbx.co"

	#~ valid for nzbx.co
	url = 'https://nzbx.co/api/search';

	params = dict(
		#~ q='The Silver Wing'
		#~ q='impossible'
		q=strtosearch
	)
	r = requests.get(url=url,params=params)
	data = r.json()
		
	parsed_data = []
	for i in xrange(len(data)):
		d1 = {  'title': data[i]['name'],
						'poster': data[i]['fromname'],
						'size': data[i]['size'],
						'url': data[i]['nzb'],
						'filelist_preview': '',
						'group': data[i]['groupid'],
						'posting_date_timestamp': int(data[i]['postdate']),
						'release_comments': '',
						'ignore':0,
						'provider':urlbase
						}

		parsed_data.append(d1)
	return parsed_data
'''
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
'''
def parse_newznab(strtosearch, url, api):
	urlbase = url
	url = url+'/api'
	#~ valid for all newznab and spotweb (findnzb), always put api
	#~ url = 'http://findnzbs.info/api';
	#~ url = 'http://www.nzbfactor.com/spotweb/api';
	params = dict(
		t='search',
		q=strtosearch,
		o='xml',
		apikey=api
	)
	r = requests.get(url=url,params=params)
	data = r.text
	data = data.replace("<newznab:attr", "<newznab_attr")
	parsed_data = []
	
	#~ parse errors
	try:
			tree = ET.fromstring(data)
	except BaseException:
			print "ERROR: Wrong API?"
			return parsed_data

	#~ successful parsing
	for elem in tree.iter('item'):
		elem_title = elem.find("title")
		elem_url = elem.find("enclosure")
		elem_pubdate = elem.find("pubDate")
		len_elem_pubdate = len(elem_pubdate.text)
		#~ Tue, 22 Jan 2013 17:36:23 +0000
		#~ removes gmt shift
		elem_postdate =  time.mktime(datetime.datetime.strptime(elem_pubdate.text[0:len_elem_pubdate-6], "%a, %d %b %Y %H:%M:%S").timetuple())
		elem_poster = ''
		
		for attr in elem.iter('newznab_attr'):
			if('name' in attr.attrib):
				if (attr.attrib['name'] == 'poster'): 
					elem_poster = attr.attrib['value']
				#~ in case is not in default is also there
				#~ if (attr.attrib['name'] == 'size'): 
					#~ elem_sz =  attr.attrib['value']

		d1 = {  'title': elem_title.text,
							'poster': elem_poster,
							'size': int(elem_url.attrib['length']),
							'url': elem_url.attrib['url'],
							'filelist_preview': '',
							'group': '',
							'posting_date_timestamp': float(elem_postdate),
							'release_comments': '',
							'ignore':0,
							'provider':urlbase
							}
		parsed_data.append(d1)
	return parsed_data		
	#~ search_request('pino')
'''