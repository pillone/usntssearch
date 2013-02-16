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
	 
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(
			t='search',
			q=queryString,
			o='xml',
			apikey=self.api
		)
		
		parsed_data = parse_xmlsearch(self, urlParams, cfg['timeout'])		
		return parsed_data		
