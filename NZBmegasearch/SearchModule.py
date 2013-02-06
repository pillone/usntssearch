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
import requests
import json
import datetime
import time
import config_settings
import xml.etree.cElementTree as ET
import os
import threading

# Perform a search using all available modules
def performSearch(queryString, configOptions = None):
	# Find search modules
	searchModules = [];
	searchModuleNames = [];
	moduleDir = os.path.join(os.path.dirname(__file__),'SearchModules');
	print 'Loading modules from: ' + moduleDir
	for file in os.listdir(moduleDir):
		if file.endswith('.py') and file != '__init__.py':
			searchModuleNames.append(file[0:-3])
	if len(searchModuleNames) == 0:
		print 'No search modules found.'
		return []
	else:
		print 'Found ' + str(len(searchModuleNames)) + ' modules'
	# Import the modules that the user has enabled
	if configOptions != None:
		pass # Not implemented
	print 'Importing: ' + ', '.join(searchModuleNames)
	try:
		for module in searchModuleNames:
			importedModules = __import__('SearchModules.' + module)
	except Exception as e:
		print 'Failed to import search modules: ' + str(e)
		return []
	
	print 'instantiating module classes'
	# Instantiate the modules
	for module in searchModuleNames:
		try:
			targetClass = getattr(importedModules, module)
			targetClass = getattr(targetClass, module)
		except Exception as e:
			print 'Unable to load search module ' + module + ': ' + str(e)
		
		try:
			searchModules.append(targetClass())
		except Exception as e:
			print 'Error instantiating search module ' + module + ': ' + str(e)
	
	# Perform the search using every module
	global globalResults
	globalResults = []
	threadHandles = []
	lock = threading.Lock()
	for module in searchModules:
		try:
			t = threading.Thread(target=performSearchThread, args=(queryString,module,lock))
			t.start()
			threadHandles.append(t)
		except Exception as e:
			print 'Error starting thread for search module ' + module + ': ' + str(e)

	for t in threadHandles:
		t.join()
	print '=== All Search Threads Finished ==='
	return globalResults
	
def performSearchThread(queryString, module, lock):
	print 'starting search thread'
	localResults = module.search(queryString)
	lock.acquire()
	globalResults.append(localResults)
	try:
		lock.release()
	except Exception as e:
		print e

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
		self.queryURL = ''
		self.baseURL = ''
		self.nzbDownloadBaseURL = ''
		self.apiKey = ''
	# Perform a search using the given query string
	def search(self, queryString):
		raise NotImplementedException('This scraper does not have a search function.')
