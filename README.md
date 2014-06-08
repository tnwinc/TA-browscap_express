App: TA-browscap_express
Author: Robert Labrie, The Network Inc

This technology add-on provides a dynamic lookup to add fields to user 
agent (browser) data. It is a re-write of the TA-browscap add-on by
David Shpritz. The data is provcided by the Broser Capabilities Project. The
parser is a re-write of the parser in the pybrowscap library. This add-on is
faster than other browscap based projects, because it maintains a cache of
previously matched user agent strings. This significantly improves the time
for subsequent lookups, without sacrificing accuracy.

http://browscap.org/
http://pypi.python.org/pypi/pybrowscap/

All fields in the browscap file are included
ua_activexcontrols=true/false
ua_agentid=The unique ID of the user agent in the BrowsCapCSV
ua_alpha=true/false
ua_aolversion=AOL version, or 0 if not applicable
ua_backgroundsounds=true/false
ua_beta=true/false
ua_browser=The browser family: FireFox, Chrome, IE, etc
ua_comment=Browser + version
ua_cookies=true/false
ua_crawler=true/false - true if the UA is some Web Crawler
ua_cssversion=CSS version support
ua_frames=true/false
ua_iframes=true/false
ua_ismobiledevice=true/false
ua_issyndicationreader=true/false
ua_javaapplets=true/false
ua_javascript=true/false
ua_litemode <-- I don't know what this means
ua_majorver
ua_masterparent <-- I don't know what this means
ua_minorver
ua_parent <-- I don't know what this means
ua_platform=Operating system and version. Win7, etc
ua_platform_version=The OS version, not the friendly name. Win7 is 6.1
ua_propertyname=The original browscap string which matched the UA
ua_tables=true/false
ua_vbscript=true/false
ua_version=Major.Minor version
ua_win16=true/false
ua_win32=true/false
ua_win64=true/false
ua_fromcache=True if this record was read from cache, false if from the browscap file

| Installation
To install:
1. Untar the TA-browscap.tar.gz file in your $SPLUNK_HOME/etc/apps
   diectory.
2. Change to the $SPLUNK_HOME/etc/apps/TA-browscap/bin directory
3. Download the browscap.csv file from the project:
   wget -O browscap.csv http://browscap.org/stream?q=BrowsCapCSV
4. Restart Splunk.

| Usage
To use:
The lookup expects a field named "http_user_agent". In the search bar,
you can run something like:
index=iis | lookup browscap_lookup_express http_user_agent

This should produce the additional fields.

***THE FIRST FEW SEARCHES WILL BE VERY SLOW***
TA-browscap_express builds a cache of user agents which exist in your data. The
first time a string is encountered, the entire browscap file must be searched.
Subsequent searches will be faster. Be patient while the cache is built. I
suggest using a search limiter like "| head 10", then increasing that number.
In a few minutes, your cache will be populated and the searches will be very
fast.

Not all browsers are cached. Generic and default browsers are deliberately not
cached. To search for browsers which are always looking up in the browscap file
try adding "| search ua_fromcache=false". You can either exlcude these UA
strings at the start, or better, file a bug with the browscap project on github
to get the UA string added to the library.

CHANGE LOG
20130607 v1: 	Initial
