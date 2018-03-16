#!/usr/bin/python
###############################################################################
#
#
#   Handles the actual setting up of the Requests classes
#
#   Takes in a URL and optional headers and fields to be encoded.
#   If the 'get' flag is True, no data is sent the Request builder, and you
#   end up with a GET request instead of a POST request    
#
#   1-9-2018 Added Proxy Support
#
###############################################################################

import requests
import urllib2
import urllib
import cookielib
import mechanize

class pageRequest():
    
    

    
    def __init__(self,url,headers=False,fFields=False,get=False,proxy=False,UA=False):
        self.initURL=url
        self.proxy=proxy
        
#   Set headers if they are provided; otherwise, set basic default headers
        
        if headers:
            self.headers=headers
        elif UA:
            #   User-supplied User Agent?
            self.headers={
                'HTTP_USER_AGENT': UA,
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        else:
            self.headers={
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
#    Set form fields if provided; otherwise, GET method is used
            
        if fFields:
            self.formFields=fFields 
            self.encodedFields=urllib.urlencode(self.formFields)

#    If the GET flag is True, request is a GET request; otherwise, it is a POST request
 
        if get:
            if proxy:
                self.req=urllib2.Request(self.initURL,headers=self.headers)
        else:
            self.req=urllib2.Request(self.initURL,self.encodedFields,self.headers)    
            
    def __call__(self):
        
#   Option to call the URL with less sophisticated method
        
        
        return urllib2.urlopen(self.req)

class pageRequestMech():
    # proxy = {'http':ip:port}
    def __init__(self,headers=False,fFields=False,get=False,proxy=False,UA=False):
        self.proxy=proxy
        
#   Set headers if they are provided; otherwise, set basic default headers
        
        if headers:
            self.headers=headers
        elif UA:
            #   User-supplied User Agent?
            self.headers={
                'HTTP_USER_AGENT': UA,
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        else:
            self.headers={
                'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
#    Set form fields if provided; otherwise, GET method is used
            
        if fFields:
            self.formFields=fFields 
        br=mechanize.Browser()
        cj=cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        
        # Browser Options
        
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        
        # Follows refresh 0 but not hangs on refresh > 0
        
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        if proxy:
            try:
                br.set_proxies(proxy)
            except:
                raise "Proxy not formatted correctly. Format is {'http':ip:port}"
        headerList=[]
        for key in self.headers.keys():
            headerList.append((key,self.headers[key]))
        br.addheaders=headerList
        
        self.req=br