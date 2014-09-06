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

import json
from sets import Set
import decimal
import socket
import random
import string
import datetime
import requests
import time
from operator import itemgetter
from urllib2 import urlparse
from flask import render_template, Response
import SearchModule
import logging
import base64
import re
import os
import copy
from xmlrpclib import ServerProxy
import urllib2
from base64 import standard_b64encode

log = logging.getLogger(__name__)


def getdomainext( ):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(("8.8.8.8",80))
		sname = s.getsockname()[0]
		s.close()
	except Exception as e:
		print 'Network error, this is terrible. An active connection is needed for nzbmega to work: '+str(e)
		exit(0)
		
	return sname


def listpossiblesearchoptions():
	possibleopt = [ ['', 'No categ.',''],
							['1080p', 'HD 1080p',''],
							['720p','HD 720p',''],
							['BDRIP','SD BlurayRip',''],
							['DVDRIP','SD DVDRip',''],
							['DVDSCR','SD DVDScr',''],
							['CAM','SD CAM',''],
							['OSX','Mac OSX',''],
							['XBOX360','Xbox360',''],
							['PS3','PS3',''],
							['ANDROID','Android',''],
							['MOBI','Ebook (mobi)',''],
							['EPUB','Ebook (epub)',''],
							['FLAC','Audio FLAC',''] ]
	return possibleopt						
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class DoParallelSearch:
	
	def __init__(self, conf, cgen, ds, wrp):
	
		self.text2cat = [ ['tv','tv'],  
						  ['movies','movies'], 
						  ['movie','movies'], 
						  ['console','consoles'],
						  ['music','music'], 
						  ['mp3','music'],
						  ['flac','music'],
						  ['ebook','books'],
						  ['pc','apps'],
						  ['phone','pda'], 
						  ['games','games']];
								
		self.dirconf=  os.getenv('OPENSHIFT_DATA_DIR', '')
		self.results = []
		self.cfg = conf
		self.cgen = cgen
		self.svalid = 0
		self.svalid_speed = [0,0,0]
		self.qry_nologic = ''
		self.logic_items = []
		self.ds = ds			
		self.wrp = wrp
		self.sckname = self.getdomainandprotocol(self.cgen['general_ipaddress'])
		self.returncode = []
		self.returncode_fine = {}
		self.res_results = {}
		print '>> Base domain and protocol: ' + self.sckname
	
		if(self.cfg is not None):
			for i in xrange(len(self.cfg)):
				if(self.cfg[i]['valid'] != 0):
					self.svalid_speed[ self.cfg[i]['speed_class'] ] = 1 + self.svalid_speed[ self.cfg[i]['speed_class'] ]

		if(ds.cfg is not None):
			for i in xrange(len(self.ds.cfg)):
				if(self.ds.cfg[i]['valid'] != 0):
					self.svalid_speed[ self.ds.cfg[i]['speed_class'] ] = 1 + self.svalid_speed[ self.ds.cfg[i]['speed_class'] ]

				
		if( (self.cfg is not None) or (self.cgen is not None) ):
			self.svalid_speed[1] += self.svalid_speed[0]
			self.svalid_speed[2] += self.svalid_speed[1]
			self.svalid = self.svalid_speed[2]
			self.cfg_cpy = copy.deepcopy(self.cfg)
		
		self.logic_expr = re.compile("(?:^|\s)([-+])(\w+)")
		self.possibleopt = listpossiblesearchoptions()
		#~ self.searchopt = [ 	['Normal ['+str(self.svalid_speed[1]) + ']', 1,''],
							#~ ['Extensive ['+str(self.svalid_speed[2]) + ']', 2,'']]
		self.searchopt = [ 	[str(self.svalid_speed[1]) , 1,''],
							[str(self.svalid_speed[2]) , 2,'']]
		#~ correct the #providers
		self.get_num_manual_providers()
		self.searchopt_cpy = self.searchopt
		self.possibleopt_cpy = self.possibleopt		
		self.collect_info = []
		self.resultsraw = None


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


	def guesscategory(self, inputcat):
		inputcat_lower = inputcat.lower()
		for eachcat in self.text2cat:
			if(inputcat_lower.find(eachcat[0]) != -1):
				return eachcat[1]
		return ''		

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def cleancache(self):
		ntime = datetime.datetime.now()
		cinfon = []	
		for i in xrange(len(self.collect_info)):
			dt1 =  (ntime - datetime.datetime.fromtimestamp(self.collect_info[i]['tstamp']))
			dl = (dt1.days+1) * dt1.seconds
			#~ remove by overtime
			if(dl < self.cgen['max_cache_age']*60):
				cinfon.append(self.collect_info[i])
			else:
				print 'cache entry removed'	
		self.collect_info = cinfon		
			
	def chkforcache(self, qryenc, speedclass):
		rbuff = None
		if(self.cgen['cache_active'] == 1):
			#~ print len(self.collect_info)
			for i in xrange(len(self.collect_info)):
				if(self.collect_info[i]['searchstr'] == qryenc and self.collect_info[i]['speedclass'] == speedclass ):
					#~ print 'Cache hit id:' + str(i)
					rbuff = self.collect_info[i]['resultsraw']
					break
		return rbuff		
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def set_extraopt(self):
		if(self.cfg is not None):
			for conf in self.cfg :
				if ( (conf['extra_class'] >  1 ) and (conf['valid'])):
					conf['valid']  = 0
		
	def set_timeout_speedclass(self, speed_class_sel):
		if(self.cfg is not None):
			for conf in self.cfg:
				if ( (conf['speed_class'] <=  speed_class_sel) and (conf['valid'])):
					conf['timeout']  = self.cgen['timeout_class'][ speed_class_sel ]
				else:
					conf['valid']  = 0
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	
	def getdomainandprotocol(self, sgetsockname):
		if(len(self.dirconf)==0):
			if(len(sgetsockname)==0):
				sgetsockname = getdomainext()
			hprotocol = 'http://'
			if(self.cgen['general_https']):
				hprotocol = 'https://'
			sckname = hprotocol + sgetsockname +':'+ str(self.cgen['portno'])
		else:
			#~ only SSL encrypted allowed from openshift
			sckname = 'https://' + sgetsockname			
		return sckname

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 		

	def get_num_manual_providers(self):

		count = 0
		#~ 1 and 2 speed class
		for speed_class_sel in xrange(1,3):
			self.cfg = copy.deepcopy(self.cfg_cpy)
			self.ds.set_extraopt(speed_class_sel, 'manual')
			self.set_timeout_speedclass(speed_class_sel)
			self.set_extraopt()				
			self.searchopt[count][0] = 0
			if(self.cfg is not None):
				for conf in self.cfg :
					if ( (conf['speed_class'] <=  speed_class_sel) and (conf['valid'])):
						self.searchopt[count][0] = self.searchopt[count][0] + 1
			#~ manual + ds manual
			self.searchopt[count][0] = self.searchopt[count][0] + self.ds.get_dsnumproviders(speed_class_sel)
			count = count + 1
		
		#~ reset all the modification
		self.cfg = copy.deepcopy(self.cfg_cpy)
		self.ds.restore()
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 		
	
	def dosearch(self, args):
		#~ restore originals
		self.cfg = copy.deepcopy(self.cfg_cpy)
		
		if('q' not in args):
			self.results = []
			return self.results
		nuqry = args['q'] + ' ' + self.cgen['searchaddontxt']
		self.logic_items = self.logic_expr.findall(nuqry)
		self.qry_nologic = self.logic_expr.sub(" ",nuqry)
		if('selcat' in args):
			if(args['selcat'] != ""):
				self.qry_nologic += " " + args['selcat']

		#~ speed class
		speed_class_sel = 1	
		if('tm' in args):
			speed_class_sel = int(args['tm'])
		
		#~ speed class deepsearch
		self.ds.set_extraopt(speed_class_sel, 'manual')
		#~ speed class Nabbased	
		self.set_timeout_speedclass(speed_class_sel)
		#~ manual search Nabbased
		self.set_extraopt()				
		
				
		if( len(args['q']) == 0 ):
			if('selcat' in args):
				if(len(args['selcat'])==0):
					self.results = []
					return self.results
			else:
				self.results = []
				return self.results
		if(self.qry_nologic.replace(" ", "") == ""):
			self.results = []
			return self.results

		log.info('TYPE OF SEARCH: '+str(speed_class_sel))
						
		self.cleancache()
		#~ cache hit, no server report
		cachehit = True
		self.returncode_fine['code'] = 2
		self.resultsraw = self.chkforcache(self.wrp.chash64_encode(SearchModule.sanitize_strings(self.qry_nologic)), speed_class_sel)
		if( self.resultsraw is None):
			self.resultsraw = SearchModule.performSearch(self.qry_nologic, self.cfg, self.ds )
			cachehit = False
			
		if( self.cgen['smartsearch'] == 1):
			#~ smartsearch
			self.res_results = {}
			self.results = summary_results(self.resultsraw, self.qry_nologic, self.logic_items, self.res_results)
		else:
			#~ no cleaning just flatten in one array
			self.results = []
			self.res_results = {}
			for provid in xrange(len(self.resultsraw)):
				if (len(self.resultsraw[provid])):
					self.res_results[ str(self.resultsraw[provid][0]['providertitle']) ] = [len(self.resultsraw[provid]), 0]
			for provid in xrange(len(self.resultsraw)):
				for z in xrange(len(self.resultsraw[provid])):
					if (self.resultsraw[provid][z]['title'] != None):
						self.results.append(self.resultsraw[provid][z])

		#~ server status output
		if(cachehit == False):
			self.prepareretcode();

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
	def prepareretcode(self):
		self.returncode_fine = {}
		rcode = []
		rcode_resqty = []
		
		for cfg_t in self.cfg:
			if('retcode' in cfg_t):
				rcode.append(cfg_t['retcode'])

		for cfg_ds_base in self.ds.ds:
			if('retcode' in cfg_ds_base.cur_cfg):
				rcode.append(cfg_ds_base.cur_cfg['retcode'])
		
		codesuccess = 1
		rr_codesuccess = []
		nofail = 0
		cnt_rcode = 0
		for rr in rcode:
			rr_msg = ''
			rr_msg_complete = {}
			rr_msg_complete['numentry'] = 10000000
			if(rr[0] == 200):
				rr_msg = "<p class='text-green'>SUCCESS (200): "+rr[3]+" in "+'%.1f' % rr[2] + "s"				
				if(rr[3] in self.res_results):
					rr_msg = rr_msg + ", valid results: "+ str(self.res_results [rr[3]][1]) + "/" + str(self.res_results [rr[3]][0]) +"</p>"
					rr_msg_complete['numentry'] = self.res_results [rr[3]][1]
				else:
					rr_msg = rr_msg + ", no results </p>"	
					rr_msg_complete['numentry'] = 0
				rr_msg = rr_msg + "</p>"
			else:
				codesuccess = 0
				rr_msg = "<p class='text-red'>ERROR ("+str(rr[0])+"): "+rr[1] + ' (' + rr[3]+')</p>'
				nofail = nofail + 1
			rr_msg_complete['msg'] = rr_msg
			rr_codesuccess.append(rr_msg_complete)
			cnt_rcode = cnt_rcode + 1
				
		infofine = sorted(rr_codesuccess, key=itemgetter('numentry'), reverse=True) 
		self.returncode_fine['info'] = []
		for inffine in infofine:
			self.returncode_fine['info'].append(inffine['msg'])
		self.returncode_fine['code'] = codesuccess
		self.returncode_fine['summary'] = str(len(rr_codesuccess)) +  ' total ('+ str(nofail)+' failed, ' +str(len(rr_codesuccess)-nofail) +' successful)'
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
	def renderit(self,params):
		params['search_opt']=  copy.deepcopy(self.searchopt)
		search_def = 1
		if('tm' in params['args']):
			for j in xrange(len(params['search_opt'])):
				if(params['search_opt'][j][1] == int(params['args']['tm'])):
					search_def = j
		params['search_opt'][ search_def ][2] = 'checked'

		params['selectable_opt']=  copy.deepcopy(self.possibleopt)
		params['motd']=self.cgen['motd']
		if('selcat' in params['args']):
			for slctg in params['selectable_opt']:
				if(slctg[0] == params['args']['selcat']):
					slctg[2] = 'selected'
		return self.cleanUpResults(params)
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	
	def renderit_empty(self,params):	
		searchopt_local =  copy.deepcopy(self.searchopt)
		searchopt_local[0][2] = 'checked'

		possibleopt =  copy.deepcopy(self.possibleopt)
		for slctg in possibleopt:
			if(slctg[0] == self.cgen['search_default']):
				slctg[2] = 'selected'
		#~ params['ver']['chk'] = 1
		#~ params['ver']['os'] = 'openshift'
		
		return render_template('main_page.html', vr=params['ver'], nc=self.svalid, sugg = [], 
								cgen = self.cgen,
								trend_show = params['trend_show'], trend_movie = params['trend_movie'], debug_flag = params['debugflag'],
								large_server = self.cgen['large_server'],
								servercode_return = [],
								sstring  = "", selectable_opt = possibleopt, search_opt = searchopt_local,  motd = self.cgen['motd'], sid = params['sid'])
		
	
	
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def tonzbget(self, args, hname):
		
		if('data' not in args):
			return 0
			
		if ('nzbget_url' in self.cgen):
			if(len(self.cgen['nzbget_url'])):				
				rq_url = 'http://'+self.cgen['nzbget_user']+':'+self.cgen['nzbget_pwd']+'@'+self.cgen['nzbget_url'] + '/xmlrpc'
				print rq_url
				try:
					server = ServerProxy(rq_url)
				except Exception as e:
					print 'Error contacting NZBGET '+str(e)
					return 0

				try:
					myrq = args['data'].replace("warp?", "")
					pulrlparse = dict(urlparse.parse_qsl(myrq))					
					if('m' in args):
						pulrlparse['m'] = args['m']
						
					#~ print pulrlparse
					res = self.wrp.beam(pulrlparse)	
					#~ print res.headers
					
					if('Location'   in res.headers):
						#~ for redirect
						log.info('tonzbget: Warp is treated as 302 redirector')
						geturl_rq = res.headers['Location']
						r = requests.get(geturl_rq, verify=False)
						nzbname = 'nzbfromNZBmegasearcH'
						if('content-disposition' in r.headers):
							rheaders = r.headers['content-disposition']
							idxsfind = rheaders.find('=')
							if(idxsfind != -1):
								nzbname = rheaders[idxsfind+1:len(rheaders)].replace('"','')
						nzbcontent64=standard_b64encode(r.content)
						server.append(nzbname, '', False, nzbcontent64)
					else:
						#~ for downloaded						
						log.info('tonzbget: Warp gets full content')
						nzbname = 'nzbfromNZBmegasearcH'
						if('content-disposition' in res.headers):
							rheaders = res.headers['content-disposition']
							idxsfind = rheaders.find('=')
							if(idxsfind != -1):
								nzbname = rheaders[idxsfind+1:len(rheaders)].replace('"','')
						#~ print res.data
						nzbcontent64=standard_b64encode(res.data)
						server.append(nzbname, '', False, nzbcontent64)
		
																			
				except Exception as e:
					#~ print 'Error connecting server or downloading nzb '+str(e)
					log.info('Error connecting server or downloading nzb: '+str(e))
					return 0	

				return 1

				
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def tosab(self, args, hname):		
	
		if('data' not in args):
			return 0
	
		send2sab_exist = None
		if ('sabnzbd_url' in self.cgen):
			if(len(self.cgen['sabnzbd_url'])):
				send2sab_exist = self.sckname

				reportedurl = send2sab_exist+self.cgen['revproxy']+'/'+args['data']
				if(self.cgen['revproxy'].find('http') != -1):
					reportedurl = self.cgen['revproxy'] +'/'+args['data']
				
				urlq = self.cgen['sabnzbd_url']+ '/api'
				urlParams = dict(
									mode='addurl',
									name=reportedurl,
									apikey=self.cgen['sabnzbd_api'],
								)
				if('cat' in args):
					guessed_cat = self.guesscategory(args['cat'].encode('utf-8'))
					if(len(guessed_cat)):
						urlParams['cat']=guessed_cat

				#~ print urlParams
				#~ print urlq
				try:				
					http_result = requests.get(url=urlq, params=urlParams, verify=False, timeout=15)
				except Exception as e:
					log.error ('Error contacting SABNZBD '+str(e))
					return 0
				
				data = http_result.text
				
				#~ that's dirty but effective
				if(len(data) < 100):
					limitpos = data.find('ok')
					if(limitpos == -1):
						log.error ('ERROR: send url to SAB fails #1')
						return 0
				else:
					log.error ('ERROR: send url to SAB fails #2')
					return 0

				return 1


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def matchpredb(self, results, predb_info):		
		
		for i in xrange(len(results)):
			results[i]['predb']  = 0			
			results[i]['predb_lnk']  = ''
			
			if('title' in results[i]):
				#~ best match test
				for j in  xrange(len(predb_info)):
					#~ print predb_info[j]['title']
					#~ print results[i]['title']
					#~ print results[i]['title'].find(predb_info[j]['title'])
					#~ print '-----------------'
					if(results[i]['title'] == predb_info[j]['title']):
						results[i]['predb']  = 2
						results[i]['predb_lnk']  = 'http://www.derefer.me/?'+predb_info[j]['link']
					elif(results[i]['title'].lower().find(predb_info[j]['title'].lower()) != -1):
						results[i]['predb']  = 1
						results[i]['predb_lnk']  = 'http://www.derefer.me/?'+predb_info[j]['link']
			#~ print results[i]['predb']			
			
						
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def cleanUpResults(self, params):
		sugg_list = params['sugg']
		results = self.results
		svalid = self.svalid
		args = params['args']
		ver_notify = params['ver']
		niceResults = []
		existduplicates = 0

		#~ tries to match predb entries
		self.matchpredb(results, params['predb'])	

		#~ avoids GMT problems
		for i in xrange(len(results)):
			totdays = int ( (time.time() - results[i]['posting_date_timestamp'])/ (3600*24) )			
			if(totdays == 0):
				totdays = float ( (time.time() - results[i]['posting_date_timestamp'])/ (3600) )
				if(totdays < 0):
					totdays = -totdays
				totdays =  totdays/100
			results[i]['posting_date_timestamp_refined'] = float(totdays)
	
		#~ sorting		
		if 'order' not in args:
			results = sorted(results, key=itemgetter('posting_date_timestamp_refined'), reverse=False) 
		else:
			if	(args['order']=='t'):
				results = sorted(results, key=itemgetter('title'))
			if	(args['order']=='s'):
				results = sorted(results, key=itemgetter('size'), reverse=True)
			if	(args['order']=='p'):
				results = sorted(results, key=itemgetter('providertitle'))
			if	(args['order']=='d'):
				results = sorted(results, key=itemgetter('posting_date_timestamp_refined'), reverse=False) 
			if	(args['order']=='x'):
				results = sorted(results, key=itemgetter('predb'), reverse=True) 
			if	(args['order']=='c'):
				results = sorted(results, key=itemgetter('categ'), reverse=True) 
	
						
		#~ do nice 
		for i in xrange(len(results)):
			if(results[i]['posting_date_timestamp_refined'] > self.cgen['daysretention']):
				continue

			if(results[i]['ignore'] == 2):
				continue
				
			if(results[i]['ignore'] == 1): 
				existduplicates = 1

			# Convert sized to smallest SI unit (note that these are powers of 10, not powers of 2, i.e. OS X file sizes rather than Windows/Linux file sizes)
			szf = float(results[i]['size']/1000000.0)
			mgsz = ' MB '
			if (szf > 1000.0): 
				szf = szf /1000
				mgsz = ' GB '
			fsze1 = str(round(szf,1)) + mgsz
			
			if (results[i]['size'] == -1):
				fsze1 = 'N/A'
			totdays = results[i]['posting_date_timestamp_refined']
			if(totdays < 1):
				totdays = str(int(totdays*100)) + "h"	
			else:
				totdays = str(int(totdays)) + "d"

			category_str = '' 
			keynum = len(results[i]['categ'])
			keycount = 0
			for key in results[i]['categ'].keys():
				category_str = category_str + key
				keycount = keycount + 1
				if (keycount < 	keynum):
					 category_str =  category_str + ' - ' 
			if (results[i]['url'] is None):
				results[i]['url'] = ""
			
			qryforwarp=self.wrp.chash64_encode(results[i]['url'])
			if('req_pwd' in results[i]):
				qryforwarp += '&m='+ results[i]['req_pwd']
			niceResults.append({
				'id':i,
				'url':results[i]['url'],
				'url_encr':'warp?x='+qryforwarp,
				'title':results[i]['title'],
				'filesize':fsze1,
				'cat' : category_str.upper(),
				'age':totdays,
				'details':results[i]['release_comments'],
				'details_deref':'http://www.derefer.me/?'+results[i]['release_comments'],
				'providerurl':results[i]['provider'],
				'providertitle':results[i]['providertitle'],
				'ignore' : results[i]['ignore'],
				'predb':results[i]['predb'],
				'predb_lnk':results[i]['predb_lnk']
			})
		send2nzbget_exist = None
		if ('nzbget_url' in self.cgen):
			if(len(self.cgen['nzbget_url'])):
				send2nzbget_exist = self.sckname

		send2sab_exist = None
		if ('sabnzbd_url' in self.cgen):
			if(len(self.cgen['sabnzbd_url'])):
				send2sab_exist = self.sckname
		speed_class_sel = 1	
		if('tm' in args):
			speed_class_sel = int(args['tm'])
		
		#~ save for caching
		if(self.resultsraw is not None):
			if(self.cgen['cache_active'] == 1 and len(self.resultsraw)>0):
				if(len(self.collect_info) < self.cgen['max_cache_qty']):
					if(self.chkforcache(self.wrp.chash64_encode(SearchModule.sanitize_strings(self.qry_nologic)), speed_class_sel) is None):						
						collect_all = {}
						collect_all['searchstr'] = self.wrp.chash64_encode(SearchModule.sanitize_strings(self.qry_nologic))
						collect_all['tstamp'] =  time.time()
						collect_all['resultsraw'] = self.resultsraw		
						collect_all['speedclass'] = speed_class_sel		
						self.collect_info.append(collect_all)
						#~ print 'Result added to the cache list'
		#~ ~ ~ ~ ~ ~ ~ ~ ~ 
		scat = ''
		if('selcat' in params['args']):
			scat = params['args']['selcat']		

		return render_template('main_page.html',results=niceResults, exist=existduplicates, 
												vr=ver_notify, args=args, nc = svalid, sugg = sugg_list,
												speed_class_sel = speed_class_sel,
												send2sab_exist= send2sab_exist,
												send2nzbget_exist= send2nzbget_exist,
												cgen = self.cgen,
												trend_show = params['trend_show'], 
												trend_movie = params['trend_movie'], 
												debug_flag = params['debugflag'],
												sstring  = params['args']['q'],
												scat = scat,
												selectable_opt = params['selectable_opt'],
												search_opt =  params['search_opt'],
												sid = params['sid'],
												servercode_return = self.returncode_fine,
												large_server = self.cgen['large_server'],
												motd = params['motd'] )


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def summary_results(rawResults, strsearch, logic_items=[],results_stats={}):

	results =[]
	titles = []
	sptitle_collection =[]	
	
	#~ stats for each provider
	for provid in xrange(len(rawResults)):
		if (len(rawResults[provid])):
			results_stats[ str(rawResults[provid][0]['providertitle']) ] = [len(rawResults[provid]), 0]
		
	#~ all in one array
	for provid in xrange(len(rawResults)):
		for z in xrange(len(rawResults[provid])):
			if (rawResults[provid][z]['title'] != None):
				rawResults[provid][z]['title'] = SearchModule.sanitize_html(rawResults[provid][z]['title'])
				rawResults[provid][z]['provid'] = provid
				title = SearchModule.sanitize_strings(rawResults[provid][z]['title'])
				titles.append(title)
				sptitle_collection.append(Set(title.split(".")))
				results.append(rawResults[provid][z])
			
	strsearch1 = SearchModule.sanitize_strings(strsearch)
	strsearch1_collection = Set(strsearch1.split("."))	

	rcount = [0]*3
	for z in xrange(len(results)):
		findone = 0 
		results[z]['ignore'] = 0			
		intrs = strsearch1_collection.intersection(sptitle_collection[z])
		if ( len(intrs) ==  len(strsearch1_collection)):
			findone = 1
		else:
			results[z]['ignore'] = 2
			#~ relax the search ~ 0.45
			unmatched_terms_search = strsearch1_collection.difference(intrs)
			unmatched_count = 0
			for mst in unmatched_terms_search:
				my_list = [i for i in sptitle_collection[z] if i.find(mst) == 0]
				if(len(my_list)):
					unmatched_count = unmatched_count + 1		
				if(unmatched_count == len(unmatched_terms_search)):
					findone = 1
					results[z]['ignore'] = 0
				#~ print unmatched_terms_search
				#~ print unmatched_count
				#~ print unmatched_terms_search


		#~ print strsearch1_collection
		#~ print intrs
		#~ print findone 
		#~ print '------------------'

		if(findone and results[z]['ignore'] == 0):
			#~ print titles[z]
			for v in xrange(z+1,len(results)):
				if(titles[z] == titles[v]):
					sz1 = float(results[z]['size'])
					sz2 = float(results[v]['size'])
					if( abs(sz1-sz2) < 5000000):
						results[z]  ['ignore'] = 1
		#~ stats
		rcount[	results[z]  ['ignore'] ] += 1			

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	#~ logic params
	exclude_coll = Set([])
	include_coll = Set([])
	#~ print '*'+logic_items[0][1]+'*'
	for i in xrange(len(logic_items)):
		if(logic_items[i][0] == '-'):
			exclude_coll.add(logic_items[i][1])
		if(logic_items[i][0] == '+'):
			include_coll.add(logic_items[i][1])
	if(len(include_coll)):
		for z in xrange(len(results)):
			if(results[z]['ignore'] < 2):
				intrs_i = include_coll.intersection(sptitle_collection[z])
				if ( len(intrs_i) == 0 ):			
					results[z]['ignore'] = 2
	if(len(exclude_coll)):
		for z in xrange(len(results)):
			if(results[z]['ignore'] < 2):
				intrs_e = exclude_coll.intersection(sptitle_collection[z])
				if ( len(intrs_e) > 0 ):			
					results[z]['ignore'] = 2
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	
	mssg = 'Overall search stats: [' + strsearch1 + ']'+ ' [' + strsearch + '] ' + str(rcount[0]) + ' ' + str(rcount[1]) + ' ' + str(rcount[2])
	log.info (mssg)
	

	for z in xrange(len(results)):
		if(results[z]['ignore'] != 2):
			results_stats[ str(results[z]['providertitle']) ][1] = results_stats[ str(results[z]['providertitle']) ][1] + 1
	return results
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

