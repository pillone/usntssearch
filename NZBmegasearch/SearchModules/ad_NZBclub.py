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
import urllib
import time

class ad_NZBclub(SearchModule):
	# Set up class variables
	def __init__(self, configFile=None):
		super(ad_NZBclub, self).__init__()
		# Parse config file		
		self.name = 'NZBClub'
		self.typesrch = 'CLB'
		self.queryURL = 'http://www.nzbclub.com/nzbfeed.aspx'
		self.baseURL = 'http://www.nzbclub.com'
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.api_catsearch = 0
		self.agent_headers = {	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' }	
		self.categories = {'Console': {'code':[], 'pretty': 'Console'},
							'Movie' : {'code': [], 'pretty': 'Movie'},
 							'Movie_HD' : {'code': [], 'pretty': 'HD'},
							'Movie_SD' : {'code': [], 'pretty': 'SD'},
							'Audio' : {'code': [], 'pretty': 'Audio'},
							'PC' : {'code': [], 'pretty': 'PC'},
							'TV' : {'code': [], 'pretty': 'TV'},
							'TV_SD' : {'code': [], 'pretty': 'SD'},
							'TV_HD' : {'code': [], 'pretty': 'HD'},
							'XXX' : {'code': [], 'pretty': 'XXX'},
							'Other' : {'code': [], 'pretty': 'Other'},
							'Ebook' : {'code': [], 'pretty': 'Ebook'},
							'Comics' : {'code': [], 'pretty': 'Comics'},
							} 
		self.category_inv= {}
		for key in self.categories.keys():
			prettyval = self.categories[key]['pretty']
			for i in xrange(len(self.categories[key]['code'])):
				val = self.categories[key]['code'][i]
				self.category_inv[str(val)] = prettyval
		
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(q =queryString,
            ig= 1,
            rpp= 200,
            st= 5,
            sp= 1,
            ns= 1	)
         
		parsed_data = self.parse_xmlsearch_special(urlParams, cfg['timeout'], cfg)	

		return parsed_data
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def parse_xmlsearch_special(self, urlParams, tout, cfg): 
		parsed_data = []
		timestamp_s = time.time()	

		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=tout, headers= self.agent_headers)
					
		except Exception as e:
			log.critical(self.queryURL + ' -- ' + str(e))
			if(cfg is not  None):			
				cfg['retcode'] = [600, 'Server timeout', tout,self.name]
			return parsed_data

		timestamp_e = time.time()
		log.info('TS ' + self.baseURL + " " + str(timestamp_e - timestamp_s))
		
		data = http_result.text
		data = data.replace("<newznab:attr", "<newznab_attr")

		try:
			tree = ET.fromstring(data.encode('utf-8'))
		except Exception as e:
			if(cfg is not  None):
				cfg['retcode'] = [250, 'Server responded with an unexpected format', timestamp_e - timestamp_s,self.name]			
			return parsed_data

		#~ successful parsing
		for elem in tree.iter('item'):
			category_found= {}

			elem_title = elem.find("title")
			elem_url = elem.find("enclosure")
			elem_pubdate = elem.find("pubDate")
			len_elem_pubdate = len(elem_pubdate.text)
			#~ Tue, 22 Jan 2013 17:36:23 +0000
			#~ removes gmt shift
			try: 
				elem_postdate =  time.mktime(datetime.datetime.strptime(elem_pubdate.text[0:len_elem_pubdate-6], "%a, %d %b %Y %H:%M:%S").timetuple())
			except Exception as e:
				elem_postdate = datetime.datetime.now()
			
			elem_poster = ''

			elem_lnk = elem.find("link")
			release_details = self.baseURL
			if(elem_lnk is not None):
				release_details = elem_lnk.text
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
				'size': int(elem_url.attrib['length']),
				'url': urllib.quote(elem_url.attrib['url'], safe='/:' ),
				'filelist_preview': '',
				'group': '',
				'posting_date_timestamp': float(elem_postdate),
				'release_comments': release_details,
				'categ':category_found,
				'ignore':0,
				'provider':self.baseURL,
				'providertitle':self.name
			}

			parsed_data.append(d1)
			
		returncode = self.default_retcode
		if(	len(parsed_data) == 0 and len(data) < 300):
			returncode = self.checkreturn(data)
		returncode[2] = timestamp_e - timestamp_s
		returncode[3] = self.name
		if(cfg is not  None):
			cfg['retcode'] = copy.deepcopy(returncode)
						
		return parsed_data		
