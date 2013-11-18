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
import base64
import DeepsearchModule
from functools import wraps
from flask import Response,request
import config_settings
from flask import render_template
import os
import subprocess
import datetime
import time
import logging
import SearchModule
import urlparse
import urllib
import datetime
import json
from operator import itemgetter

#~ max visualized
LOG_MAXLINES = 500
	
log = logging.getLogger(__name__)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def logviewer(logsdir):
	filename=logsdir+'nzbmegasearch.log'


	array1 = []
	count = 0
	for line in reversed(open(filename).readlines()):
		if(count > LOG_MAXLINES):
			break
		array1.append(line.decode('utf-8').rstrip())
		count = count + 1
    
    
	return(render_template('loginfo.html', loginfo =array1 ))


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def daemonize(logsdir):
	#~ full credits to SICKBEARD
	
	# Make a non-session-leader child process
	try:
		pid = os.fork()  # @UndefinedVariable - only available in UNIX
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

	os.setsid()  # @UndefinedVariable - only available in UNIX

	# Make sure I can read my own files and shut out others
	prev = os.umask(0)
	os.umask(prev and int('077', 8))

	# Make the child a session-leader by detaching from the terminal
	try:
		pid = os.fork()  # @UndefinedVariable - only available in UNIX
		if pid != 0:
			sys.exit(0)
	except OSError, e:
		raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

	dev_null = file('/dev/null', 'r')
	os.dup2(dev_null.fileno(), sys.stdin.fileno())
	log.info("Daemonized using PID " + str(pid))

	#~ LEGACY DAEMON LOGGING
	#~ silences console output
	#~ sys.stdout = open('tmpdl', 'wt')
	#~ logging.basicConfig(
	#~ level=logging.DEBUG,
	#~ format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
	#~ filename=logsdir+'nzbmegasearch_daemon.log',
	#~ filemode='a')
	#~ stdout_logger = logging.getLogger('STDOUT')
	#~ sl = StreamToLogger(stdout_logger, logging.INFO)
	#~ sys.stdout = sl
	#~ stderr_logger = logging.getLogger('STDERR')
	#~ sl = StreamToLogger(stderr_logger, logging.ERROR)
	#~ sys.stderr = sl


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


