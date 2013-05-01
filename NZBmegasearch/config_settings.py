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
import copy


MAX_PROVIDER_NUMBER = 8


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class CfgSettings:
	
	# Set up class variables
	def __init__(self):
		self.selectable_speedopt = [ ['1', 'Normal Response',''],
									 ['2','Extensive Response','']]
		self.selectable_speedopt_cpy = copy.deepcopy(self.selectable_speedopt)
		self.cgen = []
		self.cfg = []
		self.cfg_deep = []
		self.read_conf_general()
		self.read_conf_custom()
		self.read_conf_deepsearch()

	def	reset(self):
		self.cfg = []
		
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def	write(self, request_form):
		parser = SafeConfigParser()

		#~ general settings
		parser.add_section('speed_option')
		parser.add_section('general')
		parser.set('general', 'port', request_form['port'].replace(" ", ""))
		parser.set('general', 'general_user', request_form['general_usr'].replace(" ", ""))
		parser.set('general', 'general_pwd', request_form['general_pwd'].replace(" ", ""))
		
		parser.set('general', 'general_https', '0')
		if (request_form.has_key('https')  == True):
			parser.set('general', 'general_https', '1')

		parser.set('general', 'sabnzbd_url', request_form['sabnzbd_url'].replace(" ", ""))
		parser.set('general', 'sabnzbd_api', request_form['sabnzbd_api'].replace(" ", ""))
		
		
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
					parser.set('speed_option', 's%d_speed_class' % counter, request_form['selspeed%d' %i].replace(" ", ""))
					counter = counter + 1
		parser.set('general', 'numserver', str(counter-1))

		#~ builtin search
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
				parser.set('speed_option', 'b%d_speed_class' % counter2, request_form['bi_host%dspeed' %i])	
				counter2 = counter2 + 1	
		parser.set('general', 'builtin_numserver', str(counter2-1))
		

		#~ web search
		counter3 = 1
		for i in xrange(MAX_PROVIDER_NUMBER):
			if (request_form.has_key('host%d' % i)  == True):
				if(request_form['host%d' % i].replace(" ", "")): 
					parser.add_section('deep_search_provider%s' % counter3)
					parser.set('deep_search_provider%s' % counter3, 'url',request_form['ds_host%d' % i].replace(" ", ""))
					parser.set('deep_search_provider%s' % counter3, 'user',request_form['ds_usr%d' % i].replace(" ", ""))
					parser.set('deep_search_provider%s' % counter3, 'pwd', request_form['ds_pass%d' % i])
					parser.set('deep_search_provider%s' % counter3, 'type', request_form['ds_type%d' % i].replace(" ", ""))
					parser.set('deep_search_provider%s' % counter3, 'valid', '1')
					parser.set('speed_option', 'd%d_speed_class' % counter3, request_form['ds_selspeed%d' %i])
					counter3 = counter3 + 1
		parser.set('general', 'deep_numserver', str(counter3-1))

		#~ parser.write(sys.stdout)	
		with open('custom_params.ini', 'wt') as configfile:
			parser.write(configfile)


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def read_conf_deepsearch(self): 
		self.cfg_deep = []
		parser = SafeConfigParser()
		parser.read('custom_params.ini')

		if(parser.has_option('general'  ,'deep_numserver') == False):
			return None

		numserver = parser.get('general', 'deep_numserver')	

		try:
			for i in xrange(int(numserver)):
				spc = self.get_conf_speedopt(parser, i, 'd')
				if ( spc == -1 ):
					spc = 1

				d1 = {'url': parser.get('deep_search_provider%d' % (i+1)  , 'url'),
					  'user': parser.get('deep_search_provider%d' % (i+1)  , 'user'),
					  'pwd': parser.get('deep_search_provider%d' % (i+1)  , 'pwd'),
					  'speed_class': spc,
					  'valid': int(parser.getint('deep_search_provider%d' % (i+1)  , 'valid')),
					  }
				self.cfg_deep.append(d1)

		except Exception as e:
			print str(e)
			cfg_deep = None

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    

	def get_conf_speedopt(self, parser, idx, secname):

		if(parser.has_section('speed_option') == True):
			try:
				spc1 = parser.getint('speed_option', secname + '%d_speed_class' % (idx+1))
				return spc1
			except Exception as e:
				print str(e)
				return -1
		else:
			return -1		

				
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    
		
	def read_conf_general(self, forcedcustom=''): 
		parser = SafeConfigParser()
		parser.read('builtin_params.ini')
		portno = parser.getint('general', 'port')	
		gen_user = parser.get('general', 'general_user')	
		gen_pwd = parser.get('general', 'general_pwd')	
		gen_https = parser.getint('general', 'general_https')
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
		self.cgen = {'portno': portno, 'general_usr' : gen_user, 'general_pwd' : gen_pwd, 'general_trend' : gen_trd,
				'general_https' : gen_https,
				'default_timeout' : gen_timeout, 'timeout_class' : [gen_tfast, gen_timeout, gen_tslow ],
				'max_cache_age' : gen_cacheage, 'log_backupcount': gen_log_backupcount, 
				'log_size' : gen_log_size, 'seed_warptable' : gen_seed_warptable, 'trends_refreshrate':gen_trends_refreshrate,
				'sabnzbd_url' : '', 'sabnzbd_api':'',
				'stats_key' : gen_stats_key, 'motd':gen_motd}
		self.selectable_speedopt = copy.deepcopy(self.selectable_speedopt_cpy)
		self.selectable_speedopt[0][1] += ' ['+str(self.cgen['timeout_class'][1])+'s]'
		self.selectable_speedopt[1][1] += ' ['+str(self.cgen['timeout_class'][2])+'s]'
		#~ self.selectable_speedopt[2][1] += ' ['+str(self.cgen['timeout_class'][2])+'s]'

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    
	
	def read_conf_custom(self, forcedcustom=''): 
		self.cfg = []
		
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
				spc = self.get_conf_speedopt(cst_parser, i, 's')
				if ( spc == -1 ):
					spc = 1

				d1 = {'url': cst_parser.get('search_provider%d' % (i+1)  , 'url'),
					  'type': cst_parser.get('search_provider%d' % (i+1)  , 'type'),
					  'api': cst_parser.get('search_provider%d' % (i+1)  , 'api'),
					  'speed_class': spc,
					  'valid':  cst_parser.getint('search_provider%d' % (i+1)  , 'valid'),
					  'timeout':  self.cgen['default_timeout'],
					  'builtin': 0
					  }					  
				self.cfg.append(d1)


			if(cst_parser.has_option('general' ,'sabnzbd_url')):
				self.cgen['sabnzbd_url'] = cst_parser.get('general', 'sabnzbd_url')
			if(cst_parser.has_option('general' ,'sabnzbd_api')):
				self.cgen['sabnzbd_api'] = cst_parser.get('general', 'sabnzbd_api')
			if(cst_parser.has_option('general' ,'general_https')):
				self.cgen['general_https'] = cst_parser.getint('general', 'general_https')			
			if (cst_parser.has_option('general', 'port')):
				self.cgen['portno'] = cst_parser.getint('general', 'port')	
			if(cst_parser.has_option('general', 'general_user')):
				self.cgen['general_usr'] = cst_parser.get('general', 'general_user') 
				self.cgen['general_pwd'] = cst_parser.get('general', 'general_pwd')	

		except Exception as e:
			print str(e)
			self.cfg = None
			return

		try:
			builtin_numserver = cst_parser.get('general', 'builtin_numserver')
			for i in xrange(int(builtin_numserver)):	
				spc = self.get_conf_speedopt(cst_parser, i, 'b')
				if ( spc == -1 ):
					spc = 1

				ret = cst_parser.has_option('bi_search_provider%d' % (i+1), 'login')			
				lgn= ''
				pwd= ''
				if(ret == True): 
					 lgn = cst_parser.get('bi_search_provider%d' % (i+1)  , 'login')
					 pwd = cst_parser.get('bi_search_provider%d' % (i+1)  , 'pwd')
				
				d1 = {'valid': cst_parser.getint('bi_search_provider%d' % (i+1)  , 'valid'),
					  'type': cst_parser.get('bi_search_provider%d' % (i+1)  , 'type'),
					  'speed_class': spc,
					  'login': lgn,
					  'pwd': pwd,
					  'timeout':  self.cgen['default_timeout'],
					  'builtin': 1}
				self.cfg.append(d1)
				
		except Exception as e:
			print str(e)
			return
	 
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def html_editpage(self): 

		count = 0
		if 'SearchModule.loadedModules' not in globals():
			SearchModule.loadSearchModules()
		
		cffileb = []		
		cffile  = copy.deepcopy(self.cfg)
		cdsfile = self.cfg_deep
		genopt = self.cgen
		
		if(cffile is None):
			cffile = []

		if(cdsfile is None):
			cdsfile = []
			
		for module in SearchModule.loadedModules:
			if(module.builtin):
				option='checked=yes'
				flogin=0
				login_name =  ''
				login_pwd = ''
				speed_cl = 1
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
						speed_cl = cffile[i]['speed_class']
						
				if(module.login == 1):
					flogin = 1
				
				tmpcfg= {'stchk' : option,
						'humanname' : module.name,
						'idx' : count,
						'speed_class' : speed_cl,
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
				sel_speedopt_tmp = copy.deepcopy(self.selectable_speedopt)	
				sel_speedopt_tmp[cffile[i]['speed_class']][2] = 'selected'
				cffile[i]['selspeed_sel'] =  sel_speedopt_tmp

		
		sel_speedopt_basic = copy.deepcopy(self.selectable_speedopt)	
		sel_speedopt_basic[0][2] = 'selected'
		
		count=0
		for i in xrange(len(cdsfile)):
			cdsfile[i]['idx'] =  count
			count = count + 1
			sel_speedopt_tmp = copy.deepcopy(self.selectable_speedopt)	
			sel_speedopt_tmp[cdsfile[i]['speed_class']][2] = 'selected'
			cdsfile[i]['selspeed_sel'] =  sel_speedopt_tmp
					
		genopt['general_https_verbose']	 = ''
		if(genopt['general_https'] == 1):
			genopt['general_https_verbose']	 = 'checked=yes'
		

					
		return render_template('config.html', cfg=cffile, cfg_dp=cdsfile,  cnt=count,  genopt = genopt, 
											  sel_speedopt_basic = sel_speedopt_basic,
 											  cnt_max=MAX_PROVIDER_NUMBER, cfg_bi=cffileb)


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


	def edit_config(self):
		self.read_conf_general()
		self.read_conf_custom()		
		self.read_conf_deepsearch()
		webbuf_body_bi = self.html_editpage()
		
		return webbuf_body_bi
		


