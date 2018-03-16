#!/usr/bin/python
##############################################################################
#
#   Cobb County residential class
#
#   12/22/2017 - v1.1 
#
#    Added zip codes to resProp class
#
#   12/21/2007 - v 1.0
#
#   Class established as database elements for mining Cobb County Properties
#   website
#    
#   resProp():
#
#   pID         = Cobb County Property ID
#   zID         = Zillow ID
#   address     = Property address from Cobb website
#   owner       = Owner from Cobb website
#   propClass   = Class of property, typically residential
#   lastPrice   = Last sales price avaialble, if at all, from Cobb website
#   lastDate    = Last date of a transaction, corresponds to LastPrice
#
#   mortgageEst():
#   Input:
#
#   buyPrice    = Buy price input from cobb county
#   lastPrice   = Last sales price available, if at all, from Cobb website
#   months      = Dictionary of numerical correspondences to 3-letter months
#   
#   Output:
#
#   return  Estimated current mortgage based on 30-year, 5% interest rate
#           without refinancing
# ############################################################################

import requests
import urllib2
import urllib
from bs4 import BeautifulSoup
from StringIO import StringIO
import gzip
import xml.etree.ElementTree as ET
from browser import pageRequest
import cookielib
import pickle

ZAPI="X1-ZWz18udnaikikr_4pyss"


class resProp():
    def __init__(self,pID,address,zipCode,owner,propClass,cobbPrice,lastDate,zID):
        self.pID=pID
        self.zID=zID
        self.zipCode=zipCode
        self.address=address
        self.owner=owner
        self.propClass=propClass
        self.lastPrice=cobbPrice
        self.lastDate=lastDate
        self.manual=False
        self.zillowLat=0.
        self.zillowLong=0.
    def zillowEst(self,Requester,api=ZAPI,proxy=False,UA=False,Mechanize=False):
        
###############################################################################
#
#
#   Begin Zillow non-API scraping
#
###############################################################################     
            
#        zillowReq=pageRequest(url=zillowRedir,headers=headers,get=True)
#        zillowOpen=opener.open(zillowReq.req)
#        
#        if zillowOpen.info().get('Content-Encoding') == 'gzip':
#            buffer = StringIO( zillowOpen.read())
#            deflatedContent = gzip.GzipFile(fileobj=buffer)
#            html=deflatedContent.read()
#        else:
#            html=zillowOpen.read()
#         
#        html=html.replace("\\","")
#        soup=BeautifulSoup(html)
#        printToFile(html,fileName="zillow.html")
            
###############################################################################
#
#
#   Begin Zillow API scraping
#
###############################################################################    

        if self.zID=="0":
            print "UNKNOWN ZILLOW ID"
            self.zillowPrice="$0"
            return 0
        url="http://www.zillow.com/webservice/GetZestimate.htm?"
        url=url+"zws-id="+api+"&zpid="+str(self.zID)
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
#            'Content-Type': 'application/x-www-form-urlencoded'

        }

        if UA:
            headers['User-Agent']=UA
        if Mechanize:
            if proxy:
                zAPIreq=Requester(headers=headers,proxy=proxy)
            else:
                zAPIreq=Requester(headers=headers)
            zAPIopen=zAPIreq.req.open(url,timeout=30.)
            
        else:
            cookies=cookielib.LWPCookieJar()
            handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(cookies)
            ]
            opener=urllib2.build_opener(*handlers) 


            if proxy:
                zAPIreq=Requester(url=url,headers=headers,get=True,proxy=proxy)
            else:
                zAPIreq=Requester(url=url,headers=headers,get=True)
            zAPIopen=opener.open(zAPIreq.req,timeout=30.)
        
        
        
        if zAPIopen.info().get('Content-Encoding')=="gzip":
            buf = StringIO(zAPIopen.read())
            f = gzip.GzipFile(fileobj=buf)
            xmlData=f.read()
        else:
            xmlData=zAPIopen.read()
        
        tree=ET.ElementTree(ET.fromstring(xmlData))
        root=tree.getroot()
