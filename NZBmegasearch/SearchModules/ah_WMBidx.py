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
		
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(
            sec= '',
            fr= 'true'	)
 
   		parsed_data = self.parse_xmlsearch(urlParams, cfg['timeout'])	
   		
   		#~ force null
   		for index in xrange(len(cfg)):
			parsed_data[index]['release_comments'] = self.baseURL
		return parsed_data
