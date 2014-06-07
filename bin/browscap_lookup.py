import re
import sys
import csv
import StringIO
import pprint

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
def logtofile(msg):
	with open('b.log','a') as f:
		f.write(msg + '\n')
#the red meat
def browser_lookup(datafile,http_user_agent):	
	#logtofile('starting ' + http_user_agent)
	with open(datafile, 'r') as f:
		junk = f.readline()	#first line is junk
		junk = f.readline() #second line is junk
		header = f.readline() #third line is headers
		defaults = f.readline() #fourth line is defaults

		#repackage the header into something useful
		csv_reader = csv.reader( [ header ] )
		for row in csv_reader:
			header = row
		
		#repackage the defaults into something useful
		out = dict()
		out['browser_data_raw'] = defaults
		csv_reader = csv.reader( [ defaults ] )
		for row in csv_reader:
			defaults = row
		out['browser_data'] = data_to_dict(header,defaults)
		#the rest of the file
		best_regex = ''
		
		for line in f:
			csv_reader = csv.reader( [ line ] )
			for row in csv_reader:
				bits = row
			#print bits[0]
			ua_regex = '^{0}$'.format(re.escape(bits[0]))
			ua_regex = ua_regex.replace('\\?', '.').replace('\\*', '.*?')
			if (re.search(ua_regex,http_user_agent)) and len(ua_regex) > len(best_regex):
				best_regex = ua_regex
				#out = dict()
				out['browser_data_raw'] = line
				out['browser_data'] = data_to_dict(header,bits)
				#return out
				
				#browser_data_raw = line
				#print ua_regex + " " + browser_data_raw
				#baz = data_to_dict(header,browser_data)
		out['browser_data']['ua_fromcache'] = 'true'
		return out


def is_known_browser(browser_data):
	out = True
	#if (browser_data['ua_version'] == '0.0'): out = False
	if (" Generic" in browser_data['ua_browser']): out = False
	if ("Default" in browser_data['ua_browser']): out = False
	return out

#
# Main routine - basically it's the standard python recipe for handling
# Splunk lookups
#
if __name__ == '__main__':

    # init the browscap class
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
		#check the cache
	#print "checking cache"
	browser_data = browser_lookup('browscap_lite.csv',http_user_agent)

	#no mas? check the full dataset
	if (browser_data['browser_data']['ua_browser'] == 'DefaultProperties'):
		#print "checking master"
		browser_data = browser_lookup('browscap.csv',http_user_agent)
		browser_data['browser_data']['ua_fromcache'] = 'false'
		#pprint.pprint(browser_data['browser_data'])
		if (is_known_browser(browser_data['browser_data'])):
			#print browser_data['browser_data_raw']
			with open('browscap_lite.csv','a') as browscap_file:
				browscap_file.write(browser_data['browser_data_raw'])
		
	#pprint.pprint(browser_data['browser_data'])

	#results = get_browser_info(browscap, http_user_agent)
	results = browser_data['browser_data']
	#logtofile('building output')
	#logtofile(results)
        # Now write it out
        orow = []
        for header_name in header:
            #logtofile('h: ' + header_name)
            if (header_name == "http_user_agent"):
                orow.append(http_user_agent)
            else:
                orow.append(results[header_name])
        w.writerow(orow)
	#logtofile('we have a winner!')