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

from flask import Flask
from flask import request, Response
import os


import SearchModule
import megasearch
import config_settings
import miscdefs
from multiprocessing import Process

app = Flask(__name__)
SearchModule.loadSearchModules()
cfg,cgen = config_settings.read_conf()

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
#~ versioning check
ver_notify = miscdefs.chk_current_ver() 
print '~*~ ~*~ NZBMegasearcH (v. '+ str(ver_notify['curver']) + ') ~*~ ~*~'
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
#~ first time configuration check
first_time = 1
if os.path.exists("custom_params.ini"):
	first_time = 0
	print '>> NZBMegasearcH is configured'
else:	
	print '>> NZBMegasearcH will be configured'	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

@app.route('/s', methods=['GET'])
@miscdefs.requires_auth
def search():
	return megasearch.dosearch(request.args['q'], cfg, ver_notify)

@app.route('/config', methods=['GET','POST'])
@miscdefs.requires_auth
def config():
	return config_settings.config_read()
			
@app.route('/', methods=['GET','POST'])
@miscdefs.requires_auth
def main_index():
	global first_time,cfg,cgen
	if request.method == 'POST':
		config_settings.config_write(request.form)
		first_time = 0
	cfg,cgen = config_settings.read_conf()
	if first_time == 1:
		return config_settings.config_read()
	return megasearch.dosearch('', cfg, ver_notify)

@app.errorhandler(404)
def generic_error(error):
	return main_index()


if __name__ == "__main__":	
	if( ver_notify['chk'] == -1):
		ver_notify['chk'] = miscdefs.chk(ver_notify['curver'])
	chost = '0.0.0.0'
	cport = int(cgen['portno'])

	print '>> Running on port '	+ str(cport)
	app.run(host=chost,port=cport)