#        for child in root[2][3]:
#            print child.tag,child.attrib
        try:
            self.zillowPrice=float(root[2][3][0].text)
        except:
            print "ZID = "+self.zID
            print "URL = "+url
            print "Address = "+self.address
            self.manual=True
            raise Exception("Root tree in ET unable to be parsed correctly")
        
         try:
            self.zillowLat=float(root[2][1][5].text)
            self.zillowLong=float(root[2][1][6].text)
            print "lat/long = "+str(self.zillowLat)+"/"+str(self.zillowLong)
        except:
            print "ZID = "+self.zID
            print "URL = "+url
            print "Address = "+self.address
            print "Lat attemp = "+root[2][1].text
            self.manual=True
            raise Exception("Unable to grab Latitude and Longitude")       
        try:
            root[2][2][1].text
            self.zipCode=int(root[2][2][1].text)
        except:
            print "ZID = "+self.zID
            print "URL = "+url
            print "Address = "+self.address
            self.manual=True
            raise Exception("Root tree in ET unable to be parsed correctly")
        
        
        
def mortgageEst(buyPrice,lastDate):
    
    months={'JAN':'1',
            'FEB':'2',
            'MAR':'3',
            'APR':'4',
            'MAY':'5',
            'JUN':'6',
            'JUL':'7',
            'AUG':'8',
            'SEP':'9',
            'OCT':'10',
            'NOV':'11',
            'DEC':'12'
            }
    temp=lastDate.split("-")
    if len(temp)<=2:
        raise Exception("Month not formatted correctly from Cobb")
    temp[1]=months[temp[1]]
    temp=[float(a) for a in temp]
    if temp[2]>=50.:
        num=(17.+(100.-temp[2]))*12.+(12-temp[1])
    else:
        num=(17-temp[2])*12.+(12-temp[1])
    
    try:
        tempPrice=float(buyPrice.replace(",","")[1:])
    except:
        raise Exception("Purchase price not formatted correctly from Cobb")
    
    return num,tempPrice*.9*(1.0018-.0013*num-(1.E-6)*(num**2)-(8.E-9)*(num**3))
    
    
    
    
if __name__=="__main__":
    
    properties={}
#    properties['1']=resProp('1',"2013 RIDGESTONE LANDING","JONATHAN ROVETO","RESIDENTIAL","$150,000","10-OCT-13","60837400")
    
    print '''Thank you for running my script to get cool Zillow data
             from America's favorite Zillow site of Zillowness. Please
             provide the file name that you'd like to eat data from: 
          '''
    fileName=str(raw_input())
    
    try:
        with open(fileName,"r+") as f:
            properties=pickle.load(f)
    except:
        print "File not found. Attempting cobbProps.dat by default"
        fileName="cobbProps.dat"
        try:
            with open(fileName,"r+") as f:
                properties=pickle.load(f)
        except:
            raise Exception("Files not found")
    
    numvalid=0
    for a in properties.keys():
        if not ((properties[a].lastPrice=="$0") or (properties[a].lastPrice=="No Last Price")
                or (properties[a].lastPrice=="")):
            numvalid+=1
                
        
    print "Number of properties loaded: "+len(properties.keys())
    print "Number of valid properties: "+str(numvalid)
    print '''What property would you like to see a summary for?
    
            Type "L" for a list of IDs'''
    
    idRequest=str(raw_input())
#    idRequest='1'
    Flag=True
    while Flag==True:
        if (idRequest=="L" or idRequest=="l"):
            for a in properties.keys():
                print a
            print '''What property would you like to see a summary for?
    
                   Type "L" for a list of IDs'''
    
            idRequest=str(raw_input())
        try:
            properties[idRequest]
            Flag=False
        except:
            print '''Property ID "+str(idRequest)+" not found! Please try again
                     What property would you like to see a summary for?'''
                     
            idRequest=str(raw_input())
#            idRequest='1'
    properties[idRequest].zillowEst(Requester=pageRequest)
    
    print "Property location: "+str(properties[idRequest].address)
    print "Property owner: "+str(properties[idRequest].owner)
    print "Last sale date: "+str(properties[idRequest].lastDate)
    print "Cobb property value :"+str(properties[idRequest].lastPrice)
    print "Estimated current mortgage :"+str(mortgageEst(properties[idRequest].lastPrice,properties[idRequest].lastDate)[1])
    print "Zillow value: $"+str(properties[idRequest].zillowPrice)
    