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
import os
import SearchModule
import DeepsearchModule
import copy
import megasearch

MAX_PROVIDER_NUMBER = 20


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
class CfgSettings:
	
	# Set up class variables
	def __init__(self):
		self.dirconf_oshift =  os.getenv('OPENSHIFT_DATA_DIR', '')
		self.dirconf_local = os.path.dirname(os.path.realpath(__file__))+'/'
		if getattr(sys, 'frozen', False):
			self.dirconf_local = os.path.dirname(sys.executable)+'/'

		if(len(self.dirconf_oshift)):
			self.dirconf = self.dirconf_oshift
		else:
			self.dirconf = 	self.dirconf_local
		
		self.selectable_extraopt = [ ['0', 'API+Manual',''],
								  ['1','Manual only',''],
								  ['2','API only','']]
		self.selectable_speedopt = [ ['1', 'Normal Response',''],
									 ['2','Slow Response','']]
		self.selectable_speedopt_cpy = copy.deepcopy(self.selectable_speedopt)
		self.cgen = []
		self.cfg = []
		self.cfg_deep = []
		self.read_conf_general()
		self.read_conf_custom()
		self.read_conf_deepsearch()
		self.filter_obsolete_providers()
		
	def	reset(self):
		self.cfg = []

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def	filter_obsolete_providers(self):
		
		#~ avoids obsolete modules to appear in the search routine
		#~ this is an additional safety measure
		if 'loadedModules' not in globals():
			SearchModule.loadSearchModules()
		
		saved_cfg = []
		if(self.cfg is not None):
			for index in xrange(len(self.cfg)):
				index_found = False
				for module in SearchModule.loadedModules:
					if( module.typesrch == self.cfg[index]['type']):
						index_found = True
				if(index_found is True):
					saved_cfg.append(self.cfg[index])
			self.cfg = copy.deepcopy(saved_cfg)
						
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def	write(self, request_form):
		parser = SafeConfigParser()

		#~ general settings
		parser.add_section('speed_option')
		parser.add_section('extra_option')
		parser.add_section('general')
		parser.set('general', 'port', request_form['port'].replace(" ", ""))
		parser.set('general', 'general_user', request_form['general_usr'].replace(" ", ""))
		parser.set('general', 'general_pwd', request_form['general_pwd'].replace(" ", ""))
		parser.set('general', 'config_user', request_form['config_user'].replace(" ", ""))
		parser.set('general', 'config_pwd', request_form['config_pwd'].replace(" ", ""))
		parser.set('general', 'general_apikey', request_form['general_apikey'].replace(" ", ""))
		parser.set('general', 'searchaddontxt', request_form['searchaddontxt'])
		parser.set('general', 'general_https', '0')
		parser.set('general', 'search_suggestions', '0')
		parser.set('general', 'trends', '0')
		parser.set('general', 'trends_qty', request_form['seltrqty'])		
		parser.set('general', 'smartsearch', '0')
		parser.set('general', 'cache_active', '0')	
		parser.set('general', 'general_ipaddress', '')		
		parser.set('general', 'predb_active', '0')	
		parser.set('general', 'general_restrictopt1', '0')				
		

		if (request_form['general_ipaddress'] != 'AUTO'):			
			cip = request_form['general_ipaddress'].replace(" ", "").replace("http://", "").replace("https://", "")
			if(cip[-1] == '/'):
				cip = cip[:-1]
			parser.set('general', 'general_ipaddress', cip)
		if (request_form.has_key('https')  == True):
			parser.set('general', 'general_https', '1')
		if (request_form.has_key('general_restrictopt1')  == True):
			parser.set('general', 'general_restrictopt1', '1')
		if (request_form.has_key('trends')  == True):
			parser.set('general', 'trends', '1')
		if (request_form.has_key('sugg')  == True):
			parser.set('general', 'search_suggestions', '1')
		if (request_form.has_key('smartsearch')  == True):
			parser.set('general', 'smartsearch', '1')
		if (request_form.has_key('predb_active')  == True):
			parser.set('general', 'predb_active', '1')
		if (request_form.has_key('cache_active')  == True):
			parser.set('general', 'cache_active', request_form['cache_active'])

		revproxy =  request_form['revproxy'].replace(" ", "")
		if(len(revproxy)):
			if(revproxy[-1] == '/'):
				revproxy = revproxy[:-1]
		parser.set('general', 'revproxy', revproxy)

		sab_url = request_form['sabnzbd_url'].replace(" ", "")
		if(len(sab_url)):
			if(sab_url[-1] == '/'):
				sab_url = sab_url[:-1]
		parser.set('general', 'sabnzbd_url', sab_url)
		parser.set('general', 'sabnzbd_api', request_form['sabnzbd_api'].replace(" ", ""))
		parser.set('general', 'search_default', request_form['selcat'])

		nzbget_url = request_form['nzbget_url'].replace(" ", "")
		if(len(nzbget_url)):
			if(nzbget_url[-1] == '/'):
				nzbget_url = sab_url[:-1]
		parser.set('general', 'nzbget_url', nzbget_url)
		parser.set('general', 'nzbget_user', request_form['nzbget_user'].replace(" ", ""))
		parser.set('general', 'nzbget_pwd', request_form['nzbget_pwd'].replace(" ", ""))
		
		no_APInab = int(request_form['no_APInab'])+1
		no_WEBnab = int(request_form['no_WEBnab'])+1
		
		#~ api
		counter = 1
		for i in xrange(no_APInab):
			if (request_form.has_key('host%d' % i)  == True):
				if(request_form['host%d' % i].replace(" ", "")): 
					parser.add_section('search_provider%s' % counter)
					hosturl = request_form['host%d' % i].replace(" ", "")
					if(hosturl[-1] == '/'):
						hosturl = hosturl[:-1]
					parser.set('search_provider%s' % counter, 'url',hosturl)
					parser.set('search_provider%s' % counter, 'api',request_form['API%d' % i].replace(" ", ""))
					parser.set('search_provider%s' % counter, 'type', request_form['type%d' % i].replace(" ", ""))
					parser.set('search_provider%s' % counter, 'valid', '0')
					if (request_form.has_key('valid%d' % i)  == True):
						parser.set('search_provider%s' % counter, 'valid', '1')
					parser.set('speed_option', 's%d_speed_class' % counter, request_form['selspeed%d' %i].replace(" ", ""))
					parser.set('extra_option', 's%d_extra_class' % counter, request_form['selextra%d' %i].replace(" ", ""))
					counter = counter + 1
		parser.set('general', 'numserver', str(counter-1))

		#~ builtin search
		counter2 = 1
		for i in xrange(MAX_PROVIDER_NUMBER):
			if (request_form.has_key('bi_host%d' % i)  == True):
				site_typename = request_form['bi_host%d' % i].replace(" ", "")
				#~ API based builtins
				if(site_typename[:2] != 'DS'):
					parser.add_section('bi_search_provider%s' % counter2)
					parser.set('bi_search_provider%s' % counter2, 'type', site_typename)
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
					parser.set('extra_option', 'b%d_extra_class' % counter2, request_form['bi_host%dextra' %i])	
					counter2 = counter2 + 1	
		parser.set('general', 'builtin_numserver', str(counter2-1))
		

		#~ web search
		counter3 = 1
		for i in xrange(no_WEBnab):
			if (request_form.has_key('ds_host%d' % i)  == True):
				if(request_form['ds_host%d' % i].replace(" ", "")): 
					parser.add_section('deep_search_provider%s' % counter3)
					hosturl = request_form['ds_host%d' % i].replace(" ", "")
					if(hosturl[-1] == '/'):
						hosturl = hosturl[:-1]
					
					parser.set('deep_search_provider%s' % counter3, 'url',hosturl)
					parser.set('deep_search_provider%s' % counter3, 'user',request_form['ds_usr%d' % i].replace(" ", ""))
					parser.set('deep_search_provider%s' % counter3, 'pwd', request_form['ds_pass%d' % i])
					parser.set('deep_search_provider%s' % counter3, 'type', request_form['ds_type%d' % i].replace(" ", ""))
					parser.set('deep_search_provider%s' % counter3, 'valid', '0')
					if (request_form.has_key('ds_valid%d' % i)  == True):
						parser.set('deep_search_provider%s' % counter3, 'valid', '1')
					parser.set('speed_option', 'd%d_speed_class' % counter3, request_form['ds_selspeed%d' %i])
					parser.set('extra_option', 'd%d_extra_class' % counter3, request_form['ds_selextra%d' %i])
					counter3 = counter3 + 1

		#~ builtin web search
		for i in xrange(MAX_PROVIDER_NUMBER):
			if (request_form.has_key('bi_host%d' % i)  == True):
				site_typename = request_form['bi_host%d' % i].replace(" ", "")
				#~ API based builtins
				if(site_typename[:2] == 'DS'):
					parser.add_section('deep_search_provider%s' % counter3)
					parser.set('deep_search_provider%s' % counter3, 'isbuiltin', '1')
					parser.set('deep_search_provider%s' % counter3, 'type', site_typename)
					parser.set('deep_search_provider%s' % counter3, 'url', request_form['bi_host%durl' % i].replace(" ", ""))
					
					if (request_form.has_key('bi_host%dactive' % i)  == True):
						parser.set('deep_search_provider%s' % counter3, 'valid', '1')
					else:
						parser.set('deep_search_provider%s' % counter3, 'valid', '0')
					
					if (request_form.has_key('bi_host%dlogin' % i)  == True):	
						blgin = request_form['bi_host%dlogin' % i].replace(" ", "")
						bpwd = request_form['bi_host%dpwd' % i].replace(" ", "")
						parser.set('deep_search_provider%s' % counter3, 'user', blgin)
						parser.set('deep_search_provider%s' % counter3, 'pwd', bpwd)
						if(len(blgin) == 0 and len(bpwd) == 0):
							parser.set('deep_search_provider%s' % counter3, 'valid', '0')
					parser.set('speed_option', 'd%d_speed_class' % counter3, request_form['bi_host%dspeed' %i])	
					parser.set('extra_option', 'd%d_extra_class' % counter3, request_form['bi_host%dextra' %i])	
					counter3 = counter3 + 1	

		parser.set('general', 'deep_numserver', str(counter3-1))

		#~ parser.write(sys.stdout)	
		with open(self.dirconf+'custom_params.ini', 'wt') as configfile:
			parser.write(configfile)


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

	def read_conf_deepsearch(self): 
		self.cfg_deep = []
		parser = SafeConfigParser()
		parser.read(self.dirconf+'custom_params.ini')

		if(parser.has_option('general'  ,'deep_numserver') == False):
			return None

		numserver = parser.get('general', 'deep_numserver')	

		try:
			for i in xrange(int(numserver)):
				spc = self.get_conf_speedopt(parser, i, 'd')
				if ( spc == -1 ):
					spc = 1
				epc = self.get_conf_extraopt(parser, i, 'd')
				if ( epc == -1 ):
					epc = 0

				if(parser.has_option('deep_search_provider%d' % (i+1)  , 'type')):	
					typeds = parser.get('deep_search_provider%d' % (i+1)  , 'type')
				else:	
					typeds = 'DSN'

				d1 = {'url': parser.get('deep_search_provider%d' % (i+1)  , 'url'),
					  'user': parser.get('deep_search_provider%d' % (i+1)  , 'user'),
					  'pwd': parser.get('deep_search_provider%d' % (i+1)  , 'pwd'),
					  'type': typeds,
					  'speed_class': spc,
					  'extra_class': epc,
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

	def get_conf_extraopt(self, parser, idx, secname):

		if(parser.has_section('extra_option') == True):
			try:
				spc1 = parser.getint('extra_option', secname + '%d_extra_class' % (idx+1))
				return spc1
			except Exception as e:
				print str(e)
				return -1
		else:
			return -1		
				
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~    
		
	def read_conf_general(self, forcedcustom=''): 
		parser = SafeConfigParser()
		parser.read(self.dirconf+'builtin_params.ini')
		portno = parser.getint('general', 'port')	
		gen_user = parser.get('general', 'general_user')	
		gen_pwd = parser.get('general', 'general_pwd')	
		config_user = parser.get('general', 'config_user')	
		config_pwd = parser.get('general', 'config_pwd')
		gen_https = parser.getint('general', 'general_https')
		gen_trd = parser.getint('general', 'trends')	
		gen_timeout = int(parser.get('general', 'default_timeout'))
		gen_cacheage = int(parser.get('general', 'max_cache_age'))
		gen_cacheqty = int(parser.get('general', 'max_cache_qty'))
		gen_log_size = int(parser.get('general', 'max_log_size'))
		gen_log_backupcount = int(parser.get('general', 'max_log_backupcount'))
		gen_seed_warptable = int(parser.get('general', 'seed_warptable'))
		gen_trends_refreshrate = int(parser.get('general', 'trends_refreshrate'))
		gen_motd = parser.get('general', 'motd')
		gen_stats_key = parser.get('general', 'stats_key')
		gen_tslow = int(parser.get('general', 'timeout_slow'))
		gen_tfast = int(parser.get('general', 'timeout_fast'))
		gen_sugg = parser.getint('general', 'search_suggestions')
		gen_search_default = parser.get('general', 'search_default')
		gen_trends_qty = parser.getint('general', 'trends_qty')
		smartsearch = parser.getint('general', 'smartsearch')
		cache_active = parser.getint('general', 'cache_active')
		searchaddontxt = parser.get('general', 'searchaddontxt')		
		revproxy = parser.get('general', 'revproxy')
		self.cgen = {'portno': portno, 'general_usr' : gen_user, 'general_pwd' : gen_pwd, 'general_trend' : gen_trd,
				'config_user':config_user,
				'config_pwd':config_pwd,
				'smartsearch':smartsearch,
				'searchaddontxt':searchaddontxt,
				'general_suggestion' : gen_sugg,
				'general_https' : gen_https,
				'cache_active':cache_active,
				'general_ipaddress': '',
				'default_timeout' : gen_timeout, 'timeout_class' : [gen_tfast, gen_timeout, gen_tslow ],
				'max_cache_age' : gen_cacheage, 'log_backupcount': gen_log_backupcount,
				'max_cache_qty' : gen_cacheqty, 
				'log_size' : gen_log_size, 'seed_warptable' : gen_seed_warptable, 'trends_refreshrate':gen_trends_refreshrate,
				'search_default':gen_search_default,
				'trends_qty':gen_trends_qty,
				'sabnzbd_url' : '', 'sabnzbd_api':'',
				'nzbget_url' : '', 'nzbget_user':'','nzbget_pwd':'',
				'general_apikey' : '',
				'general_restrictopt1' : 0,
				'predb_active' : 1,
				'revproxy':revproxy,
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
			cst_parser.read(self.dirconf+'custom_params.ini')
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
				epc = self.get_conf_extraopt(cst_parser, i, 's')
				if ( epc == -1 ):
					epc = 0

				d1 = {'url': cst_parser.get('search_provider%d' % (i+1)  , 'url'),
					  'type': cst_parser.get('search_provider%d' % (i+1)  , 'type'),
					  'api': cst_parser.get('search_provider%d' % (i+1)  , 'api'),
					  'speed_class': spc,
					  'extra_class': epc,
					  'valid':  cst_parser.getint('search_provider%d' % (i+1)  , 'valid'),
					  'timeout':  self.cgen['default_timeout'],
					  'builtin': 0
					  }					  
				self.cfg.append(d1)


			if(cst_parser.has_option('general' ,'sabnzbd_url')):
				self.cgen['sabnzbd_url'] = cst_parser.get('general', 'sabnzbd_url')
			if(cst_parser.has_option('general' ,'sabnzbd_api')):
				self.cgen['sabnzbd_api'] = cst_parser.get('general', 'sabnzbd_api')
			if(cst_parser.has_option('general' ,'nzbget_url')):
				self.cgen['nzbget_url'] = cst_parser.get('general', 'nzbget_url')
			if(cst_parser.has_option('general' ,'nzbget_user')):
				self.cgen['nzbget_user'] = cst_parser.get('general', 'nzbget_user')
			if(cst_parser.has_option('general' ,'nzbget_pwd')):
				self.cgen['nzbget_pwd'] = cst_parser.get('general', 'nzbget_pwd')
			if(cst_parser.has_option('general' ,'general_https')):
				self.cgen['general_https'] = cst_parser.getint('general', 'general_https')			
			if (cst_parser.has_option('general', 'port')):
				self.cgen['portno'] = cst_parser.getint('general', 'port')	
			if(cst_parser.has_option('general', 'general_user')):
				self.cgen['general_usr'] = cst_parser.get('general', 'general_user') 
				self.cgen['general_pwd'] = cst_parser.get('general', 'general_pwd')	
			if(cst_parser.has_option('general' ,'search_suggestions')):
				self.cgen['general_suggestion'] = cst_parser.getint('general', 'search_suggestions')			
			if(cst_parser.has_option('general' ,'trends')):
				self.cgen['general_trend'] = cst_parser.getint('general', 'trends')			
			if(cst_parser.has_option('general' ,'search_default')):	
				self.cgen['search_default'] = cst_parser.get('general', 'search_default')		
			if(cst_parser.has_option('general' ,'config_user')):	
				self.cgen['config_user'] = cst_parser.get('general', 'config_user')
			if(cst_parser.has_option('general' ,'config_pwd')):	
				self.cgen['config_pwd'] = cst_parser.get('general', 'config_pwd')
			if(cst_parser.has_option('general' ,'general_apikey')):	
				self.cgen['general_apikey'] = cst_parser.get('general', 'general_apikey')
			if(cst_parser.has_option('general' ,'trends_qty')):	
				self.cgen['trends_qty'] = cst_parser.getint('general', 'trends_qty')
			if(cst_parser.has_option('general' ,'smartsearch')):	
				self.cgen['smartsearch'] = cst_parser.getint('general', 'smartsearch')
			if(cst_parser.has_option('general' ,'max_cache_age')):	
				self.cgen['max_cache_age'] = cst_parser.getint('general', 'max_cache_age')
			if(cst_parser.has_option('general' ,'max_cache_qty')):	
				self.cgen['max_cache_qty'] = cst_parser.getint('general', 'max_cache_qty')
			if(cst_parser.has_option('general' ,'cache_active')):	
				self.cgen['cache_active'] = cst_parser.getint('general', 'cache_active')
			if(cst_parser.has_option('general' ,'searchaddontxt')):	
				self.cgen['searchaddontxt'] = cst_parser.get('general', 'searchaddontxt')
			if(cst_parser.has_option('general' ,'general_ipaddress')):	
				self.cgen['general_ipaddress'] = cst_parser.get('general', 'general_ipaddress')
			if(cst_parser.has_option('general' ,'predb_active')):	
				self.cgen['predb_active'] = cst_parser.getint('general', 'predb_active')
			if(cst_parser.has_option('general' ,'general_restrictopt1')):	
				self.cgen['general_restrictopt1'] = cst_parser.getint('general', 'general_restrictopt1')
			if(cst_parser.has_option('general' ,'revproxy')):	
				self.cgen['revproxy'] = cst_parser.get('general', 'revproxy')

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
				epc = self.get_conf_extraopt(cst_parser, i, 'b')
				if ( epc == -1 ):
					epc = 0

				ret = cst_parser.has_option('bi_search_provider%d' % (i+1), 'login')			
				lgn= ''
				pwd= ''
				if(ret == True): 
					 lgn = cst_parser.get('bi_search_provider%d' % (i+1)  , 'login')
					 pwd = cst_parser.get('bi_search_provider%d' % (i+1)  , 'pwd')
				
				d1 = {'valid': cst_parser.getint('bi_search_provider%d' % (i+1)  , 'valid'),
					  'type': cst_parser.get('bi_search_provider%d' % (i+1)  , 'type'),
					  'speed_class': spc,
					  'extra_class': epc,
					  'login': lgn,
					  'pwd': pwd,
					  'timeout':  self.cgen['default_timeout'],
					  'builtin': 1}
				self.cfg.append(d1)
				
				#~ Gingadaddy
				
		except Exception as e:
			print str(e)
			return
	 
	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def html_editpage(self): 

		count = 0
		if 'SearchModule.loadedModules' not in globals():
			SearchModule.loadSearchModules()
		
		dsearchsupport = DeepsearchModule.supportedengines()
		
		cffileb = []		
		cffile  = copy.deepcopy(self.cfg)
		cdsfile = self.cfg_deep
		genopt = self.cgen

		if(cffile is None):
			cffile = []

		if(cdsfile is None):
			cdsfile = []
		
		cdomainname = megasearch.getdomainext()
		
		for module in SearchModule.loadedModules:
			if(module.builtin):
				option='checked=yes'
				flogin=0
				flogin_caption_user='login'
				flogin_caption_pwd='pwd'
				login_name =  ''
				login_pwd = ''
				speed_cl = 1
				extra_cl = 0
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
						extra_cl = cffile[i]['extra_class']
						
				if(module.login == 1):
					flogin = 1
					#~ if('caption_login_user' in module):
					if (hasattr(module, 'caption_login_user')):
						flogin_caption_user = module.caption_login_user
						flogin_caption_pwd = module.caption_login_pwd
				
				tmpcfg= {'stchk' : option,
						'humanname' : module.name,
						'url': '',
						'idx' : count,
						'speed_class' : speed_cl,
						'extra_class' : extra_cl,
						'type' : module.typesrch,
						'flogin': flogin,
						'flogin_caption_user': flogin_caption_user,
						'flogin_caption_pwd': flogin_caption_pwd,
						'loginname': login_name,
						'loginpwd': login_pwd,
						}
				cffileb.append(tmpcfg)
				count = count + 1
		
		#~ scrapers with web login
		for dsearchmodule in dsearchsupport:
			if(dsearchmodule['opts']['builtin']):
				option='checked=yes'
				flogin=0
				login_name =  ''
				login_pwd = ''
				speed_cl = dsearchmodule['opts']['speed_cl']
				extra_cl = dsearchmodule['opts']['extra_cl']
				if(dsearchmodule['opts']['active'] == 0):
					option=''
					
				for i in xrange(len(cdsfile)):
					if(cdsfile[i]['type'] == dsearchmodule['opts']['typesrch']):
						if(cdsfile[i]['valid'] == 0):
							option=''
						else: 	
							option='checked=yes'							
						#~ speed_cl = cdsfile[i]['speed_cl']
						login_name=cdsfile[i]['user']
						login_pwd=cdsfile[i]['pwd']
				if(dsearchmodule['opts']['login'] == 1):
					flogin = 1
				tmpcfg= {'stchk' : option,
						'humanname' : dsearchmodule['name'],
						'url': dsearchmodule['opts']['url'],
						'idx' : count,
						'flogin_caption_user': 'login',
						'flogin_caption_pwd': 'pwd',
						'speed_class' : speed_cl,
						'extra_class' : extra_cl,
						'type' : dsearchmodule['opts']['typesrch'],
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
				cffile[i]['valid_verbose'] = ''
				if(cffile[i]['valid'] == 1):
					cffile[i]['valid_verbose'] = 'checked=yes'
				count = count + 1
				sel_speedopt_tmp = copy.deepcopy(self.selectable_speedopt)	
				sel_speedopt_tmp[cffile[i]['speed_class']-1][2] = 'selected'
				sel_extraopt_tmp = copy.deepcopy(self.selectable_extraopt)	
				sel_extraopt_tmp[cffile[i]['extra_class']][2] = 'selected'
				cffile[i]['selspeed_sel'] =  sel_speedopt_tmp
				cffile[i]['selextra_sel'] =  sel_extraopt_tmp

		
		sel_speedopt_basic = copy.deepcopy(self.selectable_speedopt)	
		sel_speedopt_basic[0][2] = 'selected'
		sel_extraopt_basic = copy.deepcopy(self.selectable_extraopt)	
		sel_extraopt_basic[0][2] = 'selected'
		
		count_ds=0
		cdsfile_toshow1 = []
		for i in xrange(len(cdsfile)):
			if(cdsfile[i]['type'] == 'DSN'):
				cdsfile_toshow = copy.deepcopy(cdsfile[i])
				cdsfile_toshow['idx'] =  count_ds
				cdsfile_toshow['valid_verbose'] = ''
				if(cdsfile_toshow['valid'] == 1):
					cdsfile_toshow['valid_verbose'] = 'checked=yes'			
				count_ds = count_ds + 1
				sel_speedopt_tmp = copy.deepcopy(self.selectable_speedopt)	
				sel_speedopt_tmp[cdsfile[i]['speed_class']-1][2] = 'selected'
				
				sel_extraopt_tmp = copy.deepcopy(self.selectable_extraopt)	
				sel_extraopt_tmp[cdsfile[i]['extra_class']][2] = 'selected'

				cdsfile_toshow['selspeed_sel'] =  sel_speedopt_tmp
				cdsfile_toshow['selextra_sel'] =  sel_extraopt_tmp
				cdsfile_toshow1.append(cdsfile_toshow)
		
		possibleopt=megasearch.listpossiblesearchoptions()
		for slctg in possibleopt:
			if(slctg[0] == genopt['search_default']):
				slctg[2] = 'selected'
		
		tnarray = []
		for ntn in xrange(1,50):
			if(genopt['trends_qty'] == ntn):
				tnarray.append([ ntn, ntn,'selected'])
			else:
				tnarray.append([ntn, ntn,''])
		
		genopt['general_https_verbose']	 = ''
		genopt['general_trend_verbose']	 = ''
		genopt['general_suggestion_verbose']	 = ''
		genopt['smartsearch_verbose']	 = ''
		genopt['max_cache_verbose']	 = ''
		genopt['predb_active_verbose']	 = ''		
		genopt['general_restrictopt1_verbose']	 = ''				
		if(genopt['predb_active'] == 1):
			genopt['predb_active_verbose']	 = 'checked=yes'
		if(genopt['general_https'] == 1):
			genopt['general_https_verbose']	 = 'checked=yes'
		if(genopt['general_restrictopt1'] == 1):
			genopt['general_restrictopt1_verbose']	 = 'checked=yes'
		if(genopt['general_suggestion'] == 1):
			genopt['general_suggestion_verbose']	 = 'checked=yes'
		if(genopt['general_trend'] == 1):
			genopt['general_trend_verbose']	 = 'checked=yes'
		if(genopt['smartsearch'] == 1):
			genopt['smartsearch_verbose']	 = 'checked=yes'
		if(genopt['cache_active'] == 1):
			genopt['cache_active_verbose']	 = 'checked=yes'
		genopt['general_ipaddress_verbose']	 = 'AUTO'
		if(genopt['general_ipaddress'] != ''):
			genopt['general_ipaddress_verbose'] = genopt['general_ipaddress']


		openshift_install = False
		if(len(self.dirconf_oshift)):
			openshift_install = True
		return render_template('config.html', cfg=cffile, cfg_dp=cdsfile_toshow1,  cnt=count,  cnt_ds=count_ds, genopt = genopt, 
											  selectable_opt = possibleopt,
											  sel_speedopt_basic = sel_speedopt_basic,
											  sel_extraopt_basic = sel_extraopt_basic,
											  openshift_install = openshift_install,
											  tnarray = tnarray,
											  cdomainname = cdomainname,
 											  cnt_max=MAX_PROVIDER_NUMBER, cfg_bi=cffileb)


	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	def refresh(self):
		self.read_conf_general()
		self.read_conf_custom()		
		self.read_conf_deepsearch()

	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
	
	def edit_config(self):
		self.refresh()
		webbuf_body_bi = self.html_editpage()		
		return webbuf_body_bi
		


