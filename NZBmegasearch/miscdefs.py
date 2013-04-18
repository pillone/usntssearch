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

import requests
import sys
from functools import wraps
from flask import Response,request
import config_settings
from flask import render_template
import os
import subprocess
import time
import logging
import SearchModule
import urlparse
import urllib
import datetime
import json
from operator import itemgetter

log = logging.getLogger(__name__)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def legal():
	return render_template('legal.html')


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def connectinfo():
	return render_template('connectinfo.html')
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def check_auth(username, password, cgen):
	if(username == cgen['general_usr'] and password == cgen['general_pwd']):
		return True
		

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
		cfg,cgen = config_settings.read_conf()		
		if(len(cgen['general_usr']) != 0):
			auth = request.authorization
			if not auth or not check_auth(auth.username, auth.password, cgen):
				return authenticate()
			return f(*args, **kwargs)
		else:
			return f(*args, **kwargs)
    return decorated


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class DownloadedStats:
	#~ megatransfer
	def __init__(self):
		import urlparse

		cfg,cgen = config_settings.read_conf('custom_params.ini')
		self.cgen = cgen
		self.logsdir = SearchModule.resource_path('logs/nzbmegasearch.log')
		self.scriptsdir = SearchModule.resource_path('get_stats.sh')
		self.cfg_urlidx = []
		self.excludeurls= ['http://ftdworld.net', 'https://nzbx.co']
		if(cfg is not None):
			self.config = cfg
			for i in xrange(len(self.config)):
				if(self.config[i]['builtin'] == 0):
					self.cfg_urlidx.append(i)
		
	def get_generalstats(self,args):
		log.info('Stats general have been requested')
		savedurl = []
		errstr = "WRONG KEY"
		if('key'  not in args):
			return errstr
		else:	
			if(args['key'] != self.cgen['stats_key']):
				return errstr
			daytochk = datetime.datetime.now().strftime("%Y-%m-%d") 
		if('d'  in args):
			daytochk=args['d']
		subprocess.call([self.scriptsdir + ' '+self.logsdir + ' ' + daytochk ], shell=True, executable="/bin/bash")
		
		stat_info = {}
		with open("/tmp/logstats_gen") as infile:
			for line in infile:
				value = line.split()
				#~ print value
				#~ print line
				if(value[0] not in stat_info):
					stat_info[value[0]] = []
				stat_info[value[0]].append( float(value[1]) )
			#~ print stat_info
			 
			stat_info_curated = []
			uidx = 0
			for key in stat_info.keys():
				meant = float(sum(stat_info[key]))/len(stat_info[key]) if len(stat_info[key]) > 0 else float('nan')
				mediant = sorted(stat_info[key])[len(stat_info[key])/2]
				stat_info_curated_t = {}
				stat_info_curated_t['succ_call'] = len(stat_info[key])
				stat_info_curated_t['name'] = key
				stat_info_curated_t['mean'] = meant
				stat_info_curated_t['median'] = mediant
				stat_info_curated_t['min'] = min(stat_info[key])
				stat_info_curated_t['max'] = max(stat_info[key])
				stat_info_curated.append(stat_info_curated_t)
				uidx += 1
		
			stat_info_curated = sorted(stat_info_curated, key=itemgetter('median'))
		return render_template('stats_gen.html',stat_cur=stat_info_curated)

	'''
	def get(self,args):
		log.info('Stats have been requested')
		savedurl = []
		errstr = "WRONG KEY"
		if('key'  not in args):
			return errstr
		else:	
			if(args['key'] != self.cgen['stats_key']):
				return errstr
			daytochk = datetime.datetime.now().strftime("%Y-%m-%d") 
			
		if('d'  in args):
			daytochk=args['d']
		subprocess.call([self.scriptsdir + ' '+self.logsdir + ' ' + daytochk ], shell=True, executable="/bin/bash")
		with open("/tmp/logstats") as infile:
			for line in infile:
				#~ print line
				parsedurlparam = dict(urlparse.parse_qsl(line))
				matched_idx = -1
				if( 'r' in parsedurlparam):
					for i in self.cfg_urlidx:
						sz_to_mtch = len(self.config[i]['url'])
						if(line[0:sz_to_mtch] == self.config[i]['url']):
							#~ print self.config[i]['url']
							matched_idx = i 
							break
					
					if(matched_idx != -1):
						parsedurlparam['r'] = self.config[i]['api']
						r1 = urlparse.urlsplit(line)
						uidx = line.find("&")
						if(uidx != -1):
							savedurl.append(line[0:uidx] + '&' + urllib.urlencode(parsedurlparam))
				else:
					matched_idx = -1
					for i in xrange(len(self.excludeurls)):
						sz_to_mtch = len(self.excludeurls[i])
						if(line[0:sz_to_mtch] == self.excludeurls[i]):
							matched_idx = 1
							break
					
					if(matched_idx == -1):	
						savedurl.append(line[:-1])
							
		return json.dumps(savedurl)
	'''		

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class ChkVersion:

	def __init__(self):
		self.ver_notify = ver_notify= { 'chk':-1, 
									'curver': -1}
		self.chk_local_ver()
		self.ver_notify['chk'] = self.chk_repos_ver()
	
	
	def chk_local_ver(self): 
		verify_str = '80801102808011028080110280801102'

		with open('vernum.num') as f:
			content = f.readlines()
		vals = content[0].split(' ')
		if(vals[0] == verify_str):
			self.ver_notify['curver'] = float(vals[1])
	
	def autoupdate(self): 
		#~ linux only, sorry win users
		if sys.platform.startswith('linux'):
			#~ print 'MISCDEFS: THIS LINE HAS TO BE REMOVED BEFORE DEPLOYMENT'
			mssg = '>> Running autoupdate on Linux platform' 
			print mssg
			log.info(mssg)
			subprocess.call(["git", "fetch"])
			subprocess.call(["git", "reset", "--hard", "origin/master"])
			pythonscr = sys.executable
			os.execl(pythonscr, pythonscr, * sys.argv)

	def chk_repos_ver(self): 
		verify_str = '80801102808011028080110280801102'
		url_versioning = 'https://raw.github.com/pillone/usntssearch/master/NZBmegasearch/vernum.num'
		
		#~ print 'MISCDEFS: TO REMOVE  LINE IN AUTOUPD  BEFORE DEPLOYMENT'
		try:
			http_result = requests.get(url=url_versioning, verify=False)
			#~ print http_result.text
			vals = http_result.text.split(' ')
			cur_ver = float(vals[1])
			if(vals[0] != verify_str):
				return  -1

			if(self.ver_notify['curver'] < cur_ver):
				print '>> A newer version is available. User notification on.' 

				#~ in case of supported platforms this is never executed, but autoupdated
				self.autoupdate()
				return 1
			else:
				if(self.ver_notify['curver'] == cur_ver):
					print '>> This is the newest version available'
				return 0	

		except Exception as e:
			mssg = str(e)
			print mssg
			log.critical(mssg)
			return -1
