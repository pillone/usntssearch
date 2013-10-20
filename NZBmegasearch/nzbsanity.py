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

from flask import  send_file
import logging
import tempfile
import beautifulsoup
from operator import itemgetter
from urllib2 import urlparse

log = logging.getLogger(__name__)



#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class GetNZBInfo:
 
	def __init__(self, conf, cgen, ds, wrp):
		self.cfg = conf
		self.cgen = cgen
		self.wrp = wrp

		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def process(self, args, parsedurl):
		
		
		if('data' not in args):
			return 0
			
		urls = args['data'].split('=====')
		
		nzbdata = []
		
		#~ download all
		for url in urls:
			if(len(url)):
				nzbdata.append(self.download_hook(url))
		
		#~ analyze all
		info_nzbdata = []
		count = 0
		for nzbi in nzbdata:
			info = self.getdetailednzbinfo(nzbi['content'])
			info['id'] = count
			info_nzbdata.append(info)
			count = count +1
		
		#~ rank all
		ranked = self.whatisbetter(info_nzbdata)
		if (len(ranked)):
			return self.sendto(nzbdata[ranked[0]['id']])
		return []

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
		
		fresponse.headers = datablob['headers']

		return fresponse	

		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def download_hook(self, downloadurl):
		resinfo = {}
		resinfo['headers']=[]
		resinfo['content']=[]
		try:
			if(len(downloadurl)):
				#~ print downloadurl
				#~ print '=============='
				myrq = downloadurl.replace("warp?", "")
				pulrlparse = dict(urlparse.parse_qsl(myrq))		
				
				#~ print pulrlparse
				res = self.wrp.beam(pulrlparse)	
				
				if('Location'   in res.headers):
					#~ for redirect
					geturl_rq = res.headers['Location']
					r = requests.get(geturl_rq)
					nzbname = 'nzbfromNZBmegasearcH'
					if('content-disposition' in r.headers):
						rheaders = r.headers['content-disposition']
						idxsfind = rheaders.find('=')
						if(idxsfind != -1):
							nzbname = rheaders[idxsfind+1:len(rheaders)].replace('"','')
				
					resinfo['headers'] = res.headers	
					resinfo['content'] = r.content.encode('utf-8')
					return resinfo
					#~ with open(nzbname + '.nzb', 'wt') as fp:
						#~ fp.write(r.content)
							
			
				else:
					#~ for downloaded TO CHK
					nzbname = 'nzbfromNZBmegasearcH'
					if('content-disposition' in res.headers):
						rheaders = res.headers['content-disposition']
						idxsfind = rheaders.find('=')
						if(idxsfind != -1):
							nzbname = rheaders[idxsfind+1:len(rheaders)].replace('"','')

					resinfo['headers'] = res.headers	
					resinfo['content'] = res.data.encode('utf-8')
					return resinfo
					#~ with open(nzbname, 'wt') as fp:
						#~ fp.write(res.data)				


																		
		except Exception as e:
			log.info('Error downloading nzb: '+str(e))
			return []

		return []
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def getdetailednzbinfo(self, data):

		filesegs = []
		fileinfo  = {}
		fileinfo['pars'] = 0
		fileinfo['nofile'] = 0
		fileinfo['postid'] = []
		
		if(len(data)==0):
			return fileinfo
			
		soup = beautifulsoup.BeautifulSoup(data)
		paperdiv_title = soup.findAll('meta', {'type': 'name'})
		fileno = soup.findAll('file')
		
		for fno in fileno:	
			try:
				#~ print fno['subject']
				segs = fno.findAll('segments')		
				fsggs = 0
				parfile = 0
				#~ exclude nzb containing links to other nzb
				fileinfo['nofile'] = fileinfo['nofile'] + 1
				if (fno['subject'].find('.par2') != -1):
					fileinfo['pars'] = fileinfo['pars'] + 1
					parfile = 1
				for s in segs:	
					s_segs = s.findAll('segment')
					fsggs = fsggs + len(s_segs)
					postid = []
					#~ for s2 in s_segs:
						#~ curpost = ''.join(s2.findAll(text=True))
						#~ fileinfo['postid'].append(curpost)
						#~ postid.append(curpost)
				filesegs.append([fno['subject'],fsggs,postid,parfile])
			except:
				print "Error, could not parse NZB file"
				sys.exit()
		
		#~ print 'Num files: ' + str(fileinfo['nofile']) + ' of which repair files ' + str(fileinfo['pars'])
		return fileinfo

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def whatisbetter(self, nzbinfos):
		
		nzbinfos_sort = sorted(nzbinfos, key=itemgetter('nofile'), reverse=True) 
		
		#~ heuristic works just on pars, for now..
		#~ for nzbs in nzbinfos_sort:			
			#~ nzbs['postid'] = []
		
		return nzbinfos_sort
			

