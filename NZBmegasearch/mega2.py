# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by pillone.
#~ 
#~ NZBmegasearch is free software: you can redistribute it and/or modify
#~ it under the terms of the GNU General Public License as published by
#~ the Free Software Foundation, either version 3 of the License, or
#~ (at your option) any later version.
#~ 
#~ Foobar is distributed in the hope that it will be useful,
#~ but WITHOUT ANY WARRANTY; without even the implied warranty of
#~ MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#~ GNU General Public License for more details.
#~ 
#~ You should have received a copy of the GNU General Public License
#~ along with NZBmegasearch.  If not, see <http://www.gnu.org/licenses/>.
# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    

import megasearch
import config_settings
from flask import Flask
from flask import request

app = Flask(__name__)
cfg = config_settings.read_conf()
	
@app.route('/s', methods=['GET'])
def search():
	cfg = config_settings.read_conf()
	return megasearch.dosearch(request.args.get('q'), cfg)

@app.route('/config', methods=['GET'])
def config():
	#~ if request.method == 'POST':
		#~ return config_settings.config_write(request.form)
	if request.method == 'GET':
		return config_settings.config_read()
			
@app.route('/', methods=['GET','POST'])
def main_index():
	if request.method == 'POST':
		config_settings.config_write(request.form)
	return megasearch.dosearch('', cfg)

@app.errorhandler(404)
def generic_error(error):
	return main_index()
	
if __name__ == "__main__":
	app.run(host='0.0.0.0')
