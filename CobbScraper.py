#!/usr/bin/python
##############################################################################
#
#    Cobb County property data mining script
#
#    12/22/2017 - v1.1
#
#    Implemented zip code
#
#    12/21/2007 - v 1.0
#
#    Main Script
#
#    Mines Cobb County's website and establishes all Property IDs for querying 
#    their websites. Property IDs are pushed back to Cobb County's website, and
#    the address and last sale date/value, if available are grabbed.
#
#    The script then attempts to load cobbProps.dat as old data and further
#    build up the database.
#
#    
#############################################################################



import requests
import urllib2
import urllib
from residential import resProp
from bs4 import BeautifulSoup
import re
import time
import pickle
import cookielib
from time import sleep
from StringIO import StringIO
import gzip
from browser import pageRequest



def printToFile(htmlText,fileName="temp.html"):
    with open(fileName,"wb") as f:
        f.write(htmlText)
    f.close()

###############################################################################
#
#
#   Form Field generator for the PID search ONLY
#   Probably can be deprecated
#
###############################################################################

def fFieldGen(pid=False,add=False):
    if pid!=False:
        FormFields = (
        	(r'__VSTATE', r'wEPDwUKMTMyMjI2NDUyNA8UKwACZGcWAmYPZBYEAgcPZBYEAgEPDxYCHgdWaXNpYmxlaGQWAmYPZBYCZg9kFgQCAQ9kFgICAQ9kFgICAQ8QZGQWAGQCAw9kFgJmD2QWAmYPPCsADgIAFCsAAmQXAQUIUGFnZVNpemUCCgEWAhYLDwICFCsAAjwrAAUBBAUDSlVSPCsABQEEBQROQU1FZGUUKwAACyl5VGVsZXJpay5XZWIuVUkuR3JpZENoaWxkTG9hZE1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTMuMS40MDMuNDUsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkNAE8KwAHAAspdFRlbGVyaWsuV2ViLlVJLkdyaWRFZGl0TW9kZSwgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxMy4xLjQwMy40NSwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0AWRkZGRmZAIDDw8WAh8AaGRkAggPFCsAAw8WAh4XRW5hYmxlQWpheFNraW5SZW5kZXJpbmdoZGRkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUVUmFkV2luZG93X05hdmlnYXRlVXJs'),
        	(r'__VIEWSTATE',r''),
        	(r'__EVENTVALIDATION',r'wEdAAvvuYnCceePGXnBm008YLT/imrMKsvipVqgAm6eeFqW4HJKYAFO6I0fqTxQsc4lhuw/VBgahKiSYWm0TH20tWytmzXzYHIa1dmXlvkbftBdgwslnNmVQBKtcUYebedL4DIIE4uP8nfiSzXQ9yZdaHxE13z69BI9GFFQ52nNWBw1jGE7wbUKBFGxkg1vsxgrWVeJ/gVz0FNuJTGXAWFWdI3aBWrIxCGTmNcpF4dAhdp4eQ=='),
        	(r'__EVENTTARGET',r''),
        	(r'__EVENTARGUMENT',r''),
        	(r'SortBy',r'FULLADD'),
        	(r'SortDir',r' asc'),
        	(r'PageSize',r'100'),
        	(r'sIndex',r'-1'),
        	(r'hdListType','PA'),
        	(r'inPNumber',''),
        	(r'inpParid',str(pid)),
        	(r'btSearch','Search'),
         (r'selPageSize','100')
        )
        return FormFields
    if add!=False:
        FormFields = (
        	(r'__VSTATE', r'wEPDwUKMTMyMjI2NDUyNA8UKwACZGcWAmYPZBYEAgcPZBYEAgEPDxYCHgdWaXNpYmxlaGQWAmYPZBYCZg9kFgQCAQ9kFgICAQ9kFgICAQ8QZGQWAGQCAw9kFgJmD2QWAmYPPCsADgIAFCsAAmQXAQUIUGFnZVNpemUCCgEWAhYLDwICFCsAAjwrAAUBBAUDSlVSPCsABQEEBQROQU1FZGUUKwAACyl5VGVsZXJpay5XZWIuVUkuR3JpZENoaWxkTG9hZE1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTMuMS40MDMuNDUsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkNAE8KwAHAAspdFRlbGVyaWsuV2ViLlVJLkdyaWRFZGl0TW9kZSwgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxMy4xLjQwMy40NSwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0AWRkZGRmZAIDDw8WAh8AaGRkAggPFCsAAw8WAh4XRW5hYmxlQWpheFNraW5SZW5kZXJpbmdoZGRkZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAQUVUmFkV2luZG93X05hdmlnYXRlVXJs'),
        	(r'__VIEWSTATE',r''),
        	(r'__EVENTVALIDATION',r'wEdAAvvuYnCceePGXnBm008YLT/imrMKsvipVqgAm6eeFqW4HJKYAFO6I0fqTxQsc4lhuw/VBgahKiSYWm0TH20tWytmzXzYHIa1dmXlvkbftBdgwslnNmVQBKtcUYebedL4DIIE4uP8nfiSzXQ9yZdaHxE13z69BI9GFFQ52nNWBw1jGE7wbUKBFGxkg1vsxgrWVeJ/gVz0FNuJTGXAWFWdI3aBWrIxCGTmNcpF4dAhdp4eQ=='),
        	(r'__EVENTTARGET',r''),
        	(r'__EVENTARGUMENT',r''),
        	(r'SortBy',r'FULLADD'),
        	(r'SortDir',r' asc'),
        	(r'PageSize',r'100'),
        	(r'sIndex',r'-1'),
        	(r'hdListType','PA'),
        	(r'inPNumber',''),
        	(r'inpStreet',str(add)),
        	(r'btSearch','Search'),
         (r'selPageSize','100')
        )       
        return FormFields
    
    
        
