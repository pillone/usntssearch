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
import ConfigParser
from SearchModule import *

# Search on Newznab
class ad_NZBclub(SearchModule):
	# Set up class variables
	def __init__(self, configFile=None):
		super(ad_NZBclub, self).__init__()
		# Parse config file		
		self.name = 'NZBClub'
		self.typesrch = 'CLB'
		self.queryURL = 'https://www.nzbclub.com/nzbfeed.aspx'
		self.baseURL = 'https://www.nzbclub.com'
		self.active = 1
		self.builtin = 1
		self.login = 0
	# Perform a search using the given query string
	def search(self, queryString, cfg):		
		urlParams = dict(q =queryString,
            ig= 1,
            rpp= 200,
            st= 5,
            sp= 1,
            ns= 1	)
            
		try:
			http_result = requests.get(url=self.queryURL, params=urlParams, verify=False, timeout=cfg['timeout'])
		except Exception as e:
			print e
			return []
		data = http_result.text
		data = data.replace("<newznab:attr", "<newznab_attr")
		parsed_data = []
			
		#~ parse errors
		try:
			tree = ET.fromstring(data.encode('utf-8'))
		except BaseException:
			print "ERROR: Wrong API?"
			return parsed_data
		except Exception as e:
			print e
			return parsed_data

		#~ successful parsing
		for elem in tree.iter('item'):
			elem_title = elem.find("title")
			elem_url = elem.find("enclosure")
			elem_pubdate = elem.find("pubDate")
			len_elem_pubdate = len(elem_pubdate.text)
			#~ Tue, 22 Jan 2013 17:36:23 +0000
			#~ removes gmt shift
			elem_postdate =  time.mktime(datetime.datetime.strptime(elem_pubdate.text[0:len_elem_pubdate-6], "%a, %d %b %Y %H:%M:%S").timetuple())
			elem_poster = ''
			
			for attr in elem.iter('newznab_attr'):
				if('name' in attr.attrib):
					if (attr.attrib['name'] == 'poster'): 
						elem_poster = attr.attrib['value']

			d1 = { 
				'title': elem_title.text,
				'poster': elem_poster,
				'size': int(elem_url.attrib['length']),
				'url': elem_url.attrib['url'],
				'filelist_preview': '',
				'group': '',
				'posting_date_timestamp': float(elem_postdate),
				'release_comments': '',
				'ignore':0,
				'provider':self.baseURL,
				'providertitle':self.name
			}
			parsed_data.append(d1)
		return parsed_data		
