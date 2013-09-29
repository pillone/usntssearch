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
from SearchModule import *
import time
import urllib
		
# Search on NZBx.co
class al_OMGwtf(SearchModule):
	
	# Set up class variables
	def __init__(self):
		super(al_OMGwtf, self).__init__()
		self.name = 'Omgwtfnzbs'
		self.typesrch = 'OMG'
		self.queryURL = 'https://api.omgwtfnzbs.org/json/?search'
		self.baseURL = 'https://omgwtfnzbs.org/'
		self.queryURLSBreq = ''
		self.active = 0
		self.builtin = 1
		self.login = 1
		self.inapi = 0
		self.api_catsearch = 0
		self.caption_login_user = 'user'
		self.caption_login_pwd = 'api'
		self.returncode = 0
											 
		self.categories = {'Console': {'code':[1000,1010,1020,1030,1040,1050,1060,1070,1080], 'pretty': 'Console'},
							'Movie' : {'code': [2000, 2010, 2020], 'pretty': 'Movie'},
							'Movie_HD' : {'code': [2040, 2050, 2060], 'pretty': 'Movie - HD'},
							'Movie_SD' : {'code': [2030], 'pretty': 'Movie - SD'},
							'Audio' : {'code': [3000, 3010, 3020, 3030, 3040], 'pretty': 'Audio'},
							'PC' : {'code': [4000, 4010, 4020, 4030, 4040, 4050, 4060, 4070], 'pretty': 'PC'},
							'TV' : {'code': [5000, 5010, 5020, 5050, 5060, 5070, 5080], 'pretty': 'TV'},
							'TV_SD' : {'code': [5030], 'pretty': 'TV - SD'},
							'TV_HD' : {'code': [5040], 'pretty': 'TV - HD'},
							'XXX' : {'code': [6000, 6010, 6020, 6030, 6040, 6050, 6060], 'pretty': 'XXX'},
							'Other' : {'code': [7000, 7010], 'pretty': 'Other'},
							'Ebook' : {'code': [7020], 'pretty': 'Ebook'},
							'Comics' : {'code': [7030], 'pretty': 'Comics'}
							} 
							
		self.category_inv= {}
		for key in self.categories.keys():
			prettyval = self.categories[key]['pretty']
			for i in xrange(len(self.categories[key]['code'])):
				val = self.categories[key]['code'][i]
				self.category_inv[str(val)] = prettyval



	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~						

	def search(self, queryString, cfg):
		
		urlParams = dict(
			search=queryString,
			user=cfg['login'],
			api=cfg['pwd']
		)
		
		return self.search_internal(urlParams, self.queryURL, cfg)
						
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~						

	def search_internal(self, urlParams, urlq, cfg):
		timestamp_s = time.time()

		try:
			http_result = requests.get(url=urlq, params=urlParams, verify=False, timeout=cfg['timeout'])
		except Exception as e:
			print e
			log.critical(str(e))
			cfg['retcode'] = [600, 'Server timeout', tout, self.name]
			return []

		timestamp_e = time.time()
		log.info('TS ' + self.baseURL + " " + str(timestamp_e - timestamp_s))
		
		try:
			data = http_result.json()
		except Exception as e:
			print e
			cfg['retcode'] = [700, 'Server responded in unexpected format', timestamp_e - timestamp_s, self.name]
			return []
			
		parsed_data = []
					
		if ('notice' in data):
			log.info('Wrong api/pass ' + self.baseURL + " " + str(timestamp_e - timestamp_s))
			cfg['retcode'] = [100, 'Incorrect user credentials', timestamp_e - timestamp_s, self.name]			
			
			return []
		for i in xrange(len(data)):
			if(('nzbid' in data[i]) and ('release' in data[i]) and ('sizebytes' in data[i]) and ('usenetage' in data[i]) and ('details' in data[i])):
								
				category_found = {}
				if('categoryid' in data[i]):
					val = str(data[i]['categoryid'])
					if(val in self.category_inv):
						category_found[self.category_inv[val]] = 1
				if(len(category_found) == 0):
					category_found['N/A'] = 1
		
				d1 = {
					'title': data[i]['release'],
					'poster': 'poster',
					'size': int(data[i]['sizebytes']),
					'url': data[i]['getnzb'],
					'filelist_preview': '',
					'group': 'alt.binaries',
					'posting_date_timestamp': int(data[i]['usenetage']),
					'release_comments': data[i]['details'],
					'categ':category_found,
					'ignore':0,
					'provider':self.baseURL,
					'providertitle':self.name
				}

				parsed_data.append(d1)


		if(cfg is not  None):
			returncode = self.default_retcode
			if(	len(parsed_data) == 0 and len(data) < 300):
				returncode = self.checkreturn(data)
			returncode[2] = timestamp_e - timestamp_s
			returncode[3] = self.name
			cfg['retcode'] = copy.deepcopy(returncode)
		
		return parsed_data