def findPIDs(pid,inList):
    
#   Recursive function used to pull the website with finer details of PID lists
#   Same as code in main program

        finePID=(pid*10)
        print "Entering finer detail"
        for a in range(finePID,finePID+10):
            cobbMain=pageRequest(url="http://www.cobbassessor.org/cobbga/search/commonsearch.aspx?mode=parid",fFields=fFieldGen(pid=a))
            cobbMainStr=''.join(cobbMain().readlines())
            pagePIDs=re.findall(r'(\d{11}):2017',str(cobbMainStr))                   
            if len(pagePIDs)<100:
                print "Current PID: "+str(a)+" "+str(pagePIDs)
                inList.append(pagePIDs)
            else:
                findPIDs(a,inList)
        return inList
    
if __name__=="__main__":    
    pidList=[]
###############################################################################
#
#    Populate PID list
#
#   Code starts from 1512000000 and goes to 2111300000 using website search
#   
#
##############################################################################
    try:
        open('pids.dat', 'r')
    except:
        print "Generating PID list. This could take a while. Go grab a Starbucks"
        
        for pid in range(1512,2113,1):
            cobbMain=pageRequest(url="http://www.cobbassessor.org/cobbga/search/commonsearch.aspx?mode=parid",fFields=fFieldGen(pid=pid))
            cobbMainStr=''.join(cobbMain().readlines())
        
            #   Searches for PIDs based on regex search
            
            pagePIDs=re.findall(r'(\d{11}):2017',str(cobbMainStr))
            
            #   Less than 100 PIDs? Perfect! Add to list
            
            if len(pagePIDs)<100:
                print "Current PID: "+str(pid)+" "+str(pagePIDs)
           
                for a in pagePIDs:
                    pidList.append(a)
                
                #    Running tally of PID list size
                
                print "Current pid list size: "+str(len(pidList))
                
                #   Sleep for 5 seconds to not buy Cobb Servers
                if len(pagePIDs)>0: time.sleep(5)
                
            else:
                blankList=[]
                
                #   Begin recursion using findPIDs function 
                #   This function continues into itself in the definitino above
                
                pagePIDs=[val for sublist in findPIDs(pid,blankList) for val in sublist]
                for a in pagePIDs:
                    pidList.append(a)
                    
                #   Sleep for 5 seconds after running tally of PID list size
                print "Current pid list size: "+str(len(pidList))+"\n"
                if len(pagePIDs)>0: time.sleep(5)
                
        print "Total number of PIDs: "+len(pidList)
        
        #   Pickle the PID data for later
        
        with open('pids.dat','wb') as f:
            pickle.dump(pidList,f)
        f.close()
    

###############################################################################
#
#
#   Opens the current PIDs data, unpickles, checks for duplicats (set), and
#   adds them to the pids list
#
###############################################################################
        
    f=open('pids.dat','r')
    pids=pickle.load(f)
    pids=list(set(pids))
    pids.sort()




###############################################################################
#
#
#   Build a cookie jar, cookie handler, and build the URL opener
#
###############################################################################
    
    print "There a total of "+str(len(pids))+ " PIDs in Cobb County"
    cookies=cookielib.LWPCookieJar()
    handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
    opener=urllib2.build_opener(*handlers) 

