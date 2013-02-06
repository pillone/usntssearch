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

# Search on NZBx.co
class NZBx(SearchModule):
	# Set up class variables
	def __init__(self):
		super(NZBx, self).__init__()
		self.queryURL = 'https://nzbx.co/api/search'
		self.baseURL = 'https://nzbx.co'
	# Perform a search using the given query string
	def search(self, queryString):
		# Get JSON
		urlParams = dict(
			q=queryString
		)
		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False)
		except Exception as e:
			print e
			return []
		
		data = http_result.json()
			
		parsed_data = []
		for i in xrange(len(data)):
			d1 = {
				'title': data[i]['name'],
				'poster': data[i]['fromname'],
				'size': data[i]['size'],
				'url': data[i]['nzb'],
				'filelist_preview': '',
				'group': data[i]['groupid'],
				'posting_date_timestamp': int(data[i]['postdate']),
				'release_comments': '',
				'ignore':0,
				'provider':self.baseURL
			}

			parsed_data.append(d1)
		return parsed_data