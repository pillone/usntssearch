import search_scrappers
import decimal
import datetime
import time
import dateutil.relativedelta
from operator import itemgetter

from BeautifulSoup import BeautifulSoup

def sanitize_html(value):
	VALID_TAGS = []
	soup = BeautifulSoup(value.replace("<\/b>", ""))

	for tag in soup.findAll(True):
		if tag.name not in VALID_TAGS:
			tag.hidden = True
	
	return soup.renderContents()
 
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def summary_results(results):
	
	#~ sanitize
	for provid in xrange(len(results)):
		for i in xrange(len(results[provid])):
			results[provid][i]['title'] = sanitize_html(results[provid][i]['title'])

	#~ search one on top of the other
	#~ success is nospace matching on top of the other.
	for provid in xrange(len(results)):
		for z in xrange(len(results[provid])):
			for providj in xrange(provid+1,len(results)):
				for i in xrange(len(results[providj])):
					#~ print results[providj][i]['title']
					#~ print results[provid][z]['title']
					#~ print providj
					#~ print provid
					#~ print z
					#~ print i
					#~ print ret
					ret = results[providj][i]['title'].find( results[provid][z]['title'])
					if(ret != -1):
						#~ print 'duplicate ==========' 
						results[providj][i]['ignore'] = 1
					#~ print '))))))))))))))))' 
	return results
			
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

def summary_results2(results,results_provid,strsearch):
	
	#~ sanitize
	for provid in xrange(len(results)):
		for i in xrange(len(results[provid])):
			results[provid][i]['title'] = sanitize_html(results[provid][i]['title'])

	results2 =[]
	ptr = []
	#~ all in one array
	#~ success is nospace matching on top of the other.
	for provid in xrange(len(results)):
		for z in xrange(len(results[provid])):
			results[provid][z]['provider'] = results_provid[provid]
			results2.append(results[provid][z])
			ptr.append([provid, z])
	
	strsearch1 = strsearch.replace(" ", ".")
	
	print "Processing data..."	
	results2 = sorted(results2, key=itemgetter('posting_date_timestamp'), reverse=True) 	
	for z in xrange(len(results2)):
		#~ print results2[z]['title']
		findone = 0
		if(results2[z]['title'].lower().find( strsearch.lower() ) != -1):
			findone = 1
		if(results2[z]['title'].lower().find( strsearch1.lower()) != -1 ):
			findone = 1 
	
		#~ check same name, == takes too much time
		#~ for j in xrange(z+1,len(results2)):	
			#~ ret = results2[z]['title'].lower().find( results2[j]['title'].lower())			
			#~ if(ret == -1):
				#~ findone = 0 
		results2[z]  ['ignore'] = 0			
		#~ then update
		if(findone==0):
			results[ptr[z][0]] [ ptr[z][1] ] ['ignore'] = 1		
			results2[z]  ['ignore'] = 1		
		#~ resultsn[ptr[z][0]] = 	results[ptr[z][0]] [ ptr[z][1] ]
		#~ print results2[z]['title']
		#~ print findone
			

	
	return results2
			
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

			
def html_head(): 
			
	buf = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
	buf = buf+'<html xmlns="http://www.w3.org/1999/xhtml">\n'
	buf = buf+'<head>\n'
	buf = buf+'<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
	buf = buf+'<title>NZB MegasearcH - 0byte</title>\n'
	buf = buf+'<style type="text/css">\n'
	buf = buf+'<!--\n'
	buf = buf+'@import url("/static/style.css");\n'
	buf = buf+'-->\n'
	buf = buf+'</style>\n'
	buf = buf+'<script src="/static/overlay.js"></script>'
	buf = buf+'</head>\n'
	buf = buf+'<body>\n'	
	buf = buf+'<span id="loader" style="visibility:hidden;"><img src="static/loadingicon.gif" width="75" height="75" /></span>'
	buf = buf+'<form action="/s" method="get"  class="form-wrapper-01">'		
	buf = buf+'<input type="text" id="search" placeholder="Enter your keyword" name="q"><input type="submit" value="Search" id="submit" onclick="show_loader()">'
	buf = buf+'</form>'	
	buf = buf + '<table id="hor-minimalist-b" summary="Search Results"><thead>\n'
	buf = buf+'<tr><th scope="col" class=titlecell>Title</th><th scope="col" class=sizecell>Size</th> <th scope="col" class=datecell>Age</th> <th scope="col" class=providercell>Prov</th> </tr></thead><tbody>\n'
	return buf	

def html_foot(): 	 

	buf =  '</tbody></table>'
	buf =  buf+ '<div class="topright">'
	buf =  buf+ '<a href= "config">Configure</a></div>'
	buf =  buf+ '</body></html>\n'	
	
  

	return buf
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

    
def html_output(results,results_provid): 

	buf= ''
	#~ for provid in xrange(len(results)):
		#~ for i in xrange(len(results[provid])):
	
	for i in xrange(len(results)):
		if(results[i]['ignore'] == 0):
			szf = float(results[i]['size']/1000000.0)
			mgsz = ' MB '
			if (szf > 1000.0): 
				szf = szf /1000
				mgsz = ' GB '
			dt1 =  datetime.datetime.fromtimestamp(results[i]['posting_date_timestamp'])
			dt2 =  datetime.datetime.today()
			rd = dateutil.relativedelta.relativedelta (dt2, dt1)
			#~ approximated date, whatev
			totdays = rd.years * 365  + rd.months * 31  + rd.days
			
			buf = buf+'<tr>\n'
			buf = buf+'<td class=titlecell> <a href= "'+ results[i]['url']+ '"> ' + results[i]['title'] + '</a>'		
			buf = buf+'<td class=sizecell> %.1f' % szf + mgsz + ' </td>\n'
			buf = buf+'<td class=datecell>' + str(totdays) + ' days </td>\n'
			buf = buf+'<td class=providercell>' + results[i]['provider'] + '</td>\n'
			buf = buf+'</tr>\n'
	return buf
#~ 
	#~ myFile = open('results.html', 'w')
	#~ myFile.write(buf)
	#~ myFile.close()
			#~ 
			
#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

    
def dosearch(strsearch, cfg):
	strsearch = strsearch.strip()
#~ strsearch='Hotel.Impossible.S01E01'
	webbuf_head = html_head()
	webbuf_body = ''
	if(len(strsearch)):
		results, results_provid = search_scrappers.search_request(strsearch, cfg)
		results = summary_results2(results,results_provid,strsearch)
		webbuf_body = html_output(results,results_provid)
	webbuf_foot = html_foot()	
	webbuf_ret = webbuf_head+webbuf_body+webbuf_foot	
	return webbuf_ret

#~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 
#~ debug
if __name__ == "__main__":
	print 'Save to file'
	webbuf_ret = dosearch('Hotel.Impossible.S01E01')
	myFile = open('results.html', 'w')
	myFile.write(webbuf_ret)
	myFile.close()



	
