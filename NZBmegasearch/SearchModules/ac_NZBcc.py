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
from SearchModule import *
import time

# Search on NZB.cc
class ac_NZBcc(SearchModule):
	# Set up class variables
	def __init__(self):
		super(ac_NZBcc, self).__init__()
		self.name = 'NZB.cc'
		self.typesrch = 'NZB'
		self.queryURL = 'https://nzb.cc/q.php'
		self.baseURL = 'https://nzb.cc'
		self.nzbDownloadBaseURL = 'http://nzb.cc/nzb.php?c='
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.api_catsearch = 1
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
				
				
				alt.binaries.tv

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def search_raw(self, queryopt, cfg):
	
		queryString = 'alt.binaries.tv'
		parsed_data = self.search(queryString, cfg)
		return parsed_data		
						
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def search(self, queryString, cfg):
		# Relaxed search on .cc
		urlParams = dict(
			q=queryString.replace(".", " ")
		)
		timestamp_s = time.time()	
		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=cfg['timeout'], headers= self.agent_headers)
		except Exception as e:
			log.critical(str(e))
			if(cfg is not  None):
				cfg['retcode'] = [600, 'Server timeout', tout, self.name]
			return []

		timestamp_e = time.time()
		log.info('TS ' + self.baseURL + " " + str(timestamp_e - timestamp_s))
					
		data = http_result.text
		# Start parsing the text
		cstart = 0
		cend = len(data)
		cstart = data.find("[", cstart, cend)+1

		#~ parse all members and put in parsed data
		parsed_data = []
		inc=1
		
		while True:
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
			url = self.nzbDownloadBaseURL + id_nzb
			
			cstart = s8b+1
			d1 = {  'title': name,
					'poster': poster_name,
					'size': filesize,
					'url': url,
					'filelist_preview': filelist_preview,
					'group': group,
					'posting_date_timestamp': posting_date_timestamp,
					'release_comments': self.baseURL,
					'categ':{'N/A' : 1},
					'ignore':0,
					'provider':self.baseURL,
					'providertitle':self.name
					}
			
			parsed_data.append(d1)
			#~ print d1["url"]
			#~ inc = inc +1 
			#~ print "=======" +str(inc)

			if(cfg is not  None):
				cfg['retcode'] = [200, 'ok', timestamp_e - timestamp_s, self.name]

		return parsed_data
