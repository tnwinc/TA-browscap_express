import re
import sys
import csv
import StringIO
import pprint
import os
#this converts an array of keys and an array of values into a dict. Probably
#there is a native Python way to do this. I do PHP. *shrugs*
def data_to_dict(headers, data):
	out = dict()
	for i in range(0,len(data)):
		#print "{} and {}".format(i, data[i])
		x = headers[i]
		x = x.lower()
		x = 'ua_' + x
		out[x] = data[i]
	#pprint.pprint(out)
	return out
	
#the red meat
def browser_lookup(data,http_user_agent):	
	header = data[2]
	defaults = data[3]

	#repackage the header into something useful
	csv_reader = csv.reader( [ header ] )
	for row in csv_reader:
		header = row
	
	#repackage the defaults into something useful
	csv_reader = csv.reader( [ defaults ] )
	for row in csv_reader:
		defaults = row

	#initialize a blank out object with default files
	out = dict()
	out['browser_data_raw'] = defaults
	out['browser_data'] = data_to_dict(header,defaults)
	
	#for short, or unspecified UA strings, just return the default
	if len(http_user_agent) < 2:
		return out

	#best_regex tracks the regex which will eventually be used for a match
	best_regex = ''

	#with the headers handled, start to enumerate data
	for line in data[3:]:
		csv_reader = csv.reader( [ line ] )
		for row in csv_reader:
			bits = row
		
		#convert the browscap string to a regex string. The length
		#comparison solves the problem of finding the "best" match. In the
		#ini file, the best matches come first, but the CSV is a mess.
		#In this case, enumerate the entire file, and the longest regex
		#string will have the most detail and therefore is the best match
		#This logic lifted without shame from pybrowscap
		ua_regex = '^{0}$'.format(re.escape(bits[0]))
		ua_regex = ua_regex.replace('\\?', '.').replace('\\*', '.*?')
		if (re.search(ua_regex,http_user_agent)) and len(ua_regex) > len(best_regex):
			best_regex = ua_regex
			out['browser_data_raw'] = line
			out['browser_data'] = data_to_dict(header,bits)
	return out

#is_known_browser solves the problem of not recording Generic or Default
#browsers. Since the cache file is always checked first, if a generic was
#returned, then results would be skewed and the master file never checked.
def is_known_browser(browser_data):
	out = True
	#Bots start with generic (ie Generic Java Crawler), but browsers have
	#the name first (ie Firefox Generic). The leading space prevents caching
	#generic mainline browsers
	if (" Generic" in browser_data['ua_browser']): out = False
	if ("Default" in browser_data['ua_browser']): out = False
	return out

#
# Main routine - basically it's the standard python recipe for handling
# Splunk lookups
#
if __name__ == '__main__':

	uacache = dict()
	scriptpath = os.path.dirname(os.path.realpath(__file__))
	
	#read the databases into memory
	browscapdata_lite = open(scriptpath + '\\browscap_lite.csv').readlines()
	browscapdata = open(scriptpath + '\\browscap.csv').readlines()

	r = csv.reader(sys.stdin)
	w = csv.writer(sys.stdout)
	have_header = False
	header = []
	idx = -1
	for row in r:
		if (have_header == False):
			header = row
			have_header = True
			z = 0
			for h in row:
				if (h == "http_user_agent"):
					idx = z
				z = z + 1
			w.writerow(row)
			continue

		# We only care about the user-agent field - everything else is filled in
		http_user_agent = row[idx]
		#print "**** " + http_user_agent 

		#check the inmem cache
		if http_user_agent in uacache:
			results = uacache[http_user_agent]
		else:
			#print "check the cache"
			browser_data = browser_lookup(browscapdata_lite,http_user_agent)
			browser_data['browser_data']['ua_fromcache'] = 'true'

			#no mas? check the full dataset
			if (browser_data['browser_data']['ua_browser'] == 'DefaultProperties'):
				#print "checking master"
				browser_data = browser_lookup(browscapdata,http_user_agent)
				browser_data['browser_data']['ua_fromcache'] = 'false'
				if (is_known_browser(browser_data['browser_data'])):
					#write a match back to the currently cached browscapdata_lite and to it's backing file
					browscapdata_lite.append(browser_data['browser_data_raw'])
					with open(scriptpath + '\\browscap_lite.csv','a') as browscap_file:
						browscap_file.write(browser_data['browser_data_raw'])
			results = browser_data['browser_data']
			uacache[http_user_agent] = results
		# Now write it out
		orow = []
		for header_name in header:
			#logtofile('h: ' + header_name)
			if (header_name == "http_user_agent"):
				orow.append(http_user_agent)
			else:
				orow.append(results[header_name])
		w.writerow(orow)
