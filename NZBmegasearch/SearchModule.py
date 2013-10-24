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
import requests
import json
import sys
import datetime
import time
import config_settings
import xml.etree.ElementTree
import xml.etree.cElementTree as ET
import os
import copy
import threading
import re
import logging
import unicodedata

log = logging.getLogger(__name__)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
def resource_path(relative_path):
	dirconf_oshift =  os.getenv('OPENSHIFT_DATA_DIR', '')
	dirconf_local = os.path.dirname(os.path.realpath(__file__))+'/'
	if getattr(sys, 'frozen', False):
		dirconf_local = os.path.dirname(sys.executable)+'/'

	try:
		base_path = sys._MEIPASS
	except Exception:
        #~ base_path = os.path.abspath(".")
		base_path = os.path.abspath(dirconf_local)

	if(len(dirconf_oshift)):
		dirconf = dirconf_oshift
		base_path = os.path.abspath(".")
	else:
		dirconf = 	dirconf_local
        
	retstr = os.path.join(base_path, relative_path)    

	if(len(dirconf_oshift)):
		retstr = os.path.join(base_path+'/wsgi/usntssearch/NZBmegasearch/' , relative_path)    

	return retstr
    
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	
def loadSearchModules(moduleDir = None):
	global loadedModules
	loadedModules = [];
	searchModuleNames = [];
	if moduleDir == None:
		moduleDir = resource_path('SearchModules/')
	#~ print '>> Loading modules from: ' + moduleDir
	for file in os.listdir(moduleDir):
		if file.endswith('.py') and file != '__init__.py':
			searchModuleNames.append(file[0:-3])
	if len(searchModuleNames) == 0:
		#~ print '>> No search modules found.'
		return
	#~ else:
		#~ print '>> Found ' + str(len(searchModuleNames)) + ' modules'
		
	searchModuleNames = sorted(searchModuleNames)
	path = list(sys.path)
	sys.path.insert(0, moduleDir)

	# Import the modules that the user has enabled
	#~ mssg = '>> Importing: ' + ', '.join(searchModuleNames)
	#~ print mssg
	#~ log.info (mssg)

	try:
		for module in searchModuleNames:
			importedModules = __import__('SearchModules.' + module)
	except Exception as e:
		mssg = 'Failed to import search modules: ' + str(e)
		print mssg
		log.critical (mssg)
		return
	
	#~ print 'instantiating module classes'
	# Instantiate the modules
	for module in searchModuleNames:
		try:
			targetClass = getattr(importedModules, module)
			targetClass = getattr(targetClass, module)
		except Exception as e:
			print 'Unable to load search module ' + module + ': ' + str(e)
		
		try:
			loadedModules.append(targetClass())
		except Exception as e:
			print 'Error instantiating search module ' + module + ': ' + str(e)

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	
# Perform a search using all available modules
def performSearch(queryString,  cfg, dsearch=None, extraparam=None):
		
	queryString = queryString.strip()
	queryString = sanitize_strings(queryString)
	#~ print queryString
	
	# Perform the search using every module
	global globalResults
	if 'loadedModules' not in globals():
		loadSearchModules()
	globalResults = []
	threadHandles = []
	lock = threading.Lock()

	#~ prepare cpy modules (thread safety), not nice
	neededModules = []
	neededModules_LUT = [None]*len(cfg)
	for index in xrange(len(cfg)):
		for module in loadedModules:
			if( module.typesrch == cfg[index]['type']):
				neededModules.append(copy.copy(module))
				neededModules_LUT[index] = len(neededModules)-1

	#~ for SB autodiscovery, uses all the possible providers
	if (extraparam is not None):
		for index in xrange(len(cfg)):
			rval = (neededModules[index].api_catsearch and cfg[index]['valid'] > 0)
			if (neededModules_LUT[index] is None):
				rval = False	

			if(rval == True):
				try:
					module_idx = neededModules_LUT[index]
					t = threading.Thread(target=performSearchThreadRaw, args=(extraparam,neededModules[module_idx],lock,cfg[index]))
					t.start()
					threadHandles.append(t)
				except Exception as e:
					print 'Error starting raw apisearch thread  : ' + str(e)
		if(dsearch is not None):
			for index in xrange(len(dsearch.ds)):
				if(dsearch.ds[index].cur_cfg['valid'] == 1):
					try:
						t = threading.Thread(target=performSearchThreadDSRaw, args=(extraparam,lock,dsearch.ds[index]))
						t.start()
						threadHandles.append(t)
					except Exception as e:
						print 'Error starting raw deepsearch thread  : ' + str(e)			

	else:
	#~ for standard search
		for index in xrange(len(cfg)):
			rval = False
			if (((dsearch is not None) and (cfg[index]['valid'] == 2)) or (cfg[index]['valid'] == 1)):
				rval = True	
			if (neededModules_LUT[index] is None):
				rval = False	
			
			if(rval == True):
				try:
					module_idx = neededModules_LUT[index]
					t = threading.Thread(target=performSearchThread, args=(queryString,neededModules[module_idx],lock,cfg[index]))
					t.start()
					threadHandles.append(t)
				except Exception as e:
					print 'Error starting thread  : ' + str(e)

		if(dsearch is not None):
			for index in xrange(len(dsearch.ds)):
				if(dsearch.ds[index].cur_cfg['valid'] == 1):
					try:
						t = threading.Thread(target=performSearchThreadDS, args=(queryString,lock,dsearch.ds[index]))
						t.start()
						threadHandles.append(t)
					except Exception as e:
						print 'Error starting deepsearch thread  : ' + str(e)


	for t in threadHandles:
		t.join()

	return globalResults


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