#    Attempt to load property data from available .dat files

    try:
        with open("cobbProps.dat","r+") as cobbProps:
            CobbProperties=pickle.load(cobbProps)
            print "Length of load: "+str(len(CobbProperties.keys()))
    except:
        print "No cobbProps.dat found! Starting from scratch"
        CobbProperties={}
    for i in range(len(pids)):
        
        pid=pids[i]    
        try: 
            CobbProperties[pid]
            print "duplicate"
            continue
        except:
            pass
        #   New cookies each time or else Cobb says you're dumb
        
        cookies=cookielib.LWPCookieJar()
        handlers = [
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        urllib2.HTTPCookieProcessor(cookies)
        ]
        opener=urllib2.build_opener(*handlers) 
    ###############################################################################
    #
    #   
    #   Form fields to start a search with Cobb county using a pid
    #    
    #
    ###############################################################################
        
        fields=(
            	(r'__VSTATE', r'wEPDwUKMTMyMjI2NDUyNA8UKwACZGgWAmYPZBYEAgcPZBYEAgEPDxYCHgdWaXNpYmxlaGQWAmYPZBYCZg9kFgQCAQ9kFgICAQ9kFgICAQ8QZGQWAGQCAw9kFgJmD2QWAmYPPCsADgIAFCsAAmQXAQUIUGFnZVNpemUCCgEWAhYLDwICFCsAAjwrAAUBBAUDSlVSPCsABQEEBQROQU1FZGUUKwAACyl5VGVsZXJpay5XZWIuVUkuR3JpZENoaWxkTG9hZE1vZGUsIFRlbGVyaWsuV2ViLlVJLCBWZXJzaW9uPTIwMTMuMS40MDMuNDUsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49MTIxZmFlNzgxNjViYTNkNAE8KwAHAAspdFRlbGVyaWsuV2ViLlVJLkdyaWRFZGl0TW9kZSwgVGVsZXJpay5XZWIuVUksIFZlcnNpb249MjAxMy4xLjQwMy40NSwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj0xMjFmYWU3ODE2NWJhM2Q0ARYCHgRfZWZzZGQWBB4EX2hsbQsrBAEeCkRhdGFNZW1iZXJlZGZkAgMPDxYCHwBoZGQCCA8UKwADDxYCHhdFbmFibGVBamF4U2tpblJlbmRlcmluZ2hkZGRkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBRVSYWRXaW5kb3dfTmF2aWdhdGVVcmw='),
            	(r'__VIEWSTATE',r''),
            	(r'__EVENTVALIDATION',r'wEdABE1Fug0U+8/JGLteHqvVTNeimrMKsvipVqgAm6eeFqW4HJKYAFO6I0fqTxQsc4lhuw/VBgahKiSYWm0TH20tWytmzXzYHIa1dmXlvkbftBdgwslnNmVQBKtcUYebedL4DIIE4uP8nfiSzXQ9yZdaHxEkpZphq0EWIFvkGxtF05/wLkiZksNPBvlSaCOL8hDFAE/E5bKg5EnTwfrx1uvZsipMT7B4MaPrL7QBFDCtPJDH07Ff7+9mF+A8KMwkLLEOg9iYFK1Ys8u4s3Ki111cEIq13z69BI9GFFQ52nNWBw1jGE7wbUKBFGxkg1vsxgrWVeJ/gVz0FNuJTGXAWFWdI3aBWrIxCGTmNcpF4dAhdp4eQ=='),
            	(r'__EVENTTARGET',r''),
            	(r'__EVENTARGUMENT',r''),
            	(r'SortBy',r'PARID'),
            	(r'SortDir',r' asc'),
            	(r'PageSize',r'15'),
            	(r'sIndex',r'-1'),
            	(r'hdListType','PA'),
            	(r'inpParid',str(pid)),
            	(r'btSearch','Search'),
            	(r'selSortBy',r'PARID'),
            	(r'selSortDir',r' asc'),
            	(r'selPageSize',r'15'),
             (r'selPageSize','100'),
             (r'hdLink',r'../Datalets/Datalet.aspx?sIndex=0&idx=1')
                )
        print "Using "+str(pid)
        cobbClick=pageRequest(url="http://www.cobbassessor.org/cobbga/search/CommonSearch.aspx?mode=PARID",fFields=fields)
        Flag=True
        while Flag:
            try:
                temp=opener.open(cobbClick.req)
                Flag=False
            except:
                sleep(1)

        
    ###############################################################################
    #
    #   Begin Scraping Cobb County Site
    #   Open the page to a given PID's property listing
    #
    ###############################################################################
        headers={
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
            'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml; q=0.9,*/*; q=0.8',
            'Referer': 'http://www.cobbassessor.org/cobbga/search/CommonSearch.aspx?mode=PARID',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        cobbApp=pageRequest(url="http://www.cobbassessor.org/cobbga/Datalets/Datalet.aspx?sIndex=0&idx=1",headers=headers,get=True)
        Flag=True
        while Flag:
            try:
                f=opener.open(cobbApp.req)
                Flag=False
            except:
                sleep(10)
        html=f.read()
        soup=BeautifulSoup(html,"html.parser")

        dataslets=soup.find_all("td",text="Address")
        try:
            for element in dataslets:
                addressTemp=element.find_next_sibling("td")
                address=str(addressTemp.get_text())
                address=re.sub(" +"," ",address)
        except:
            address="No Address Available"
            
        
        dataslets=soup.find_all("td",text="Owner")
        for element in dataslets:
            ownerTemp=element.find_next_sibling("td")
            try:
                owner=str(ownerTemp.get_text())
            except:
                owner="No Owner Available"
                pass
        
        dataslets=soup.find_all("td",text="Class")
        for element in dataslets:
            propClasstemp=element.find_next_sibling("td")
            propClass=str(propClasstemp.get_text())  
            
            
        cobbSales=pageRequest(url="http://www.cobbassessor.org/cobbga/datalets/datalet.aspx?mode=sales&sIndex=0&idx=1&LMparent=20",headers=headers,get=True)
        Flag=True
        while Flag:
           try:
               g=opener.open(cobbSales.req)
               Flag=False
           except:
               sleep(5)
        html=g.read()
        soup=BeautifulSoup(html,"html.parser")    
    
        dataslets=soup.find_all("td",class_="DataletData")
        dataslets=dataslets[:-1]
        if not len(dataslets)%7==0:
            raise Exception("Something is bad in dataslets land")
        tempPriceList=[]
        tempDateList=[]
        for a in range(len(dataslets)/7):
            tempPriceList.append(dataslets[(1+a*7)].get_text())
            tempDateList.append(dataslets[(0+a*7)].get_text())
        try:
            lastPrice=tempPriceList[0]
            lastDate=tempDateList[0]
        except:
            lastPrice="No Last Price"
            lastDate="No Last Date"
    ###############################################################################
    #
    #
    #   Begin google scraping
    #
    ###############################################################################
    
        if address=="No Address Available":
            continue
        
        url="https://www.google.com/search?source=hp&q="+str(address.replace(" ","+"))+str("+zillow+georgia")+"&oq="+str(address.replace(" ","+"))+str("+zillow+georgia")+"&btnI=1"
#        url="https://www.google.com/search?source=hp&ei=rkA8Wpm2GpK6jwPinrCoCQ&q=4859+post+oak+tritt+rd&oq=4&gs_l=psy-ab.7..35i39k1l2j0i131k1j0i67k1j0i131k1j0j0i131k1j0l2j0i131k1.3834.3834.0.8032.2.1.0.0.0.0.130.130.0j1.1.0....0...1c..64.psy-ab..1.1.129.0...0.Z-yYeJtB2DM&btnI=1"

        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Connection': 'keep-alive',
            'Referer': 'www.google.com',
#            'Content-Type': 'application/x-www-form-urlencoded'

        }
        

        googName=pageRequest(url=url,headers=headers,get=True)
        try:
            googOpen=opener.open(googName.req)
