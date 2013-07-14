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

# Search on NZBx.co
class ai_FTDworld(SearchModule):
	# Set up class variables
	def __init__(self):
		super(ai_FTDworld, self).__init__()
		self.name = 'FTDworld.net'
		self.typesrch = 'FTD'
		self.queryURL = 'http://ftdworld.net/api/index.php'
		self.baseURL = 'http://ftdworld.net'
		self.nzbdetailsBaseURL = 'http://ftdworld.net/spotinfo.php?id='
		self.nzbDownloadBaseURL = 'http://ftdworld.net/cgi-bin/nzbdown.pl?fileID='
		self.active = 0
		self.builtin = 1
		self.login = 1
		self.inapi = 0
		self.cookie = {}
		self.api_catsearch = 0
		self.cfg = {}
		
	def dologin(self, cfg):			
		loginurl='http://ftdworld.net/api/login.php'
		urlParams = dict(
			userlogin=cfg['login'],
			passlogin=cfg['pwd']
		)
		
		try:
			#~ short timeout
			http_result = requests.post(loginurl, data=urlParams, timeout=2)
			data = http_result.json()
			#~ print data
			self.cookie = {'FTDWSESSID' : http_result.cookies['FTDWSESSID']}
			return data['goodToGo']
		except Exception as e:
			print e
			return False			
		
	# Perform a search using the given query string
	def search(self, queryString, cfg):
		# Get JSON
		urlParams = dict(
			customQuery='usr',
			ctitle=queryString
		)
		
		timestamp_s = time.time()	
		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=cfg['timeout'])
		except Exception as e:
			print e
			log.critical(str(e))
			return []
		
		timestamp_e = time.time()
		log.info('TS ' + self.baseURL + " " + str(timestamp_e - timestamp_s))


		try:
			dataglob = http_result.json()
		except Exception as e:
			print e
			return []
		
		if('data' not in dataglob ):
			return []
		data = dataglob['data'];	
				
		parsed_data = []
		for i in xrange(len(data)):
			d1 = {  'title': data[i]['Title'],
							'poster': '',
							'size': int(data[i]['Size'])*1000000,
							'url': self.nzbDownloadBaseURL + data[i]['id'],
							'filelist_preview': '',
							'group': '',
							'categ': {'N/A':1},
							'posting_date_timestamp': int(data[i]['Created']),
							'release_comments': self.nzbdetailsBaseURL + data[i]['id'],
							'ignore':0,
							'provider':self.baseURL,
							'req_pwd':self.typesrch,
							'providertitle':self.name
							}
			parsed_data.append(d1)
		return parsed_data
