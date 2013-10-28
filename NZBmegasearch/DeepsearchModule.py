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


import re
import time
import tempfile
import datetime
import mechanize
import sys, logging
import cookielib
import beautifulsoup
import config_settings
from urllib2 import urlparse
import socket
import locale
import copy
import megasearch

log = logging.getLogger(__name__)

def supportedengines ():
	supp = []
	supp.append( {'name':'NewsNab', 
				 'opts':DeepSearch_one.basics() } )
	supp.append( {'name':'GingaDaddy', 
				 'opts':DeepSearchGinga_one.basics() } )
				 
	return supp			 

class DeepSearch:

	def __init__(self, cur_cfg, cgen):
		self.cfg = None
		self.cgen = cgen
		self.ds = []
		count  = 0
		self.extraopts = supportedengines()
		
		if(cur_cfg is not None):
			self.cfg = copy.deepcopy(cur_cfg)
			for cfg in cur_cfg:
				if(cfg['type'] == 'DS_GNG'):
					self.ds.append(DeepSearchGinga_one(cfg, cgen))
				else:	
					self.ds.append(DeepSearch_one(cfg, cgen))

				self.ds[count].typesrch = cfg['type'] + str(count)
				count = count + 1
				
			if(len(self.cfg) != len(self.ds)):
				print 'ERROR: Fatal error in deepsearch configuration ->' + str(len(self.cfg)) + '  ' + str(len(self.ds))
				exit(1)
			
	def get_validity(self):
		for i in xrange(len(self.ds)):
			self.ds[i].timeout = self.cgen['default_timeout']
			self.ds[i].cur_cfg['valid'] = self.cfg[i]['valid']
			
	def restore(self):
		for i in xrange(len(self.ds)):
			self.ds[i].timeout = self.cgen['default_timeout']
			self.ds[i].cur_cfg['valid'] = self.cfg[i]['valid']

	def get_dsnumproviders(self, rq_speed_class):
		count = 0
		for i in xrange(len(self.ds)):
			if ( (self.ds[i].cur_cfg['speed_class'] <=  rq_speed_class) and (self.ds[i].cur_cfg['valid'])):
				count = count + 1
		return count		
				
	def set_extraopt(self, rq_speed_class, searchmode):
		self.restore()

		#~ timeout
		if(rq_speed_class is not None):
			for i in xrange(len(self.ds)):
				if ( (self.ds[i].cur_cfg['speed_class'] <=  rq_speed_class) and (self.ds[i].cur_cfg['valid'])):
					self.ds[i].timeout = self.cgen['timeout_class'][  rq_speed_class  ]
				else:
					self.ds[i].cur_cfg['valid']  = 0
		#~ extramode
		if(searchmode is not None):
			for i in xrange(len(self.ds)):
				if(searchmode == 'manual'):
					if ( (self.ds[i].cur_cfg['extra_class'] >  1) and (self.ds[i].cur_cfg['valid'])):
						self.ds[i].cur_cfg['valid']  = 0
				elif(searchmode == 'api'):
					if ( (self.ds[i].cur_cfg['extra_class'] ==  1)  and (self.ds[i].cur_cfg['valid'])):
						self.ds[i].cur_cfg['valid']  = 0

	#~ def set_timeout_speedclass(self, rq_speed_class):
		#~ self.restore()
		#~ for i in xrange(len(self.ds)):
			#~ if ( (self.ds[i].cur_cfg['speed_class'] <=  rq_speed_class) and (self.ds[i].cur_cfg['valid'])):
				#~ self.ds[i].timeout = self.cgen['timeout_class'][  rq_speed_class  ]
			#~ else:
				#~ self.ds[i].cur_cfg['valid']  = 0


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 	

