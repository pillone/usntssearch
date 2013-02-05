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

from ConfigParser import SafeConfigParser
import sys
MAX_PROVIDER_NUMBER = 10


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def	write_conf(request_form):
	parser = SafeConfigParser()

	numserver=0
	for i in xrange(MAX_PROVIDER_NUMBER):
		if(request_form['host%d' % i].replace(" ", "")) :
			numserver = numserver + 1
	parser.add_section('general')
	parser.set('general', 'numserver', str(numserver))
#~ 
	counter = 1
	for i in xrange(MAX_PROVIDER_NUMBER):
		if(request_form['host%d' % i].replace(" ", "")): 
			parser.add_section('search_provider%s' % counter)
			parser.set('search_provider%s' % counter, 'url',request_form['host%d' % i].replace(" ", ""))
			parser.set('search_provider%s' % counter, 'api',request_form['API%d' % i].replace(" ", ""))
			parser.set('search_provider%s' % counter, 'type', request_form['type%d' % i].replace(" ", ""))
			#~ if (has_key('host%dactive' % i) in request_form == True):
			if (request_form.has_key('host%dactive' % i)  == True):
				parser.set('search_provider%s' % counter, 'valid', '1')
			else:
				parser.set('search_provider%s' % counter, 'valid', '0')
			counter = counter + 1

	#~ parser.write(sys.stdout)
	with open('settings.ini', 'wt') as configfile:
		parser.write(configfile)
   

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
     
def read_conf(): 
	cfg_struct = []
	parser = SafeConfigParser()		
	parser.read('settings.ini')
	numserver = parser.get('general', 'numserver')

	for i in xrange(int(numserver)):
		d1 = {'url': parser.get('search_provider%d' % (i+1)  , 'url'),
			  'type': parser.get('search_provider%d' % (i+1)  , 'type'),
			  'api': parser.get('search_provider%d' % (i+1)  , 'api'),
			  'valid': parser.get('search_provider%d' % (i+1)  , 'valid'),
			  }
		cfg_struct.append(d1)	  
	
	return(cfg_struct)


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

			
def html_head(): 
			
	buf = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
	buf = buf+'<html xmlns="http://www.w3.org/1999/xhtml">\n'
	buf = buf+'<head>\n'
	buf = buf+'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
	buf = buf+'<title>NZB MegasearcH</title>\n'
	buf = buf+'<style type="text/css">\n'
	buf = buf+'<!--\n'
	buf = buf+'@import url("static/style.css");\n'
	buf = buf+'-->\n'
	buf = buf+'</style>\n'
	buf = buf+'</head>\n'
	buf = buf+'<body>\n'
	buf = buf+'<form action="/" method="post">\n'	
	return buf	

def html_foot(): 	
	buf = '<div style="margin: 45px">'
	buf = buf +'<input type="submit" value="Save" style = "width: 80px; font: bold 16px \'Lucida Sans Unicode\', \'Lucida Grande\', Sans-Serif; ">\n'
	buf = buf + '<input type="button" style = "width: 80px; font: 16px \'Lucida Sans Unicode\', \'Lucida Grande\', Sans-Serif; " value="Cancel" onclick="location.href=\'\/\';">\n'
	buf = buf + '</div>'
	buf = buf+ '</form></body></html>\n'	
	
	return buf
	
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

    
def html_output(cffile): 

	buf= ''
	#~ default search providers
	option0='checked="yes"'
	option1=option0
	if(cffile[0]['valid'] == '0'):
		option0=''
	if(cffile[1]['valid'] == '0'):
		option1=''		

	buf = buf + '<table id="hor-minimalist-b" summary="Config"><thead>\n'
	buf = buf+'<tr><th scope="col">Specially supported engines</th></tr></thead><tbody>\n'
	buf = buf+'<tr>\n'	
	buf = buf+'<td><input type="checkbox" name="host0active" id="host0" value="1" size="40" %s> %s\n' % (option0,cffile[0]['url'])
	buf = buf+'<input type="hidden" name="host0" id="host0" value="%s" size="40">\n' % cffile[0]['url']
	buf = buf+'<input type="hidden" name="API0" id="API0" value="%s" size="40">\n' % cffile[0]['api']
	buf = buf+'<input type="hidden" name="type0" id="type0" value="%s" size="40"></td>\n' % cffile[0]['type']
	buf = buf+'</tr>\n'	
	buf = buf+'<tr>\n'	
	buf = buf+'<td><input type="checkbox" name="host1active" id="host1" value="1" size="40" %s> %s \n'  % (option1,cffile[1]['url'])
	buf = buf+'<input type="hidden" name="host1" id="host1" value="%s" size="40">\n' % cffile[1]['url']
	buf = buf+'<input type="hidden" name="API1" id="API1" value="%s" size="40">\n' % cffile[1]['api']
	buf = buf+'<input type="hidden" name="type1" id="type1" value="%s" size="40"></td>\n' % cffile[1]['type']
	buf = buf+'</tr>\n'
	buf = buf+'</tbody></table>'

	buf = buf + '<table id="hor-minimalist-b" summary="Config"><thead>\n'
	buf = buf+'<tr><th scope="col">Newznab Host</th><th scope="col" >API</th></tr></thead><tbody>\n'

	for i in xrange(2,MAX_PROVIDER_NUMBER):
		surl = ''
		sapi = ''

		if(i < len(cffile) ):
			if(cffile[i]['type'] == 'NAB' ):
				surl = cffile[i]['url']
				sapi = cffile[i]['api']
		
		buf = buf+'<tr>\n'
		buf = buf+'<td><input type="text" name="host%d" id="host" value="%s" size="40"></td>\n' % (i,surl)
		buf = buf+'<td><input type="text" name="API%d" id="API" value="%s" size="40">\n' % (i,sapi)
		buf = buf+'<input type="hidden" name="type%d" id="type%d" value="NAB" size="40">\n' % (i,i)
		buf = buf+'<input type="hidden" name="host%dactive" id="host%dactive" value="1" size="40"></td>\n' % (i,i)		
		buf = buf+'</tr>\n'
	 
	buf = buf+'</tbody></table>'	
	return buf


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 


def config_read():
	cf = read_conf()
	webbuf_head = html_head()
	webbuf_body = html_output(cf)
	webbuf_foot = html_foot()	
	webbuf_ret = webbuf_head+webbuf_body+webbuf_foot	
	return webbuf_ret


#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def config_write(request_form):
	write_conf(request_form)	
	#~ return config_read()

if __name__ == "__main__":
	#~ debug
	cf = read_conf()
	print cf

	webbuf_head = html_head()
	webbuf_body = html_output(cf)
	webbuf_foot = html_foot()	
	webbuf_ret = webbuf_head+webbuf_body+webbuf_foot	
	
	myFile = open('results.html', 'w')
	myFile.write(webbuf_ret)
	myFile.close()
	
