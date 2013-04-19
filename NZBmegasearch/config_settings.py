# # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## # ## #    
#~ This file is part of NZBmegasearch by 0byte.
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

MAX_PROVIDER_NUMBER = 20

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
				parser.set('search_provider%s' % counter, 'valid', int(1))
				counter = counter + 1
	parser.add_section('general')
	parser.set('general', 'numserver', str(counter-1))
	
	#~ they exist for sure
	parser.set('general', 'port', request_form['port'].replace(" ", ""))
	parser.set('general', 'general_user', request_form['general_usr'].replace(" ", ""))
	parser.set('general', 'general_pwd', request_form['general_pwd'].replace(" ", ""))

	
	counter2 = 1
	for i in xrange(MAX_PROVIDER_NUMBER):
		if (request_form.has_key('bi_host%d' % i)  == True):
			parser.add_section('bi_search_provider%s' % counter2)
			parser.set('bi_search_provider%s' % counter2, 'type', request_form['bi_host%d' % i].replace(" ", ""))
			if (request_form.has_key('bi_host%dactive' % i)  == True):
				parser.set('bi_search_provider%s' % counter2, 'valid', int(1))
			else:
				parser.set('bi_search_provider%s' % counter2, 'valid', int(0))
			
			if (request_form.has_key('bi_host%dlogin' % i)  == True):	
				blgin = request_form['bi_host%dlogin' % i].replace(" ", "")
				bpwd = request_form['bi_host%dpwd' % i].replace(" ", "")
				parser.set('bi_search_provider%s' % counter2, 'login', blgin)
				parser.set('bi_search_provider%s' % counter2, 'pwd', bpwd)
				if(len(blgin) == 0 and len(bpwd) == 0):
					parser.set('bi_search_provider%s' % counter2, 'valid', int(0))

			counter2 = counter2 + 1	
	
	parser.set('general', 'builtin_numserver', str(counter2-1))
	

	#~ bi_parser.write(sys.stdout)	
	with open('custom_params.ini', 'wt') as configfile:
		parser.write(configfile)


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def read_conf_deepsearch(): 
	cfg_struct = []
	parser = SafeConfigParser()
	parser.read('custom_params.ini')

	if(parser.has_option('general'  ,'deep_numserver') == 0):
		return None

		numserver = parser.get('general', 'deep_numserver')	

		try:
			for i in xrange(int(numserver)):
				d1 = {'url': parser.get('deep_search_provider%d' % (i+1)  , 'url'),
					  'user': parser.get('deep_search_provider%d' % (i+1)  , 'user'),
					  'pwd': parser.get('deep_search_provider%d' % (i+1)  , 'pwd'),
					  'speed_class': parser.getint('deep_search_provider%d' % (i+1)  , 'speed_class'),
					  'valid': int(parser.getint('deep_search_provider%d' % (i+1)  , 'valid')),
					  }
				cfg_struct.append(d1)

		except Exception as e:
			print str(e)
			return None
		
	return 	cfg_struct



#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def read_conf(forcedcustom=''): 
	cf1, co1 = read_conf_fn(forcedcustom)
	return cf1,co1

 #~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    