#            if googOpen.info().get('Content-Encoding')=="gzip":
#                    buf = StringIO(googOpen.read())
#                    f = gzip.GzipFile(fileobj=buf)
#                    html = f.read()
#            else:
#                html=googOpen.read()
#            printToFile(html)
            zillowRedir=googName.req.redirect_dict.keys()[0]
        except:
            zillowRedir=googName.req.redirect_dict.keys()[0]      
        headers['Host']='www.zillow.com'
        try:
            zID=int(zillowRedir.split("/")[-2].split("_")[0])
            zipCode=int(zillowRedir.split("/")[-3].split("-")[-1])

        except:
            print "URL Used: "+str(url)
            print "Redirect: "+str(zillowRedir)
            print "Zillow ID could not be generated"
            zID="0"
        


        CobbProperties[pid]=resProp(pid,str(address),str(zipCode),str(owner),str(propClass),str(lastPrice),str(lastDate),str(zID))
        print "Property ID: "+str(pid)
        print "Zillow ID: "+str(zID)
        print "Current Owner: "+str(owner)
        print "Address: "+str(address)
        print "Last price: "+str(lastPrice)
        print "Last sale: "+str(lastDate)
        
  
        sleep(2)
        if len(CobbProperties.keys())%100==0:   
            with open('cobbProps.dat','wb') as h:
                pickle.dump(CobbProperties,h)
            h.close()
        print len(CobbProperties.keys())
###############################################################################
#
#
#   Print out current page "f"
#
###############################################################################
    
    with open('cobbProps.dat','wb') as h:
	 pickle.dump(CobbProperties,h)
    h.close()
#    try:
#        fout=open('tmp.html','w')
#    except:
#        print "Can't open html file, DOBULE YOU TEE EFF"
#    
#    fout.write(html)
#    fout.close()
