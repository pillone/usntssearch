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
from urllib2 import urlparse


# Search on Newznab
class Newznab(SearchModule):
	# Set up class variables
	def __init__(self, configFile=None):
		super(Newznab, self).__init__()
		# Parse config file		
		self.name = 'Newznab'
		self.typesrch = 'NAB'
		self.queryURL = 'xxxx'
		self.baseURL = 'xxxx'
		self.nzbDownloadBaseURL = 'NA'
		self.builtin = 0
		self.inapi = 1
		
	# Perform a search using the given query string
	def search(self, queryString, cfg):
		# Get text
		urlParams = dict(
			t='search',
			q=queryString,
			o='xml',
			apikey=cfg['api']
		)
		self.queryURL = cfg['url'] + '/api'
		self.baseURL = cfg['url']
		
		#~ homemade lazy stuff
		humanprovider = urlparse.urlparse(cfg['url']).hostname			
		self.name = humanprovider.replace("www.", "")
		parsed_data = self.parse_xmlsearch(urlParams, cfg['timeout'])	
		
		return parsed_data		
