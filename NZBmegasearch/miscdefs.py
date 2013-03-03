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
