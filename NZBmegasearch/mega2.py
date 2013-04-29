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
from flask import Flask, request, Response, redirect, send_from_directory
import logging
import logging.handlers
import os
import sys
import threading
import SearchModule
import DeepsearchModule
from ApiModule import ApiResponses
from SuggestionModule import SuggestionResponses
from WarperModule import Warper
import megasearch
import config_settings
import miscdefs
import random
import time
from OpenSSL import SSL

DEBUGFLAG = True
SERVERSIDE = False

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
 	
def reload_all():
	print '>> Bootstrapping...'
	global cfgsets, sugg, ds, mega_parall, wrp, apiresp, auth
	cfgsets = config_settings.CfgSettings()	
	sugg = SuggestionResponses(cfgsets.cfg, cfgsets.cgen)
	ds = DeepsearchModule.DeepSearch(cfgsets.cfg_deep, cfgsets.cgen)
	mega_parall = megasearch.DoParallelSearch(cfgsets.cfg, cfgsets.cgen, ds)
	wrp = Warper (cfgsets.cgen, cfgsets.cfg, ds)
	apiresp = ApiResponses(cfgsets.cfg, wrp)
	auth = miscdefs.Auth(cfgsets.cgen)
		
motd = '\n\n~*~ ~*~ NZBMegasearcH ~*~ ~*~'
print motd

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

cver = miscdefs.ChkVersion() 
#~ cver.chk_local_sign()
#~ os.abort()
print '>> version: '+ str(cver.ver_notify['curver'])
cfgsets = config_settings.CfgSettings()
first_time = 0
reload_all()

if (cfgsets.cfg is None): 
	first_time = 1
	'>> It will be configured'	

logsdir = SearchModule.resource_path('logs/')
certdir = SearchModule.resource_path('certificates/')
logging.basicConfig(filename=logsdir+'nzbmegasearch.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
handler = logging.handlers.RotatingFileHandler(logsdir+'nzbmegasearch.log', maxBytes=cfgsets.cgen['log_size'], backupCount=cfgsets.cgen['log_backupcount'])
log.addHandler(handler)
log.info(motd)
templatedir = SearchModule.resource_path('templates')
app = Flask(__name__, template_folder=templatedir)	 

SearchModule.loadSearchModules()
if(DEBUGFLAG):
	cfgsets.cgen['general_trend'] = 0
	print 'MEGA2: DEBUGFLAG MUST BE SET TO FALSE BEFORE DEPLOYMENT'

#~ wait for login init
if(DEBUGFLAG == False and SERVERSIDE == True):
	random.seed()
	sleeptime = random.randrange(0, 10)
	log.info('Wait ' + str(sleeptime) + 's for initialization...')
	time.sleep(sleeptime)	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/poweroff')
def poweroff():
	os.abort()

@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
			
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/s', methods=['GET'])
@auth.requires_auth
def search():
	if(first_time):
		return (main_index)
	
	sugg.asktrend_allparallel()	
	#~ parallel suggestion and search
	if(DEBUGFLAG == False):
		t1 = threading.Thread(target=sugg.ask, args=(request.args,) )
	t2 = threading.Thread(target=mega_parall.dosearch, args=(request.args,)   )
	if(DEBUGFLAG == False):
		t1.start()
	t2.start()
	if(DEBUGFLAG == False):	
		t1.join()
	t2.join()

	params_dosearch = {'args': request.args, 
						'sugg': sugg.sugg_info, 
						'trend_movie': sugg.movie_trend, 
						'trend_show': sugg.show_trend, 
						'ver': cver.ver_notify,
						'wrp':wrp,
						'debugflag':DEBUGFLAG
						}
	return mega_parall.renderit(params_dosearch)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
@app.route('/config', methods=['GET','POST'])
@auth.requires_auth
def config():
	return cfgsets.edit_config()

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/warp', methods=['GET'])
def warpme():
	res = wrp.beam(request.args)
	
	if(res == -1):
		return main_index()
	else: 	
		return res

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
			
@app.route('/', methods=['GET','POST'])
@auth.requires_auth
def main_index():
	
	global first_time,cfg,cgen,mega_parall
	if request.method == 'POST':
		cfgsets.write(request.form)
		first_time = 0
		reload_all()

	if first_time == 1:
		return cfgsets.edit_config()

	sugg.asktrend_allparallel()
	params_dosearch = {'args': '', 
						'sugg': [], 
						'trend': [], 
						'trend_movie': sugg.movie_trend, 
						'trend_show': sugg.show_trend, 
						'ver': cver.ver_notify,
						'debugflag':DEBUGFLAG}
	return mega_parall.renderit_empty(params_dosearch)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/api', methods=['GET'])
def api():
	#~ print request.args
	return apiresp.dosearch(request.args)

@app.route('/connect', methods=['GET'])
@auth.requires_auth
def connect():
	return miscdefs.connectinfo()
 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~   

@app.errorhandler(404)
def generic_error(error):
	return main_index()

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~   
 

if __name__ == "__main__":	

	sugg.asktrend_allparallel()
	chost = '0.0.0.0'
	print '>> Running on port '	+ str(cfgsets.cgen['portno'])
	
	ctx = None
	
	if(cfgsets.cgen['general_https'] == 1):
		print '>> HTTPS security activated' 
		ctx = SSL.Context(SSL.SSLv23_METHOD)
		ctx.use_privatekey_file(certdir+'server.key')
		ctx.use_certificate_file(certdir+'server.crt')

	app.run(host=chost,port=cfgsets.cgen['portno'], debug = True, ssl_context=ctx)
