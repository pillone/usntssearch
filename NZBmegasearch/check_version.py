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

def chk(version_here): 
	verify_str = '80801102808011028080110280801102'
	url_versioning = 'https://raw.github.com/pillone/usntssearch/master/NZBmegasearch/vernum.num'
	try:
		http_result = requests.get(url=url_versioning)
		#~ print http_result.text
		vals = http_result.text.split(' ')
		cur_ver = float(vals[1])
		if(vals[0] == verify_str):
			print '>> Newest version available is ' + (vals[1])

		if(version_here < cur_ver):
			print '>> A newer version is available. User notification on.'
			return 1
		else:
			if(version_here == cur_ver):
				print '>> This is the newest version available'
			return 0	

	except Exception as e:
		print e
		cur_ver = -1
