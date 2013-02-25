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
import time
from operator import itemgetter
import threading

BEST_K_YEAR = 5
BEST_K_VOTES = 3
MAX_TRENDS = 50
MAX_CHAR_LEN = 22
MIN_REFRESHRATE_S = 1800

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class SuggestionResponses:

	# Set up class variables
	def __init__(self, conf, cgen):
		self.config = conf
		self.timeout = self.config[0]['timeout']
		self.movie_trend = []
		self.movie_trend_ts = 0
		self.show_trend = []
		self.show_trend_ts = 0
		self.sugg_info = []
		self.active_trend = 1
		if(cgen['general_trend'] == 0):
		 self.active_trend = 0

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
	def ask(self, arguments):
		self.args = arguments
		self.search_str = SearchModule.sanitize_strings(self.args['q'])
		movieinfo = self.imdb_titlemovieinfo()
		sugg_info_raw = self.movie_bestmatch(movieinfo)
		self.sugg_info = self.prepareforquery(sugg_info_raw)
		#~ return sugg_info

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def asktrend_allparallel(self):
		if(self.active_trend):
			t1 = threading.Thread(target=self.asktrend_movie)
			t2 = threading.Thread(target=self.asktrend_show)
			t1.start()
			t2.start()
			t1.join()
			t2.join()


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def asktrend_movie(self):

		dt1 =  (datetime.datetime.now() - datetime.datetime.fromtimestamp(self.movie_trend_ts)).seconds
		if(dt1 > MIN_REFRESHRATE_S):
			movieinfo_trend = self.get_trends_movie()
			sugg_trend_raw = self.movie_bestmatch(movieinfo_trend)
			self.movie_trend = self.prepareforquery(sugg_trend_raw)
			print datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ' MVT ' + str(len(self.movie_trend))
			
			if(len(self.movie_trend)):
				self.movie_trend_ts = time.time()
		#~ return sugg_trend


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
				
	def asktrend_show(self):		

		dt1 =  (datetime.datetime.now() - datetime.datetime.fromtimestamp(self.show_trend_ts)).seconds
		if(dt1 > MIN_REFRESHRATE_S):
			showinfo_trend = self.get_trends_show()
			show_trend_raw = self.show_bestmatch(showinfo_trend)
			self.show_trend = []
			for i in xrange(len(show_trend_raw)):
				lastepisode = self.get_show_lastepisode(show_trend_raw[i]['tvrage_id'])
				if(len(lastepisode)):
					self.show_trend =  self.prepareforquery_show(show_trend_raw[i], lastepisode, self.show_trend)
			print datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ' SHT ' + str(len(self.show_trend))
			
			if(len(self.show_trend)):			
				self.show_trend_ts = time.time()
		
		
		#~ return show_trend_fullinfo

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def prepareforquery_show(self, sugg_info_raw, lastepisode, sugg_info):	
		
		for i in xrange(len(lastepisode)):
			si = {'searchstr': SearchModule.sanitize_strings(sugg_info_raw['title']) 
								+ '.S%02d' % int(lastepisode[i]['season']) 
								+  '.E%02d' %  int(lastepisode[i]['ep']),
				  'prettytxt': sugg_info_raw['title'] +  ' S%02d ' %  int(lastepisode[i]['season']) 
								+ 'E%02d' %  int(lastepisode[i]['ep']),
				  'imdb_url': sugg_info_raw['tvdb_url']}
			sugg_info.append(si)
		
		return sugg_info 
				  

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def show_bestmatch(self, showinfo):	
	
		#~ trivial heuristic on popularity
		ntocheck = min(len(showinfo), BEST_K_YEAR)
		show_sorted = sorted(showinfo, key=itemgetter('rating_count'), reverse=True) 
		return show_sorted[0:ntocheck]


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def get_show_lastepisode(self, rid):
		parsed_data = []
		url_tvrage = 'http://services.tvrage.com/feeds/episode_list.php'
		urlParams = dict( sid=rid )			
		#~ print urlParams
		try:
			http_result = requests.get(url=url_tvrage, params=urlParams, verify=False, timeout=self.timeout)
		except Exception as e:
			print e
			return parsed_data
		
		data = http_result.text

		try:
			tree = ET.fromstring(data.encode('utf-8'))
		except Exception as e:
			print e
			return parsed_data

		#~ check airdate, check latest episode
		numseasons = int(tree.find("totalseasons").text)

		eps = []	
		for seas in tree.iter('Season'):
			if(int(seas.attrib['no']) >= numseasons-1):
				for episode in seas.iter('episode'):
					aird = episode.find('airdate')
					epnum = episode.find('seasonnum')
					if( (aird is not None) and (epnum is not None)):
						#~ print aird.text + ' ' + epnum.text
						#~ print datetime.datetime.strptime(aird.text, "%Y-%m-%d")
						epinfo = {'aired':aird.text, 
								  'ep': epnum.text,
								  'season': int(seas.attrib['no'])}
						eps.append(epinfo)
		
		#~ take last ep, or immediatly upcoming 0days
		#~ fixes offsets, lazy approx way of US episodes
		eps_sorted = sorted(eps, key=itemgetter('aired'), reverse=True) 		
		eps_sorted_sel = []
		nxtbest = -1
		for i in xrange(len(eps_sorted)):
			rd = (datetime.datetime.strptime(eps_sorted[i]['aired'], "%Y-%m-%d") - datetime.datetime.today()).days + 1
			if(rd <= 0):
				eps_sorted_sel.append(eps_sorted[i])
			if(rd < 0):
				break	

		#~ print eps_sorted_sel
		return eps_sorted_sel
		
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def get_trends_show(self):
		parsed_data = []
						
		url_imdb  = 'http://api.trakt.tv/shows/trending.json/34bd894ae9abade37a9fec36dd84896c'
		try:
			http_result = requests.get(url=url_imdb, verify=False, timeout=self.timeout)
		except Exception as e:
			print e
			return parsed_data
		
		try:
			data = http_result.json()
		except Exception as e:
			print e
			return parsed_data
		
		mxtrends = min(MAX_TRENDS, len(data))
		
		for i in xrange(mxtrends):
			toprocess = 1
			if(data[i]['title'] is None):
				toprocess = 0
			if(data[i]['tvdb_id'] is None ): 
				toprocess = 0
			if(data[i]['ratings']  is None ): 	
				toprocess = 0

			if(toprocess):
				p_data = { 'title': data[i]['title'],
							'year': str(data[i]['year']),
							'rating_count': data[i]['ratings']['votes'],
							'tvrage_id': data[i]['tvrage_id'],
							'tvdb_url': 'http://thetvdb.com/?tab=series&id='+data[i]['tvdb_id']}
				#~ print p_data				
				#~ print '------------------'
				parsed_data.append(p_data)				
			
		return parsed_data
							
	

		
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def get_trends_movie(self):
		parsed_data = []
						
		url_imdb  = 'http://api.trakt.tv/movies/trending.json/34bd894ae9abade37a9fec36dd84896c'
		try:
			http_result = requests.get(url=url_imdb, verify=False, timeout=self.timeout)
		except Exception as e:
			print e
			return parsed_data
		
		try:
			data = http_result.json()
		except Exception as e:
			print e
			return parsed_data
		
		mxtrends = min(MAX_TRENDS, len(data))
		
		for i in xrange(mxtrends):
			toprocess = 1
			if(data[i]['title'] is None):
				toprocess = 0
			if(data[i]['released'] is None):
				toprocess = 0
			if(data[i]['imdb_id'] is None ): 
				toprocess = 0
			if(data[i]['ratings']  is None ): 	
				toprocess = 0

			if(toprocess):
				p_data = { 'title': data[i]['title'],
							'year': str(data[i]['year']),
							'rating_count': data[i]['ratings']['votes'],
							'imdb_url': 'http://www.imdb.com/title/'+data[i]['imdb_id'],
							'release_date':data[i]['released']}
				#~ print p_data				
				#~ print '------------------'
				parsed_data.append(p_data)				
			
		return parsed_data
							
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~


	def prepareforquery(self, sugg_info_raw):	
		
		sugg_info = []
		for i in xrange(len(sugg_info_raw)):
			shorinfo = sugg_info_raw[i]['title']
			if (len(shorinfo) > MAX_CHAR_LEN):
				shorinfo = shorinfo[0:MAX_CHAR_LEN-2] + '..'
			si = {'searchstr': SearchModule.sanitize_strings(sugg_info_raw[i]['title']) +  '.' + sugg_info_raw[i]['year'] ,
				  'prettytxt': shorinfo + '('+ sugg_info_raw[i]['year'] + ')',
				  'imdb_url': sugg_info_raw[i]['imdb_url']}
			
			sugg_info.append(si)	  			
			#~ print si
			#~ print 'dcdddddddddddddddd'

		return sugg_info

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def movie_bestmatch(self, movieinfo):	
	
		#~ trivial heuristic on release date and popularity
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