class DeepSearch_one:
	
	def __init__(self, cur_cfg, cgen):
		self.definedcat = megasearch.listpossiblesearchoptions()
		self.br = mechanize.Browser(factory=mechanize.RobustFactory())
		self.cj = cookielib.LWPCookieJar()
		self.br.set_cookiejar(self.cj)
		self.br.set_handle_equiv(True)
		self.br.set_handle_redirect(False)
		self.br.set_handle_referer(True)
		self.br.set_handle_robots(False)
		self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
		self.cur_cfg = cur_cfg		
		self.timeout = cgen['default_timeout']
		self.baseURL = self.cur_cfg['url']
		#~ print self.cur_cfg['url']
		humanprovider = urlparse.urlparse(self.baseURL).hostname			
		self.name = humanprovider.replace("www.", "")
		self.basic_sz = 1024*1024
		#~ self.dologin()
		self.typesrch = 'DSNINIT'
		self.default_retcode=[200, 'Ok', 0, self.name]

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	@classmethod
	def basics(self):
		self.builtin = 0
		self.active = 0
		self.login = 1
		
		opts = {'builtin':self.builtin,
				'active':self.active,
				'typesrch': 'DSN',
				'login':self.login}
		return opts
		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def reset_cookies(self):
		self.cj = cookielib.LWPCookieJar()
		self.br.set_cookiejar(self.cj)
		log.info("Reset cookies")
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def mech_error_generic (self, e):
		if(str(e).lower().find("errno 111") != -1):
			#~ print "Wrong url or site down " + ' ' + self.baseURL
			log.warning("Wrong url or site down "  + self.baseURL)
			self.cur_cfg['retcode'] = [700, 'Server responded in unexpected format', self.timeout, self.name]
			return 111
		if(str(e).lower().find("timed out") != -1):
			#~ print "Too much time to respond "  + ' ' + self.baseURL
			log.warning("Too much time to respond - "  + self.baseURL)
			self.cur_cfg['retcode'] = [600, 'Server timeout', self.timeout, self.name]			
			return 500
		if(str(e).lower().find("http error 302") != -1):
			log.warning("Fetched exception login: " + str(e) + ' - ' + self.baseURL)
			self.cur_cfg['retcode'] = [100, 'Incorrect user credentials', self.timeout, self.name]			
			return 302
		#~ print "Fetched exception: "  + self.baseURL + ' ' + str(e)
		log.warning("Fetched exception: "  + self.baseURL + ' - ' + str(e))
		self.cur_cfg['retcode'] = [400, 'Generic server error', self.timeout, self.name]
		
		return 440


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def chkcookie(self):
		cexp = True
		for cookie in self.br._ua_handlers['_cookies'].cookiejar:
			#~ print self.br._ua_handlers['_cookies'].cookiejar
			if( cookie.is_expired() ) :
				cexp = False
		#~ print len(self.br._ua_handlers['_cookies'].cookiejar)		
		if(len(self.br._ua_handlers['_cookies'].cookiejar) == 0):
			cexp = False
		return cexp

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 	
	def dologin(self):
				
		socket.setdefaulttimeout(self.timeout)
		if	( self.chkcookie() == True):
			return True
		mainurl = self.cur_cfg['url']
		loginurl = mainurl + "/login"

		#~ print "Logging in: " + mainurl
		log.info("Logging in: " + mainurl)

		try:
			socket.setdefaulttimeout(self.timeout)
			self.br.open(loginurl)
		except Exception as e:
			#~ print str(e)
			self.mech_error_generic(e)
			return False
		
		formcount=0
		formfound=False
		for frm in self.br.forms():  
			#~ print frm.action
			if (frm.action.find("login") != -1):
				formfound = True
				break
			formcount=formcount+1
				
		if(	formfound == False):
			return False
		self.br.select_form(nr=formcount)
		self.br["username"] = self.cur_cfg['user']
		self.br["password"] = self.cur_cfg['pwd']
		try:
			response2 = self.br.submit()
		except Exception as e:

			if(str(e).lower().find("timed out") != -1):
				log.warning("Too much time to respond - "  + self.baseURL)
				self.cur_cfg['retcode'] = [600, 'Server timeout', self.timeout, self.name]			
				#~ print "Down or timeout"
				return False
			if(str(e).lower().find("http error 302") == -1):
				#~ print "Fetched exception login: " + str(e) 	
				#~ print str(e).find("HTTP Error 302")
				log.warning("Fetched server error: " + str(e) + ' - ' + self.baseURL)
				self.cur_cfg['retcode'] = [400, 'Generic server error', self.timeout, self.name]
				return False
				
 
		return True		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	
	def get_profile_info(self):
		socket.setdefaulttimeout(self.timeout)
		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return []

		loginurl = self.cur_cfg['url'] + "/profile"
		try:
			socket.setdefaulttimeout(self.timeout)
			res = self.br.open(loginurl)
		except Exception as e:
			eret = self.mech_error_generic(e)
			if(eret == 302):
				self.reset_cookies()
			return []

		data = res.get_data()  
		soup = beautifulsoup.BeautifulSoup(data)

		info = {}
		for row in soup.findAll("tr"):
			data = {}
			#~ print row
			#~ print '--------'
			allTHs = row.findAll("th")
			for x in range(len(allTHs)):
				str_lowcase = str(allTHs[x]).lower()
				if(str_lowcase.find('api hits today') > -1):
					allTD = row.findAll("td")
					if(len(allTD)):
						info['api_hits'] = ''.join(allTD[0].findAll(text=True))
						
				if(str_lowcase.find('grabs today') > -1):	
					allTD = row.findAll("td")
					if(len(allTD)):
						info['grabs_today'] =  ''.join(allTD[0].findAll(text=True))
				if(str_lowcase.find('grabs total') > -1 or str_lowcase.find('grabs') > -1):	
					allTD = row.findAll("td")
					if(len(allTD)):
						info['grabs_total'] =  ''.join(allTD[0].findAll(text=True))

		#~ print info		
		return info

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					
	def download(self, urlname):
		socket.setdefaulttimeout(self.timeout)

		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return ''
		try:
			#~ print urlname
			res = self.br.open(urlname)
			return res
		except Exception as e:
			self.mech_error_generic(e)
			return ''

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					

	def search_cat(self, dic_searchopt):
		return self.search_raw("/browse?t=",dic_searchopt['cat'])
		
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					

	def search(self, srchstr):
		return self.search_raw("/search/", srchstr)
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					

	def search_raw(self, pagestr, srchstr):
		if(self.cur_cfg['valid'] == 0):
			return []
		
		socket.setdefaulttimeout(self.timeout)
		
		#~ WIN: it seems to have issue in win32
		# locale.setlocale( locale.LC_ALL, 'en_US.utf8' )
		
		self.cur_cfg['retcode']  = self.default_retcode

		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return []
		mainurl = self.cur_cfg['url']
		loginurl = mainurl + pagestr+srchstr
		timestamp_s = time.time()	
		try:
			socket.setdefaulttimeout(self.timeout)
			res = self.br.open(loginurl)
		except Exception as e:
			eret = self.mech_error_generic(e)
			if(eret == 302):
				self.reset_cookies()
			return []	
		data = res.get_data()  
		timestamp_e = time.time()
		log.info('TS ' + mainurl + " " + str(timestamp_e - timestamp_s))
		self.cur_cfg['retcode'][2]  = timestamp_e - timestamp_s
		
		soup = beautifulsoup.BeautifulSoup(data)

	#~ def searchDBG(self, srchstr):
		#~ handler = open('tmp/tater.html').read()
		#~ soup = BeautifulSoup (handler)
		
		parsed_data = []
		titles = soup.findAll('a', {'class': 'title'})
		nzburls = soup.findAll('a', {'title': 'Download Nzb'})
		tstamp_raw = soup.findAll('td', {'class': 'less mid'})
		rdetails = soup.findAll('a', {'title': 'View details'})
		sz_raw = soup.findAll('td', {'class': 'less right'})
		catname_raw = soup.findAll('td', {'class': 'less'})

		catname = []
		for catn in catname_raw:
			catcont = catn.findAll(text=True)
			for catn1 in catcont:
				catcont_idx = catn1.find('">')
				if( catcont_idx != -1):
					catname.append(catn1[catcont_idx+2:len(catn1)].replace('>','-').capitalize())

		bytesize = []
		for sz1 in sz_raw:
			#~ rawline = str(sz1).split()
			for sz2 in sz1.findAll(text=True):
				sz2s =  sz2.split()

				if(len(sz2s) == 2):
					#~ print sz2s[1].lower()
					if (sz2s[1].lower() == 'mb' ):
						bytesize.append(int(self.basic_sz * float(sz2s[0].replace(',', '')) ))
					if (sz2s[1].lower() == 'gb' ):
						bytesize.append(int(self.basic_sz * float(sz2s[0].replace(',', '')) * 1024))
		#~ print bytesize

		#~ 2010-05-08 18:53:09
		tstamp = []
		for tt in tstamp_raw:
			for tt2 in tt.attrs:
				#~ print tt2[1]
				if('title' in tt2):
					#~ print tt2[1]
					tstamp.append( time.mktime(datetime.datetime.strptime(tt2[1], "%Y-%m-%d %H:%M:%S").timetuple()) )
					break;

		#~ deep debug
		#~ print 'tit' + str(len(titles))
		#~ print 'tst' + str(len(tstamp)	)	
		#~ print 'url' + str(len(nzburls))
		#~ print 'det' + str(len(rdetails))
		#~ print 'sz' + str(len(bytesize))
		#~ print 'cat' + str(len(catname))
		
		skipts = 1
		if(len(titles)):
			if(len(tstamp) % len(titles) == 0):
				skipts = len(tstamp) / len(titles)
				if(skipts < 1):
					return []
			
		if(len(titles) != len(nzburls)):
			return []
		#~ if(len(titles) != len(tstamp)):
			#~ return []
		if(len(titles) != len(rdetails)):
			return []
		if(len(titles) != len(bytesize)):
			return []
		
		for i in xrange(len(titles)):
			category_found= {}

			if(len(catname) == len(titles)):
				category_found[catname[i]] = 1
			else:	
				category_found['N/A'] = 1

			d1 = {
				'title': ''.join(titles[i].findAll(text=True)),
				'poster': 'poster',
				'size': bytesize[i],
				'url': self.baseURL + '/' + nzburls[i]['href'],
				'filelist_preview': '',
				'group': 'N/A',
				'posting_date_timestamp': tstamp[i*skipts],
				'release_comments': self.baseURL  + rdetails[i]['href'],
				'categ':category_found,
				'ignore':0,
				'req_pwd':self.typesrch,
				'provider':self.baseURL,
				'providertitle':self.name
			}
			#~ print d1
			parsed_data.append(d1)
		
		
		return parsed_data

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 	
class DeepSearchGinga_one(DeepSearch_one):


	def __init__(self, cur_cfg, cgen):
		DeepSearch_one.__init__(self, cur_cfg, cgen)
				
	#~ just to have access to basic vars
	@classmethod
	def basics(self):
		self.builtin = 1		
		self.speed_cl = 2
		self.extra_cl = 0
		self.active = 0
		self.login = 1
		self.basicurl = 'https://www.gingadaddy.com'
		
		opts = {'builtin':self.builtin,
				'active':self.active,
				'typesrch': 'DS_GNG',
				'speed_cl':self.speed_cl,
				'extra_cl':self.extra_cl,
				'url':self.basicurl,
				'login':self.login}
		return opts
		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 	
	def dologin(self):
				
		socket.setdefaulttimeout(self.timeout)
		if	( self.chkcookie() == True):
			return True
		mainurl = self.cur_cfg['url']
		#~ loginurl = mainurl + "/index.php"
		#~ more robust
		loginurl = mainurl + "/index.php"
		
		#~ print "Logging in: " + mainurl
		#~ log.info("Logging in: " + mainurl)

		
		try:
			socket.setdefaulttimeout(self.timeout)
			self.br.open(loginurl)
			#~ print loginurl			
		except Exception as e:
			print str(e)
			self.mech_error_generic(e)
			return False
		
		formcount=0
		formfound=False
		for frm in self.br.forms():  
			#~ print frm.action
			if (frm.action.find("login2") != -1):
				formfound = True
				break
			formcount=formcount+1
			
		if(	formfound == False):
			return False
			
		self.br.select_form(nr=formcount)
		self.br["user"] = self.cur_cfg['user']
		self.br["passwrd"] = self.cur_cfg['pwd']
		try:
			response2 = self.br.submit()
		except Exception as e:
			if(str(e).find("timed out") != -1):
				log.critical("Gingadaddy: down or timeout");
				return False
			if(str(e).find("HTTP Error 302") == -1):
				log.critical("Gingadaddy: Fetched exception login: " + str(e))
				return False
				
		return True		
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					
	def search_cat(self, dic_searchopt):
		#~ b=1&multicat%5B%5D=66&multicat%5B%5D=67&multicat%5B%5D=75
		#~ todo: mapping from nab cats to ginga cat not implemented
		return []

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 					
	
	def search(self, srchstr):
		if(self.cur_cfg['valid'] == 0):
			return []
		
		socket.setdefaulttimeout(self.timeout)

		self.cur_cfg['retcode']  = self.default_retcode
		if	(self.chkcookie() == False):
			if(self.dologin() == False):
				return []
						
		mainurl = self.cur_cfg['url']
		
		#~ category must have asterisk, it messes up the search
		srchstrnu = srchstr.split('.')
		
		for defcats in self.definedcat:
			if(defcats[0] == srchstrnu[-1]):
				srchstrnu[-1] = '*'+srchstrnu[-1]
				srchstr = ".".join(srchstrnu)

		loginurl = mainurl + '/nzbbrowse.php?b=2&st=1&c=0&g=0&sr=2&o=0&k='+srchstr
		timestamp_s = time.time()	

		try:
			socket.setdefaulttimeout(self.timeout)
			res = self.br.open(loginurl)
		except Exception as e:
			self.mech_error_generic(e)
			eret = self.mech_error_generic(e)
			if(eret == 302):
				self.reset_cookies()
			return []	

		data = res.get_data()  
		timestamp_e = time.time()
		log.info('TS ' + mainurl + " " + str(timestamp_e - timestamp_s))
		self.cur_cfg['retcode'][2]  = timestamp_e - timestamp_s

		#~ def searchDBG(self, srchstr):
		#~ handler = open('test.html').read()
		soup = beautifulsoup.BeautifulSoup(data)

		parsed_data = []
		titlesdiv = soup.findAll('div', {'class': 'pstnam'})
		nzburlsdiv = soup.findAll('div', {'class': 'dlnzb'})
		tstampdiv = soup.findAll('div', {'class': 'pstdat'})
		szdiv =  soup.findAll('abbr', {'title': 'Total size of articles'})
		catdiv =  soup.findAll('a', {'class': 'catimg'})

		titles = []
		rdetails = []
		nzburls = []
		tstamp = []
		bytesize = []
		categr = []
		
		for tl in catdiv:
			fall_tt = tl['title'].find('Show all in: ')
			if(fall_tt != -1):
				categr.append(tl['title'][fall_tt+13:])
			else:
				categr=[]
				break

		for tl in titlesdiv:
			all_a = tl.findAll("a")
			titles.append(''.join(all_a[0].findAll(text=True)))
			rdetails.append(all_a[0]['href'][1:])

		for tl in nzburlsdiv:
			all_a = tl.findAll("a")
			nzburls.append(all_a[0]['href'][1:])

		#~ absolute day of posting
		for tl in tstampdiv:
			intage =  int(tl.findAll(text=True)[0].split()[0].split('.')[0])
			today = datetime.datetime.now()
			dd = datetime.timedelta(days=intage)
			earlier = today - dd
			tstamp.append(time.mktime(earlier.timetuple()))

		for sz1 in szdiv:
			for sz2 in sz1.findAll(text=True):
				sz2s =  sz2.split()
 				if(len(sz2s) == 2):
					if (sz2s[1].lower() == 'mb' ):
						bytesize.append( int(self.basic_sz * float(sz2s[0].replace(',', '')) ) )
					if (sz2s[1].lower() == 'gb' ):
						bytesize.append( int(self.basic_sz * float(sz2s[0].replace(',', '')) * 1024) )
 
		if(len(titles) != len(nzburls)):
			return []
		if(len(titles) != len(tstamp)):
			return []
		if(len(titles) != len(rdetails)):
			return []
		if(len(titles) != len(bytesize)):
			return []
		if(len(categr) != len(titles)):
			categr =  []

		for i in xrange(len(titles)):
			category_found= {}			
			if(len(categr)):
				category_found[categr[i]] = 1
			else:	
				category_found['N/A'] = 1

			d1 = {
				'title': titles[i],
				'poster': 'poster',
				'size': bytesize[i],
				'url': self.baseURL + nzburls[i],
				'filelist_preview': '',
				'group': 'N/A',
				'posting_date_timestamp': tstamp[i],
				'release_comments': self.baseURL + rdetails[i],
				'categ':category_found,
				'ignore':0,
				'req_pwd':self.typesrch,
				'provider':self.baseURL,
				'providertitle':self.name
			}
			#~ print d1
			parsed_data.append(d1)
		return parsed_data
		
		
