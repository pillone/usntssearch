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


from flask import  Flask, render_template, redirect
import requests
import megasearch
import xml.etree.cElementTree as ET
import SearchModule
import datetime

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class SuggestionResponses:

	# Set up class variables
	def __init__(self, arguments, conf):
		self.config = conf
		self.args = arguments
		self.search_str = SearchModule.sanitize_strings(self.args['q'])
		self.timeout = self.config[0]['timeout']
		
		print self.search_str
		 
	def ask(self):

		movieinfo = self.imdb_titlemovieinfo()
		self.movie_bestmatch()
		return 'a'	

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
 
	def imdb_titlemovieinfo(self):	
		parsed_data = [{ 'rating_count':  '',
						'year': '',
						'imdb_url': '',
						'valid': 0}]
						
		url_imdb  = 'http://imdbapi.org/'
		urlParams = dict( title = self.search_str,
						type='json',
						plot='simple',
						episode=0,
						limit=50,
						yg=0,
						mt='none',
						lang='en-US',
						offset='',
						aka='simple',
						release='simple',
						business=0,
						tech=0)
		#~ loading
		try:
			http_result = requests.get(url=url_imdb , params=urlParams, verify=False, timeout=self.timeout)
		except Exception as e:
			print e
			return parsed_data
		
		try:
			datablob = http_result.json()
		except Exception as e:
			print e
			return parsed_data
		
		#~ no movie found
		if('code' in datablob):
			print 'ERROR IMDB:' + self.search_str

		for i in xrange(len(datablob)):
			data = datablob[i]
			toprocess = 1
			if('rating_count' not in data):
				toprocess = 0
			if('year' not in data):
				toprocess = 0
			if('title' not in data):
				toprocess = 0
			
			imdb_url = ''	
			if('imdb_url' in data):
				imdb_url = data['imdb_url']

			if (toprocess):
				p_data = { 'rating_count': data['rating_count'],
								'year': str(data['year']),
								'imdb_url': imdb_url,
								'valid': 1}
				
				parsed_data.append(p_data)

		return parsed_data
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
