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
from operator import itemgetter

BEST_K_YEAR = 5
BEST_K_VOTES = 3

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class SuggestionResponses:

	# Set up class variables
	def __init__(self, arguments, conf):
		self.config = conf
		self.args = arguments
		self.search_str = SearchModule.sanitize_strings(self.args['q'])
		self.timeout = self.config[0]['timeout']
		
	def ask(self):

		movieinfo = self.imdb_titlemovieinfo()
		sugg_info_raw = self.movie_bestmatch(movieinfo)
		sugg_info = self.prepareforquery(sugg_info_raw)
		return sugg_info

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def prepareforquery(self, sugg_info_raw):	
		
		sugg_info = []
		for i in xrange(len(sugg_info_raw)):
			si = {'searchstr': SearchModule.sanitize_strings(sugg_info_raw[i]['title']) +  '.' + sugg_info_raw[i]['year'] ,
				  'prettytxt': sugg_info_raw[i]['title'] + ' (' + sugg_info_raw[i]['year'] + ')',
				  'imdb_url': sugg_info_raw[i]['imdb_url']}
			
			sugg_info.append(si)	  			
			print si
			print 'dcdddddddddddddddd'

		return sugg_info

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def movie_bestmatch(self, movieinfo):	
	
		#~ trivial heuristic on release date and popularity
		print movieinfo
		movieinfo_sorted = sorted(movieinfo, key=itemgetter('release_date'), reverse=True) 
		ntocheck = min(len(movieinfo_sorted), BEST_K_YEAR)
		movieinfo_sorted_final = sorted(movieinfo_sorted[0:ntocheck-1], key=itemgetter('rating_count'), reverse=True) 
		return movieinfo_sorted_final
		
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
 
	def imdb_titlemovieinfo(self):	
		parsed_data = []
						
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
			print 'ERROR IMDB [' + self.search_str + ']'
			return parsed_data

		for i in xrange(len(datablob)):
			data = datablob[i]
			toprocess = 1
			
			if ('release_date' not in data ):
				toprocess = 0
			if('year' not in data):
				toprocess = 0
			if('title' not in data):
				toprocess = 0
			
			imdb_url = ''	
			rating = 0
	
			if('imdb_url' in data):
				imdb_url = data['imdb_url']
			if('rating_count' in data ):
				rating = data['rating_count']

			if (toprocess):
				p_data = { 'title': data['title'],
							'rating_count': rating,
								'year': str(data['year']),
								'imdb_url': imdb_url,
								'release_date':data['release_date'],
								'valid': 1}
				
				#~ print p_data
				#~ print '~~~~~~~~~~'
				parsed_data.append(p_data)

		return parsed_data
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
