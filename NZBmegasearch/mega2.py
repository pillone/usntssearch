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
	app.run(debug=True)