def sanitize_html(value):
	if(len(value)):		
		value = value.replace("<\/b>", "").replace("<b>", "").replace("&quot;", "").replace("&lt;", "").replace("&gt;", "").replace("&amp;", "'")
	return value

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
		
def sanitize_strings(value):
	if(len(value)):
		value = sanitize_html(value).lower()
		if(isinstance(value, unicode)):
			value = unicodedata.normalize('NFKD',value).encode('ascii', 'ignore')
		value = re.compile("[^A-Za-z0-99]").sub(" ",value)
		value = " ".join(value.split()).replace(" ", ".") 
		#~ print value
	return value

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	


def performSearchThreadRaw(extraparam, neededModule, lock, cfg):
	
	localResults = neededModule.search_raw(extraparam, cfg)
	lock.acquire()
	globalResults.append(localResults)

	try:
		lock.release()
	except Exception as e:
		print e
 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	

	
def performSearchThread(queryString, neededModule, lock, cfg):
	
	localResults = neededModule.search(queryString, cfg)
	lock.acquire()
	globalResults.append(localResults)
	
	try:
		lock.release()
	except Exception as e:
		print e
 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	
def performSearchThreadDS(queryString, lock, dsearch_one):
	
	localResults = dsearch_one.search(queryString)
	lock.acquire()
	globalResults.append(localResults)

	try:
		lock.release()
	except Exception as e:
		print e

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
	
def performSearchThreadDSRaw(extraparam, lock, dsearch_one):
	
	
	localResults = dsearch_one.search_cat(extraparam)
	lock.acquire()
	globalResults.append(localResults)

	try:
		lock.release()
	except Exception as e:
		print e
  
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

# Exception to be raised when a search function is not implemented
class NotImplementedException(Exception):
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)

# All search modules inherit from this class
class SearchModule(object):
	# Set up class variables
	def __init__(self):
		self.name = 'Unnamed'
		self.queryURL = ''
		self.baseURL = ''
		self.nzbDownloadBaseURL = ''
		self.apiKey = ''
		self.default_retcode=[200, 'Ok', 0, 'none']


	# Show the configuration options for this module
	def configurationHTML(self):
		return ''

	# Perform a search using the given query string
	def search(self, queryString):
		raise NotImplementedException('This scraper does not have a search function.')



	#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

	def parse_xmlsearch(self, urlParams, tout, tcfg = None): 
		parsed_data = []
		#~ print self.queryURL  + ' ' + urlParams['apikey']
		timestamp_s = time.time()

		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=tout, headers= self.agent_headers)
					
		except Exception as e:
			log.critical(self.queryURL + ' -- ' + str(e))
			if(tcfg is not  None):
				tcfg['retcode'] = [600, 'Server timeout', tout, self.name]
			return parsed_data
			
		timestamp_e = time.time()	
		#~ print "NABAPI " + self.queryURL + " " + str(timestamp_e - timestamp_s)
		log.info('TS ' + self.baseURL + " " + str(timestamp_e - timestamp_s))
							
		data = http_result.text
		data = data.replace("<newznab:attr", "<newznab_attr")

		try:
			tree = ET.fromstring(data.encode('utf-8'))
		except Exception as e:
			print e
			return parsed_data

		#~ successful parsing
		for elem in tree.iter('item'):
			category_found= {}

			elem_title = elem.find("title")
			elem_url = elem.find("enclosure")
			elem_pubdate = elem.find("pubDate")
			elem_guidattr = elem.find("newznab_attsr")
 
			len_elem_pubdate = len(elem_pubdate.text)
			#~ Tue, 22 Jan 2013 17:36:23 +0000
			#~ removes gmt shift
			elem_postdate =  time.mktime(datetime.datetime.strptime(elem_pubdate.text[0:len_elem_pubdate-6], "%a, %d %b %Y %H:%M:%S").timetuple())
			elem_poster = ''

			elem_guid = elem.find("guid")
			release_details = ''					
			for attr in elem.iter('newznab_attr'):
				if('name' in attr.attrib):
					if (attr.attrib['name'] == 'guid'): 
						release_details  = self.baseURL + '/details/' + attr.attrib['value']
					if (attr.attrib['name'] == 'poster'): 
						elem_poster = attr.attrib['value']
					if (attr.attrib['name'] == 'category'):
						val = attr.attrib['value']
						if(val in self.category_inv):
							category_found[self.category_inv[val]] = 1
						#~ print elem_title.text	
						#~ print val	
						#~ print category_found
						#~ print '=========='
			if(len(category_found) == 0):
				category_found['N/A'] = 1

			if(len(release_details) == 0):
				if(elem_guid is not None):
					release_details = elem_guid.text
				else:
					release_details = self.baseURL	
			
			d1 = { 
				'title': elem_title.text,
				'poster': elem_poster,
				'size': int(elem_url.attrib['length']),
				'url': elem_url.attrib['url'],
				'filelist_preview': '',
				'group': '',
				'posting_date_timestamp': float(elem_postdate),
				'release_comments': release_details,
				'categ':category_found,
				'ignore':0,
				'provider':self.baseURL,
				'providertitle':self.name
			}

			parsed_data.append(d1)
			
		
		#~ that's dirty but effective
		if(tcfg is not  None):
			returncode = self.default_retcode
			if(	len(parsed_data) == 0 and len(data) < 300):
				returncode = self.checkreturn(data)
			returncode[2] = timestamp_e - timestamp_s
			returncode[3] = self.name
			tcfg['retcode'] = copy.deepcopy(returncode)

		return parsed_data		

