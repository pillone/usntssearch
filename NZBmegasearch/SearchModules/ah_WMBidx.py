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
import ConfigParser
from SearchModule import *
import time

# Search on Newznab
class ah_WMBidx(SearchModule):
	# Set up class variables
	def __init__(self, configFile=None):
		super(ah_WMBidx, self).__init__()
		# Parse config file		
		self.name = 'Wombie'
		self.typesrch = 'WBX'
		self.queryURL = 'http://www.newshost.co.za/rss/'
		self.baseURL = 'http://www.newshost.co.za/'
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.api_catsearch = 1

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def search_raw(self, queryopt, cfg):		
		return self.search(queryopt, cfg)
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	# Perform a search using the given query string
	def search(self, queryString, cfg):
		urlParams = dict(
            sec= '',
            fr= 'true'	)
 
   		parsed_data = self.parse_xmlsearch_special(urlParams, cfg['timeout'])	

		return parsed_data

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
	def parse_xmlsearch_special(self, urlParams, tout): 
		parsed_data = []
		#~ print self.queryURL  + ' ' + urlParams['apikey']
		timestamp_s = time.time()	

		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=tout)
					
		except Exception as e:
			mssg = self.queryURL + ' -- ' + str(e)
			print mssg
			log.critical(mssg)
			#~ error_rlimit = str(e.args[0]).find('Max retries exceeded')
			#~ print error_rlimit
			return parsed_data
		
		timestamp_e = time.time()
		#~ print "WOMBIE " + str(timestamp_e - timestamp_s)
		log.info('TS ' + self.baseURL + " " + str(timestamp_e - timestamp_s))

					
		data = http_result.text
		data = data.replace("<newznab:attr", "<newznab_attr")

		try:
			tree = ET.fromstring(data.encode('utf-8'))
		except Exception as e:
			print e
			return parsed_data

		#~ successful parsing
		for elem in tree.iter('item'):
			category_found= {}

			elem_title = elem.find("title")
			elem_url = elem.find("enclosure")
			elem_pubdate = elem.find("pubDate")
			len_elem_pubdate = len(elem_pubdate.text)
			#~ 03/22/2013 17:36
			elem_postdate =  time.mktime(datetime.datetime.strptime(elem_pubdate.text[0:len_elem_pubdate-6], "%m/%d/%Y %H:%M").timetuple())
			elem_poster = ''

			elem_guid = elem.find("guid")
			release_details = self.baseURL
			for attr in elem.iter('newznab_attr'):
				if('name' in attr.attrib):
					if (attr.attrib['name'] == 'poster'): 
						elem_poster = attr.attrib['value']
					if (attr.attrib['name'] == 'category'):
						val = attr.attrib['value']
						if(val in self.category_inv):
							category_found[self.category_inv[val]] = 1
						#~ print elem_title.text	
						#~ print val	
						#~ print category_found
						#~ print '=========='
			if(len(category_found) == 0):
				category_found['N/A'] = 1
			
			d1 = { 
				'title': elem_title.text,
				'poster': elem_poster,
				'size': -1,
				'url': elem_url.attrib['url'],
				'filelist_preview': '',
				'group': '',
				'posting_date_timestamp': float(elem_postdate),
				'release_comments': self.baseURL,
				'categ':category_found,
				'ignore':0,
				'provider':self.baseURL,
				'providertitle':self.name
			}

			parsed_data.append(d1)
			
		#~ that's dirty but effective
		if(	len(parsed_data) == 0 and len(data) < 100):
			limitpos = data.encode('utf-8').find('<error code="500"')
			if(limitpos != -1):
				mssg = 'ERROR: Download/Search limit reached ' + self.queryURL
				print mssg
				log.error (mssg)
		return parsed_data		