class StreamToLogger(object):
   """
   Fake file-like stream object that redirects writes to a logger instance.
   """
   def __init__(self, logger, log_level=logging.INFO):
      self.logger = logger
      self.log_level = log_level
      self.linebuf = ''
 
   def write(self, buf):
      for line in buf.rstrip().splitlines():
         self.logger.log(self.log_level, line.rstrip())

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

 
def connectinfo():
	return render_template('connectinfo.html')
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
class Auth:
	def __init__(self, cfgsetsp):
		#~ another instance to not use ptrs
		self.cfgsets = 	config_settings.CfgSettings()	
	
	def check_auth(self, username, password, mode):
		if(mode == 0):
			if(username == self.cfgsets.cgen['general_usr'] and password == self.cfgsets.cgen['general_pwd']):
				return True
		if(mode == 1):
			if(len(self.cfgsets.cgen['config_user']) != 0):
				if(username == self.cfgsets.cgen['config_user'] and password == self.cfgsets.cgen['config_pwd']):
					return True
			else:
				if(username == self.cfgsets.cgen['general_usr'] and password == self.cfgsets.cgen['general_pwd']):
					return True
		return False			
			
	def authenticate(self):
		"""Sends a 401 response that enables basic auth"""
		retres =  Response(
		'Could not verify your access level for that URL.\n'
		'You have to login with proper credentials', 401,
		{'WWW-Authenticate': 'Basic realm="Login Required"'})
		return retres
 

	def requires_auth(self, f):
		@wraps(f)
		def decorated(*args, **kwargs):
			self.cfgsets.refresh()
			if(len(self.cfgsets.cgen['general_usr']) != 0):
				auth = request.authorization
				if not auth or not self.check_auth(auth.username, auth.password,0):
					sret = self.authenticate()
					return sret
				return f(*args, **kwargs)
			else:
				return f(*args, **kwargs)
			return f(*args, **kwargs)		
		return decorated

	def requires_conf(self, f):
		@wraps(f)
		def decorated(*args, **kwargs):
			if(len(self.cfgsets.cgen['config_user']) != 0 or len(self.cfgsets.cgen['general_usr']) != 0):
				auth = request.authorization
				if not auth or not self.check_auth(auth.username, auth.password,1):
					return self.authenticate()
				return f(*args, **kwargs)
			else:
				return f(*args, **kwargs)
			return f(*args, **kwargs)		
		return decorated


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class DownloadedStats:
	#~ megatransfer
	def __init__(self):
		import urlparse

		cfgsets = config_settings.CfgSettings()
		
		self.cgen = cfgsets.cgen
		self.logsdir = SearchModule.resource_path('logs/nzbmegasearch.log')
		self.scriptsdir = SearchModule.resource_path('get_stats.sh')
		self.cfg_urlidx = []
		self.excludeurls= ['http://ftdworld.net', 'https://nzbx.co']
		if(cfgsets.cfg is not None):
			self.config = cfgsets.cfg
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


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class ChkServer:
	def __init__(self, cgen):
		self.cgen = cgen
		self.agent_headers = {	'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1' }	
		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	def check(self, args):
		ret = 0
		
		if(('hostname' in args) and ('type' in args)):
			
			# Perform the search using every module
			global globalResults
			if 'loadedModules' not in globals():
				SearchModule.loadSearchModules()


			#~ specials
			if(args['type'] == 'OMG'):
				ret = 1
				cfg_tmp = {'valid': 1,
					  'type': 'OMG',
					  'speed_class': 2,
					  'extra_class': 0,
					  'login': args['user'],
					  'pwd': args['pwd'],
					  'timeout':  self.cgen['timeout_class'][2],
					  'builtin': 1}
				for module in SearchModule.loadedModules:
					if( module.typesrch == 'OMG'):
						module.search('Ubuntu', cfg_tmp)
				print cfg_tmp['retcode']		
				if(cfg_tmp['retcode'][0] != 200):
					ret = 0
					

			#~ server based API			
			if(args['type'] == 'NAB'):			
				ret = 1
				cfg_tmp = {'url': args['hostname'],
					  'type': 'NAB',
					  'api': args['api'],
					  'speed_class': 2,
					  'extra_class': 0,
					  'valid':  1,
					  'timeout':  self.cgen['timeout_class'][2],
					  'builtin': 0 }				
				for module in SearchModule.loadedModules:
					if( module.typesrch == 'NAB'):
						module.search('Ubuntu', cfg_tmp)
				print cfg_tmp['retcode']		
				if(cfg_tmp['retcode'][0] != 200):
					ret = 0

			#~ server based WEB
			if(args['type'] == 'DSN' or args['type'] == 'DS_GNG'):
				
				cfg_deep_tmp = [{'url': args['hostname'],
					  'user':args['user'],
					  'pwd': args['pwd'],
					  'type': args['type'],
					  'speed_class': 2,
					  'extra_class': 0,
					  'valid': 1,
					  }]
				ds_tmp = DeepsearchModule.DeepSearch(cfg_deep_tmp, self.cgen)
				ret_bool = ds_tmp.ds[0].search('Ubuntu')
				if(ret_bool):
					ret = 1
				else:	
					ret = 0

		return ret
		
	

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
		
class ChkVersion:
 
	def __init__(self, debugflag=False):
		self.dirconf=  os.getenv('OPENSHIFT_DATA_DIR', '')
		self.dirconf_local = os.path.dirname(os.path.realpath(__file__))+'/'
		if getattr(sys, 'frozen', False):
			self.dirconf_local = os.path.dirname(sys.executable)+'/'

		self.ver_notify = { 'chk':-1, 
							'curver': -1,
							'os':-1}
		self.chk_update_ts = 0
		self.chk_update_refreshrate = 3600 * 4
		if(debugflag == False):
			self.chk_update()
	
	def chk_update(self):
		dt1 =  (datetime.datetime.now() - datetime.datetime.fromtimestamp(self.chk_update_ts))
		dl = (dt1.days+1) * dt1.seconds
		if(dl > self.chk_update_refreshrate):
			if (sys.platform.startswith('linux') and len(self.dirconf)==0):
				self.ver_notify['os'] = 'linux'
			else:
				self.ver_notify['os'] = 'other'

			if (len(self.dirconf)):
				self.ver_notify['os'] = 'openshift'

			print '>> Checking for updates...'
			self.chk_local_ver()
			self.ver_notify['chk'] = self.chk_repos_ver()
			self.chk_update_ts = time.time()
		
	
	def chk_local_ver(self): 
		verify_str = '80801102808011028080110280801102'
		
		usedir = self.dirconf_local
		if (len(self.dirconf)):
			usedir = self.dirconf
		with open(usedir+'vernum.num') as f:
			content = f.readlines()
		vals = content[0].split(' ')
		if(vals[0] == verify_str):
			self.ver_notify['curver'] = float(vals[1])
	
	def autoupdate(self): 
		#~ linux only, sorry win users
		if (sys.platform.startswith('linux') and len(self.dirconf)==0):
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
