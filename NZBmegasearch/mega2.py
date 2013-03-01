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

from flask import Flask
from flask import request, Response
import os
import threading
import SearchModule
from ApiModule import ApiResponses
from SuggestionModule import SuggestionResponses
import megasearch
import config_settings
import miscdefs
from multiprocessing import Process

DEBUGFLAG = False
templatedir = SearchModule.resource_path('templates')
app = Flask(__name__, template_folder=templatedir)
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
#~ versioning check
print '~*~ ~*~ NZBMegasearcH ~*~ ~*~'
cver = miscdefs.ChkVersion() 
print '>> version: '+ str(cver.ver_notify['curver'])

#~ startup
SearchModule.loadSearchModules()
cfg,cgen = config_settings.read_conf()

if(DEBUGFLAG):
	cgen['general_trend'] = 0
	print 'MEGA2: DEBUGFLAG MUST BE SET TO FALSE BEFORE DEPLOYMENT'

sugg = SuggestionResponses(cfg, cgen)
mega_parall = megasearch.DoParallelSearch(cfg)
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
#~ first time configuration check
first_time = 1
if os.path.exists("custom_params.ini"):
	first_time = 0
	print '>> NZBMegasearcH is configured'
else:	
	print '>> NZBMegasearcH will be configured'	

	 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/legal')
@miscdefs.requires_auth
def legal():
	return (miscdefs.legal())

	 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/s', methods=['GET'])
@miscdefs.requires_auth
def search():
	sugg.asktrend_allparallel()	
	#~ parallel suggestion and search
	t1 = threading.Thread(target=sugg.ask, args=(request.args,) )
	t2 = threading.Thread(target=mega_parall.dosearch, args=(request.args,)   )
	t1.start()
	t2.start()
	t1.join()
	t2.join()

	params_dosearch = {'args': request.args, 
						'sugg': sugg.sugg_info, 
						'configr': cfg,
						'trend_movie': sugg.movie_trend, 
						'trend_show': sugg.show_trend, 
						'ver': cver.ver_notify
						}
	return mega_parall.renderit(params_dosearch)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/config', methods=['GET','POST'])
@miscdefs.requires_auth
def config():
	return config_settings.config_read()

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
			
@app.route('/', methods=['GET','POST'])
@miscdefs.requires_auth
def main_index():
	global first_time,cfg,cgen,mega_parall
	if request.method == 'POST':
		config_settings.config_write(request.form)
		first_time = 0
		cfg,cgen = config_settings.read_conf()
		mega_parall = megasearch.DoParallelSearch(cfg)
	if first_time == 1:
		return config_settings.config_read()	
	
	sugg.asktrend_allparallel()
	params_dosearch = {'args': '', 
						'sugg': [], 
						'trend': [], 
						'configr': cfg,
						'trend_movie': sugg.movie_trend, 
						'trend_show': sugg.show_trend, 
						'ver': cver.ver_notify}
	return mega_parall.renderit_empty(params_dosearch)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/api', methods=['GET'])
def api():
	#~ print request.args
	api = ApiResponses(cfg, cver.ver_notify)
	return api.dosearch(request.args)

@app.route('/connect', methods=['GET'])
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
	cport = int(cgen['portno'])

	print '>> Running on port '	+ str(cport)
	app.run(host=chost,port=cport, debug = DEBUGFLAG)

