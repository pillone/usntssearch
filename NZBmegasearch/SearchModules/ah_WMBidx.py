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
		self.name = 'Wombie'
		self.typesrch = 'WBX'
		self.queryURL = 'http://www.newshost.co.za/rss/'
		self.baseURL = 'http://www.newshost.co.za/'
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.api_catsearch = 1
		self.cookie = {}
		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def search_raw(self, queryopt, cfg):		
		return self.search(queryopt, cfg)
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	
	def dologin(self, cfg):	
		# does nothing, it fakes login and fixes sab error with filename
		self.cookie = {'FTDWSESSID' : 'Blub.blub'}
		return True
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
	# Perform a search using the given query string
	def search(self, queryString, cfg):
		urlParams = dict(
            sec= '',
            fr= 'false'	)
 
   		parsed_data = self.parse_xmlsearch_special(urlParams, cfg['timeout'], cfg)

		return parsed_data

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
	def parse_xmlsearch_special(self, urlParams, tout, tcfg): 
		parsed_data = []
		#~ print self.queryURL  + ' ' + urlParams['apikey']
		timestamp_s = time.time()	

		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=tout)
					
		except Exception as e:
			log.critical(self.queryURL + ' -- ' + str(e))
			if(tcfg is not  None):
				tcfg['retcode'] = [600, 'Server timeout', tout]
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
			
			elem_descrip = elem.find("description")
			elem_category = elem.find("category")
			
			if(elem_title is None or elem_url is None or elem_pubdate is None):
				continue
							
			#~ 03/22/2013 17:36
			len_elem_pubdate = len(elem_pubdate.text)
			
			try:
				elem_postdate =  time.mktime(datetime.datetime.strptime(elem_pubdate.text[0:len_elem_pubdate], "%m/%d/%Y %I:%M:%S %p").timetuple())
			except Exception as e:
				elem_postdate =  283996800
				
			elem_poster = ''

			elem_guid = elem.find("guid")
			release_details = self.baseURL

			if(elem_category is not None):
				category_found[elem_category.text.title()] = 1
			else:	
				category_found['N/A'] = 1
			
			#~ removes stray ' nzb' comment
			titletxt = elem_title.text
			rttf = titletxt.rfind(' nzb')
			if(rttf != -1):
				titletxt = titletxt [0:rttf]

			sizetxt = -1	
			if(elem_descrip is not None):
				rttf2a = elem_descrip.text.rfind('Size:');
				rttf2b = elem_descrip.text.rfind('Mb)');
				if(rttf2a != -1 and rttf2b != -1 ):
					sizetxt = int (elem_descrip.text[rttf2a+5:rttf2b]) * 1000000
									
			d1 = { 
				'title': titletxt,
				'poster': elem_poster,
				'size': sizetxt,
				'url': elem_url.attrib['url'],
				'filelist_preview': '',
				'group': '',
				'posting_date_timestamp': float(elem_postdate),
				'release_comments': self.baseURL,
				'categ':category_found,
				'ignore':0,
				'provider':self.baseURL,
				'req_pwd':self.typesrch,
				'providertitle':self.name
			}

			parsed_data.append(d1)
			
		#~ print d1
		returncode = self.default_retcode
		if(	len(parsed_data) == 0 and len(data) < 300):
			returncode = self.checkreturn(data)
		returncode[2] = timestamp_e - timestamp_s
		returncode[3] = self.name
		if(tcfg is not  None):
			tcfg['retcode'] = copy.deepcopy(returncode)

		return parsed_data

