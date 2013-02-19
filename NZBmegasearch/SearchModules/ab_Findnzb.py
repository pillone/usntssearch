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
		self.queryURL = 'https://findnzbs.info/api'
		self.baseURL = ' https://findnzbs.info'
		self.api = '5b914645c6aa2a1c959113a5aafbb1a7'
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
							'TV' : [5000,  5020, 5030, 5050, 5060],
							'SD' : [5030],
							'HD' : [5040],
							'XXX' : [6000, 6010, 6020, 6030, 6040],
							'Other' : [7000, 7010],
							'Ebook' : [7020],
							'Comics' : [7030],
							} 
		self.category_inv= {}
		for key in self.categories.keys():
			for i in xrange(len(self.categories[key])):
				val = self.categories[key][i]
				self.category_inv[str(val)] = key
		#~ print self.category_inv
		#~ if ('2030' in self.category_inv):
			#~ print 'IJDSOAJSsssssssssssssssssssssssssssssss'
		
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
