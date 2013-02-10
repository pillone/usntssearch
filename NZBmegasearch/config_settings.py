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

from flask import render_template
from ConfigParser import SafeConfigParser
import sys
import SearchModule

MAX_PROVIDER_NUMBER = 10


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def	write_conf(request_form):
	parser = SafeConfigParser()

	#~ custom
	counter = 1
	for i in xrange(MAX_PROVIDER_NUMBER):
		if (request_form.has_key('host%d' % i)  == True):
			if(request_form['host%d' % i].replace(" ", "")): 
				parser.add_section('search_provider%s' % counter)
				parser.set('search_provider%s' % counter, 'url',request_form['host%d' % i].replace(" ", ""))
				parser.set('search_provider%s' % counter, 'api',request_form['API%d' % i].replace(" ", ""))
				parser.set('search_provider%s' % counter, 'type', request_form['type%d' % i].replace(" ", ""))
				parser.set('search_provider%s' % counter, 'valid', '1')
				counter = counter + 1
	parser.add_section('general')
	parser.set('general', 'numserver', str(counter-1))

	
	counter2 = 1
	for i in xrange(MAX_PROVIDER_NUMBER):
		if (request_form.has_key('bi_host%d' % i)  == True):
			parser.add_section('bi_search_provider%s' % counter2)
			parser.set('bi_search_provider%s' % counter2, 'type', request_form['bi_host%d' % i].replace(" ", ""))
			if (request_form.has_key('bi_host%dactive' % i)  == True):
				parser.set('bi_search_provider%s' % counter2, 'valid', '1')
			else:
				parser.set('bi_search_provider%s' % counter2, 'valid', '0')
			
			if (request_form.has_key('bi_host%dlogin' % i)  == True):	
				blgin = request_form['bi_host%dlogin' % i].replace(" ", "")
				bpwd = request_form['bi_host%dpwd' % i].replace(" ", "")
				parser.set('bi_search_provider%s' % counter2, 'login', blgin)
				parser.set('bi_search_provider%s' % counter2, 'pwd', bpwd)
				if(len(blgin) == 0 and len(bpwd) == 0):
					parser.set('bi_search_provider%s' % counter2, 'valid', '0')

			counter2 = counter2 + 1	
	
	parser.set('general', 'builtin_numserver', str(counter2-1))
	

	#~ bi_parser.write(sys.stdout)	
	with open('custom_params.ini', 'wt') as configfile:
		parser.write(configfile)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def read_conf(): 
	cf1 = read_conf_fn()
	#~ print cf1
	#~ if 'loadedModules' not in globals():
		#~ loadSearchModules()
		
	#~ cf2,co2 = read_conf_fn('custom_providers.ini')
#~ 
	#~ for i in xrange(len(co2)):
		#~ for j in xrange(len(cf1)):			
			#~ if(	int(cf1[j]['unique']) == int(co2[i]['unique'])):
				#~ cf1[j]['valid'] = co2[j]['valid'] 
		#~ 
	#~ for i in xrange(len(cf2)):
		#~ cf2[i]['builtin']  = 0
		#~ cf1.append(cf2[i])
		
	return cf1

 #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    
def read_conf_fn(): 
	cfg_struct = []
	parser = SafeConfigParser()
	parser.read('builtin_params.ini')
	portno = parser.get('general', 'port')	
	
	#~ chk if exists
	cst_parser = SafeConfigParser()
	cst_parser.read('custom_params.ini')
	try:
		numserver = cst_parser.get('general', 'numserver')	
		#~ custom	 NAB
		for i in xrange(int(numserver)):
			d1 = {'url': cst_parser.get('search_provider%d' % (i+1)  , 'url'),
				  'type': cst_parser.get('search_provider%d' % (i+1)  , 'type'),
				  'api': cst_parser.get('search_provider%d' % (i+1)  , 'api'),
				  'valid': cst_parser.get('search_provider%d' % (i+1)  , 'valid'),
				  'builtin': 0
				  }
			cfg_struct.append(d1)	
	except Exception:
		return cfg_struct
	
	try:
		builtin_numserver = cst_parser.get('general', 'builtin_numserver')
		for i in xrange(int(builtin_numserver)):	
			ret = cst_parser.has_option('bi_search_provider%d' % (i+1), 'login')			
			lgn= ''
			pwd= ''
			if(ret == True): 
				 lgn = cst_parser.get('bi_search_provider%d' % (i+1)  , 'login')
				 pwd = cst_parser.get('bi_search_provider%d' % (i+1)  , 'pwd')
			
			d1 = {'valid': cst_parser.get('bi_search_provider%d' % (i+1)  , 'valid'),
				  'type': cst_parser.get('bi_search_provider%d' % (i+1)  , 'type'),
				  'login': lgn,
				  'pwd': pwd,
				  'builtin': 1}
			cfg_struct.append(d1)
	except Exception:
			pass
				
	#~ cst_parser.write(sys.stdout)	
	return cfg_struct
 

 

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def html_builtin_output(cffile): 
	count = 0
	
	if 'SearchModule.loadedModules' not in globals():
		SearchModule.loadSearchModules()
	
	cffileb = []		
	for module in SearchModule.loadedModules:
		if(module.builtin):
			option='checked=yes'
			flogin=0
			login_name =  ''
			login_pwd = ''
			if(module.active == 0):
				option=''
			for i in xrange(len(cffile)):
				if(cffile[i]['type'] == module.typesrch):
					if(cffile[i]['valid'] == '0'):
						option=''
					else: 	
						option='checked=yes'
					
					login_name=cffile[i]['login']
					login_pwd=cffile[i]['pwd']
					
			if(module.login == 1):
				flogin = 1
			
			tmpcfg= {'stchk' : option,
					'humanname' : module.name,
					'idx' : count,
					'type' : module.typesrch,
					'flogin': flogin,
					'loginname': login_name,
					'loginpwd': login_pwd,
					}
			cffileb.append(tmpcfg)
			count = count + 1

	count = 0
	for i in xrange(len(cffile)):
		if(cffile[i]['builtin'] == 0):
			cffile[i]['idx'] =  count
			count = count + 1
		
	return render_template('config.html', cfg=cffile, cnt=count,  cnt_max=MAX_PROVIDER_NUMBER, cfg_bi=cffileb)


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


def config_read():
	cf = read_conf()
	webbuf_body_bi = html_builtin_output(cf)
	
	return webbuf_body_bi


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def config_write(request_form):
	write_conf(request_form)	
	#~ return config_read()
