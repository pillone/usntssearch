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

# Search on Newznab
class ab_Findnzb(SearchModule):

	# Set up class variables
	def __init__(self, configFile=None):
		super(ab_Findnzb, self).__init__()
		# Parse config file		
		self.name = 'Findnzb'
		self.typesrch = 'FNB'
		self.queryURL = 'http://findnzbs.info/api'
		self.baseURL = ' https://findnzbs.info'
		self.api = '5b914645c6aa2a1c959113a5aafbb1a7'
		self.active = 1
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.api_catsearch = 1
		self.agent_headers = {	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' }	
		
		self.categories = {'Console': {'code':[1000,1010,1020,1030,1040,1050,1060,1070,1080], 'pretty': 'Console'},
							'Movie' : {'code': [2000, 2010, 2020], 'pretty': 'Movie'},
 							'Movie_HD' : {'code': [2040, 2050, 2060], 'pretty': 'HD'},
							'Movie_SD' : {'code': [2030], 'pretty': 'SD'},
							'Audio' : {'code': [3000, 3010, 3020, 3030, 3040], 'pretty': 'Audio'},
							'PC' : {'code': [4000, 4010, 4020, 4030, 4040, 4050, 4060, 4070], 'pretty': 'PC'},
							'TV' : {'code': [5000,  5020], 'pretty': 'TV'},
							'TV_SD' : {'code': [5030], 'pretty': 'SD'},
							'TV_HD' : {'code': [5040], 'pretty': 'HD'},
							'XXX' : {'code': [6000, 6010, 6020, 6030, 6040], 'pretty': 'XXX'},
							'Other' : {'code': [7000, 7010], 'pretty': 'Other'},
							'Ebook' : {'code': [7020], 'pretty': 'Ebook'},
							'Comics' : {'code': [7030], 'pretty': 'Comics'},
							} 
		self.category_inv= {}
		for key in self.categories.keys():
			prettyval = self.categories[key]['pretty']
			for i in xrange(len(self.categories[key]['code'])):
				val = self.categories[key]['code'][i]
				self.category_inv[str(val)] = prettyval

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def search_raw(self, queryopt, cfg):
		urlParams = dict(
			queryopt,
			o='xml',
			apikey=self.api
		)
		
		parsed_data = self.parse_xmlsearch(urlParams, cfg['timeout'])		
		return parsed_data		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
			
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(
			t='search',
			q=queryString,
			o='xml',
			apikey=self.api
		)
		
		parsed_data = self.parse_xmlsearch(urlParams, cfg['timeout'])		
		return parsed_data		