def read_conf_fn(forcedcustom=''): 
	cfg_struct = []
	parser = SafeConfigParser()
	parser.read('builtin_params.ini')
	portno = parser.get('general', 'port')	
	gen_user = parser.get('general', 'general_user')	
	gen_pwd = parser.get('general', 'general_pwd')	
	gen_trd = parser.get('general', 'trends')	
	gen_timeout = int(parser.get('general', 'default_timeout'))
	gen_cacheage = int(parser.get('general', 'max_cache_age'))
	gen_log_size = int(parser.get('general', 'max_log_size'))
	gen_log_backupcount = int(parser.get('general', 'max_log_backupcount'))
	gen_seed_warptable = int(parser.get('general', 'seed_warptable'))
	gen_trends_refreshrate = int(parser.get('general', 'trends_refreshrate'))
	gen_motd = parser.get('general', 'motd')
	gen_stats_key = parser.get('general', 'stats_key')
	gen_tslow = int(parser.get('general', 'timeout_slow'))
	gen_tfast = int(parser.get('general', 'timeout_fast'))
	co1 = {'portno': portno, 'general_usr' : gen_user, 'general_pwd' : gen_pwd, 'general_trend' : gen_trd, 
			'default_timeout' : gen_timeout, 'timeout_class' : [gen_tfast, gen_timeout, gen_tslow ],
			'max_cache_age' : gen_cacheage, 'log_backupcount': gen_log_backupcount, 
			'log_size' : gen_log_size, 'seed_warptable' : gen_seed_warptable, 'trends_refreshrate':gen_trends_refreshrate,
			'stats_key' : gen_stats_key, 'motd':gen_motd}
	
	#~ chk if exists
	cst_parser = SafeConfigParser()
	
	if(forcedcustom == ''):
		cst_parser.read('custom_params.ini')
	else:
		print 'Forced custom filename: ' + forcedcustom
		cst_parser.read(forcedcustom)	

	try:
		numserver = cst_parser.get('general', 'numserver')	
		#~ custom	 NAB
		for i in xrange(int(numserver)):
			spc = 2 
			if(cst_parser.has_option('search_provider%d' % (i+1)  ,'speed_class')):
				spc = cst_parser.getint('search_provider%d' % (i+1)  , 'speed_class')
			d1 = {'url': cst_parser.get('search_provider%d' % (i+1)  , 'url'),
				  'type': cst_parser.get('search_provider%d' % (i+1)  , 'type'),
				  'api': cst_parser.get('search_provider%d' % (i+1)  , 'api'),
				  'speed_class': spc,
				  'valid': int(cst_parser.get('search_provider%d' % (i+1)  , 'valid')),
				  'timeout':  gen_timeout,
				  'builtin': 0
				  }
			cfg_struct.append(d1)
			
		ret1 = cst_parser.has_option('general', 'port')
		if(ret1 == True): 
			portno = cst_parser.get('general', 'port')			
		ret1 = cst_parser.has_option('general', 'general_user')
		if(ret1 == True): 
			gen_user = cst_parser.get('general', 'general_user')	
			gen_pwd = cst_parser.get('general', 'general_pwd')	


	except Exception as e:
		print str(e)
		return None, co1

	try:
		builtin_numserver = cst_parser.get('general', 'builtin_numserver')
		for i in xrange(int(builtin_numserver)):	
			spc = 2 
			if(cst_parser.has_option('bi_search_provider%d' % (i+1)  ,'speed_class')):
				spc = cst_parser.getint('bi_search_provider%d' % (i+1)  , 'speed_class')

			ret = cst_parser.has_option('bi_search_provider%d' % (i+1), 'login')			
			lgn= ''
			pwd= ''
			if(ret == True): 
				 lgn = cst_parser.get('bi_search_provider%d' % (i+1)  , 'login')
				 pwd = cst_parser.get('bi_search_provider%d' % (i+1)  , 'pwd')
			
			try:
				d1 = {'valid': int(cst_parser.get('bi_search_provider%d' % (i+1)  , 'valid')),
					  'type': cst_parser.get('bi_search_provider%d' % (i+1)  , 'type'),
					  'speed_class': spc,
					  'login': lgn,
					  'pwd': pwd,
					  'timeout':  gen_timeout,
					  'builtin': 1}
			except Exception as e:
				print str(e)
				return None, co1

	  
			cfg_struct.append(d1)
	except Exception as e:
		print str(e)
		return None, co1
 
							
	#~ cst_parser.write(sys.stdout)	
	return cfg_struct, co1
 

 

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
def html_builtin_output(cffile, genopt): 
	count = 0
	
	if 'SearchModule.loadedModules' not in globals():
		SearchModule.loadSearchModules()
	
	cffileb = []		
	
	if(cffile is None):
		cffile = []
		
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
					if(cffile[i]['valid'] == 0):
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

	return render_template('config.html', cfg=cffile, cfg_dp=cfdsfile,  cnt=count,  genopt = genopt, 
										  cnt_max=MAX_PROVIDER_NUMBER, cfg_bi=cffileb)


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


def config_read():
	cf,co = read_conf()
	webbuf_body_bi = html_builtin_output(cf,co)
	
	return webbuf_body_bi


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def config_write(request_form):
	write_conf(request_form)	
	#~ return config_read()
