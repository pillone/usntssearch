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

# Search on NZBx.co
class aa_NZBx(SearchModule):
	
	
	
	# Set up class variables
	def __init__(self):
		super(aa_NZBx, self).__init__()
		self.name = 'nzbX.co'
		self.typesrch = 'NZX'
		self.queryURL = 'https://nzbx.co/api/search'
		self.baseURL = 'https://nzbx.co'
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.categories = {'Console': [1000,1010,1020,1030,1040,1050,1060,1070,1080],
							'Movie' : [2000, 2010, 2020, 2040, 2050, 2060, 2030],
							'HD' : [2040, 2050, 2060],
							'SD' : [2030],
							'Audio' : [3000, 3010, 3020, 3030, 3040],
							'PC' : [4000, 4010, 4020, 4030, 4040, 4050, 4060, 4070],
							'TV' : [5000, 5010, 5020, 5030, 5050, 5060, 5070, 5080],
							'SD' : [5030],
							'HD' : [5040],
							'XXX' : [6000, 6010, 6020, 6030, 6040, 6050, 6060],
							'Other' : [7000, 7010],
							'Ebook' : [7020],
							'Comics' : [7030],
							} 
		self.category_inv= {}
		for key in self.categories.keys():
			for i in xrange(len(self.categories[key])):
				val = self.categories[key][i]
				self.category_inv[str(val)] = key

	# Perform a search using the given query string
	def search(self, queryString, cfg):
		# Get JSON
		urlParams = dict(
			q=queryString
		)
		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=cfg['timeout'])
		except Exception as e:
			print e
			return []
		
		try:
			data = http_result.json()
		except Exception as e:
			print e
			return []
			
		parsed_data = []
		#~ data[i]['fromname'] removed for stability
		for i in xrange(len(data)):
			if('name' not in data[i]):
				return []

			category_found = {}
			if('categoryid' in data[i]):
				val = str(data[i]['categoryid'])
				if(val in self.category_inv):
					category_found[self.category_inv[val]] = 1

			if(len(category_found) == 0):
				category_found['N/A'] = 1

	
			release_details = 'https://nzbx.co/d?'+data[i]['guid']
			d1 = {
				'title': data[i]['name'],
				'poster': 'poster',
				'size': data[i]['size'],
				'url': data[i]['nzb'],
				'filelist_preview': '',
				'group': data[i]['groupid'],
				'posting_date_timestamp': int(data[i]['postdate']),
				'release_comments': release_details,
				'categ':category_found,				
				'ignore':0,
				'provider':self.baseURL,
				'providertitle':self.name
			}

			if d1['title'] is None:
				d1['title'] = 'None'
			
			parsed_data.append(d1)
		return parsed_data
