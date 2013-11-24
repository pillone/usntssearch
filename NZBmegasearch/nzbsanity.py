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

from flask import  Flask, Response, send_file
import requests
import sys
import re
import threading
import os
from WarperModule import Warper
import logging
import tempfile
import beautifulsoup
from operator import itemgetter
from urllib2 import urlparse

log = logging.getLogger(__name__)



#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class GetNZBInfo:
 
	def __init__(self, conf, cgen, ds, app):
		self.cfg = conf
		self.cgen = cgen
		self.ds = ds
		self.nzbdata = []
		self.collect_info = []
		self.app = app
		self.MAX_ALLOWED_CACHE = 10000000
		self.MAX_ALLOWED_CACHE_OVERALL_MEMSZ = 20
		
		self.wrp_localcpy = []

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def checkcache_makespace(self):		
		#~ crop to max qty
		if (len(self.collect_info) > self.MAX_ALLOWED_CACHE_OVERALL_MEMSZ):
			self.collect_info = self.collect_info[2:]
		
		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def checkcache(self, url):
		for i in xrange(len(self.collect_info)):
			if(self.collect_info[i]['url'] == url):
				if(os.path.exists(self.collect_info[i]['fname'])):
					return i
		return -1
		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
	def cleancache(self):
		ntime = datetime.datetime.now()
		cinfon = []	
		for i in xrange(len(self.collect_info)):
			dt1 =  (ntime - datetime.datetime.fromtimestamp(self.collect_info[i]['tstamp']))
			dl = (dt1.days+1) * dt1.seconds
			#~ remove by overtime
			if(dl < self.cgen['max_cache_age']*60):
				cinfon.append(self.collect_info[i])
		self.collect_info = cinfon		
			
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


	def process(self, data, parsedurl):
		
		self.nzbdata = []		
		urls = data.split('....')
		
		nzbdata = []

		tthr = []
		idx = 0
		self.wrp_localcpy = []
		for url in urls:
			if(len(url)):
				wrp = Warper (self.cgen, self.cfg, self.ds)
				self.wrp_localcpy.append(wrp)
				tthr.append( threading.Thread(target=self.download_hook, args=(url,idx) ) )
			idx += 1
		for t in tthr:
			t.start()
		for t in tthr:
			t.join()

		#~ analyze all
		info_nzbdata = []
		count = 0
		for nzbi in self.nzbdata:
			if(len(nzbi)):
				info = self.getdetailednzbinfo(nzbi['content'])
				info['url'] = nzbi['url']
				info['id'] = nzbi['id']
				info_nzbdata.append(info)
				count = count +1
		
		#~ rank all
		ranked = self.whatisbetter(info_nzbdata)
		
		return ranked

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def sendto(self, datablob):
		
		fcontent = datablob['content']
		f=tempfile.NamedTemporaryFile(delete=False)
		f.write(fcontent)
		f.close()

		fresponse = send_file(f.name, mimetype='application/x-nzb;', as_attachment=True, 
							 attachment_filename='yourmovie.nzb', add_etags=False, cache_timeout=None, conditional=False)

		try:
			os.remove(f.name)
		except Exception as e:
			print 'Cannot remove temporary NZB file' 
		
		if(len(datablob['headers'])):
			fresponse.headers['content-disposition'] = datablob['headers']
		return fresponse	

		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def download_hook(self, downloadurl, urlidx):
		resinfo = {}
		resinfo['headers']=[]
		resinfo['content']=[]
		resinfo['url']=''
		resinfo['id'] = urlidx
		
		#~ try cache hit
		ret = self.checkcache(downloadurl)
		if( ret != -1):
			resinfo = {}
			with open(self.collect_info[ret]['fname'], 'rt') as fp:
				resinfo['content'] = fp.read()
			resinfo['url'] = self.collect_info[ret]['url']
			resinfo['headers'] = self.collect_info[ret]['headers']
			#~ overwrites the old id with the new one
			resinfo['id'] = urlidx
			print 'Nzb analyzer: cache hit'
			self.nzbdata.append(resinfo)
			return resinfo
		#~ download it
		try:
			if(len(downloadurl)):
				resinfo['url']=downloadurl
				myrq = downloadurl.replace("warp?", "")
				pulrlparse = dict(urlparse.parse_qsl(myrq))		
				
				#~ print pulrlparse
				#~ create context for threaded download

				
				with self.app.test_request_context():
					res = self.wrp_localcpy[urlidx].beam(pulrlparse)	
					
				if( (res is None) or (hasattr(res, 'headers') == False) ):
					return resinfo	

				if('Location'   in res.headers):
					#~ for redirect
					geturl_rq = res.headers['Location']
					r = requests.get(geturl_rq, verify=False)
					nzbname = 'nzbfromNZBmegasearcH'
					if('content-disposition' in r.headers):
						rheaders = r.headers['content-disposition']
						resinfo['headers'] =  r.headers['content-disposition']
						idxsfind = rheaders.find('=')
						if(idxsfind != -1):
							nzbname = rheaders[idxsfind+1:len(rheaders)].replace('"','')
				
					resinfo['content'] =  r.content.encode('utf-8')

					self.nzbdata.append(resinfo)
					
					#~ saves it for caching
					#~ saves it for caching in case that filesize < 20M
					if(len(resinfo['content']) < self.MAX_ALLOWED_CACHE):
						self.checkcache_makespace()
						f = tempfile.NamedTemporaryFile(delete=False)					
						cached_info = {}
						cached_info['url']=resinfo['url']
						cached_info['headers']=resinfo['headers']
						cached_info['fname']=f.name
						f.write(resinfo['content'])
						f.close()
						self.collect_info.append(cached_info)
					return resinfo
							
			
				else:
					nzbname = 'nzbfromNZBmegasearcH'
					if('content-disposition' in res.headers):
						rheaders = res.headers['content-disposition']
						resinfo['headers'] =  rheaders
						idxsfind = rheaders.find('=')
						if(idxsfind != -1):
							nzbname = rheaders[idxsfind+1:len(rheaders)].replace('"','')

					resinfo['content'] = res.data.encode('utf-8')
					self.nzbdata.append(resinfo)

					#~ saves it for caching in case that filesize < 20M
					if(len(resinfo['content']) < self.MAX_ALLOWED_CACHE):
						self.checkcache_makespace()
						f = tempfile.NamedTemporaryFile(delete=False)					
						cached_info = {}					
						cached_info['url']=resinfo['url']
						cached_info['headers']=resinfo['headers']
						cached_info['fname']=f.name
						f.write(resinfo['content'])
						f.close()
						self.collect_info.append(cached_info)	

					return resinfo

																		
		except Exception as e:
			log.info('Error downloading nzb: '+str(e))
			return resinfo

		return resinfo
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def getdetailednzbinfo(self, data):

		filesegs = []
		fileinfo  = {}
		fileinfo['pars'] = 0
		fileinfo['rars'] = 0
		fileinfo['nfo'] = 0
		fileinfo['nofile'] = 0
		fileinfo['nbytes'] = 0
		fileinfo['postid'] = []
		
		if(len(data)==0):
			return fileinfo
			
		soup = beautifulsoup.BeautifulSoup(data)
		fileno = soup.findAll('file')
		
		for fno in fileno:	
			try:
				segs = fno.findAll('segments')		
				fsggs = 0
				parfile = 0
				#~ there is no rar or rarparts chk, many nzb contain just uncompr.files
				val_sample =  re.search(r"[\.\-]sample", fno['subject'], re.I)	
				if(	val_sample is not None):
					continue
				if (fno['subject'].find('.nfo') != -1):
					fileinfo['nfo'] = fileinfo['nfo'] + 1
				elif (fno['subject'].find('.par2') != -1):
					fileinfo['pars'] = fileinfo['pars'] + 1
					parfile = 1
				else:
					fileinfo['nofile'] = fileinfo['nofile'] + 1
					
				for s in segs:	
					s_segs = s.findAll('segment')
					fsggs = fsggs + len(s_segs)
					postid = []
					for s2 in s_segs:
						fileinfo['nbytes'] += int (s2['bytes'])
			except Exception as e:
				fileinfo['pars'] = 0
				fileinfo['rars'] = 0
				fileinfo['nfo'] = 0
				fileinfo['nofile'] = 0
				fileinfo['nbytes'] = 0
				fileinfo['postid'] = []

				log.critical("Error, could not parse NZB file")
				#~ sys.exit()
		
		fileinfo['nbytes'] = int(fileinfo['nbytes'] / (1024*1024))

		#~ print 'Num files: ' + str(fileinfo['nofile']) + ' of which repair files ' + str(fileinfo['pars'])
		return fileinfo

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def whatisbetter(self, nzbinfos):
		
		nzbinfos_sort = sorted(nzbinfos, key=itemgetter('pars'), reverse=True) 		
		#~ heuristic works just on pars, for now..
		
		return nzbinfos_sort
			

