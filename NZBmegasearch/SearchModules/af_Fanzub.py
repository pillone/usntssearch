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
import ConfigParser
from SearchModule import *

# Search on Newznab
class af_Fanzub(SearchModule):
	# Set up class variables
	def __init__(self, configFile=None):
		super(af_Fanzub, self).__init__()
		# Parse config file		
		self.name = 'Fanzub'
		self.typesrch = 'FAN'
		self.queryURL = 'https://www.fanzub.com/rss'
		self.baseURL = 'https://www.fanzub.com'
		self.active = 0
		self.builtin = 1
		self.login = 0
		self.inapi = 1
		self.api_catsearch = 0
				
		self.agent_headers = {	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' }			
		self.categories = {'Console': {'code':[], 'pretty': ''},
							'Movie' : {'code': ['Anime'], 'pretty': 'Anime'},
 							'Movie_HD' : {'code': ['Anime'], 'pretty': 'Anime'},
							'Movie_SD' : {'code': ['Anime'], 'pretty': 'Anime'},
							'Audio' : {'code': [], 'pretty': ''},
							'PC' : {'code': [], 'pretty': ''},
							'TV' : {'code': ['Anime'], 'pretty': 'Anime'},
							'TV_SD' : {'code': ['Anime'], 'pretty': 'Anime'},
							'TV_HD' : {'code': ['Anime'], 'pretty': 'Anime'},
							'XXX' : {'code': [], 'pretty': ''},
							'Other' : {'code': [], 'pretty': ''},
							'Ebook' : {'code': [], 'pretty': ''},
							'Comics' : {'code': [], 'pretty': ''},
							} 
		self.category_inv= {}
		for key in self.categories.keys():
			prettyval = self.categories[key]['pretty']
			for i in xrange(len(self.categories[key]['code'])):
				val = self.categories[key]['code'][i]
				self.category_inv[str(val)] = prettyval
						
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(
			q=queryString
		)

		parsed_data = self.parse_xmlsearch(urlParams, cfg['timeout'])		
		for i in xrange(len(parsed_data)):
			parsed_data[i]['categ'] = {'Anime': 1}

		return parsed_data		
