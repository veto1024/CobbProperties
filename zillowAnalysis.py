#!/usr/bin/python
##############################################################################
#
#    Cobb County property data analysis tool
#
#    12/27/2017 - v1.0
#

#    Main Script
#
#    1/10/2018 - v1.1
#    
#    Re-did output to output to ######.dat csv files in the main folder
#    
#   
#    
#
#    
#############################################################################
from browser import pageRequestMech
import pickle,cPickle
from residential import resProp,mortgageEst
import time,itertools,random
import logging, os, json

SLEEP=20
API=["X1-ZWz1g6x7pxeu4r_4wzn5",
     "X1-ZWz1g6xbnzmy2z_4zss3",
     "X1-ZWz18tl5afzzez_517ck",
     "X1-ZWz1g6xfm1v217_52lx1",
     "X1-ZWz18tl1cdrvgr_540hi"]

MAILERFILE="mailers4.csv"
PIDFILE="cobbList4.dat"
VIDSFILE="viewedIDs4.dat"
PROXYLOC="/home/pi/PiStorage/proxies.dat"
#PROXYLOC="proxies.dat"

def getProxy():
    
    # Gets random proxy plus UA
    uaList=[]
    proxyList=[]
    with open(PROXYLOC,"r+") as f:
        for count,line in enumerate(f,start=1):
            if count%2==0:
                line=line.replace("\n","")
                line=line.replace("\r","")
                uaList.append(line)
            else:
                ip=line.split(":")[0]
                port=line.split(":")[1]
                port=port.replace("\n","")
                port=port.replace("\r","")
                proxyList.append(ip+":"+port)
    return random.choice(proxyList),random.choice(uaList)
                
def unpickle_iter(file):
    try:
        while True:
            yield cPickle.load(file)
    except:
        raise StopIteration


if __name__=="__main__":
    
    # Establish logging
    
    logging.basicConfig(filename="log.txt",level=logging.WARNING,format='%(asctime)s %(message)s')
    
    prop={}
#    properties['1']=resProp('1',"2013 RIDGESTONE LANDING","JONATHAN ROVETO","RESIDENTIAL","$150,000","10-OCT-13","60837400")
    
    print '''Thank you for running my script to analyze Zillow data
             from America's favorite Zillow site of Zillowness. 
             Please provide the file name that you'd like to eat data from: 
                                                                             '''
 #   fileName=str(raw_input())
    fileName="cobbProps.dat"
#    with open(fileName) as file:
#        for item in unpickle_iter(file):
#            print item.viewkeys()
#            temp=raw_input()
    try:
        with open(fileName,"r+") as f:
            prop=pickle.load(f)
    except:
        raise Exception("File not found")
        
    try:
        print PIDFILE
        with open(PIDFILE,"rb") as h:
            piZIDs=pickle.load(h)
    except:
        raise Exception("No piZID file found")
    
    viewedIDs=[]
    try:
        with open("viewedIDs.dat","a") as g:
            viewedIDs=pickle.load(g)
            g.close()
            VIDfile=open(VIDSFILE,"a")
    except:
        VIDfile=open("viewedIDs.dat","w+")
        print "viewedIDs failed to load. Generating new file."
    
    
###############################################################################
#
#
#    Prepare CSV file
#   
#
###############################################################################

#    csvFile=open(MAILERFILE,"w+")
#    firstLine="ZID,Name,Address,Zip,Months"
#    csvFile.write(firstLine)
#    csvFile.flush()
    
 ###############################################################################
#
#
#    Begin analysis
#   
#
###############################################################################   
 
    proxyUA=getProxy()
    print "New Proxy: "+proxyUA[0]
    count=0  
    for apiKey in itertools.cycle(API):   
        print "New API: "+apiKey
        if len(piZIDs)==0:
            break
        item=piZIDs.pop()
        # Skip IDs that have been checked
        if item in viewedIDs:
            continue  
        # Switch proxies every 100 calls
        if len(piZIDs)%100==0:
            proxyUA=getProxy()
            print "New Proxy: "+proxyUA[0]
            
        try:
            # Zillow Estimates using Mechanize option
            prop[item].zillowEst(Requester=pageRequestMech,api=apiKey,proxy={'http':proxyUA[0]},UA=proxyUA[1],Mechanize=True)
            try: 
                prop[item].zipCode
#                count+=1
                months=mortgageEst(prop[item].lastPrice,prop[item].lastDate)[0]
                try:
                    with open(str(prop[item].zipCode)+".dat","r") as zipFile:
                        pass
                except:
                    with open(str(prop[item].zipCode)+".dat","w") as zipFile:
                        print "Instantiating "+str(prop[item].zipCode)+".dat"
                        firstLine="ZID,Name,Address,Zip,Months,Est.Mortgage\n"
                        zipFile.write(firstLine)
                        zipFile.flush()   
                with open(str(prop[item].zipCode)+".dat","a") as matchFile:
                    if months >=0:
                        print "ZID: "+prop[item].zID
                        print "Property: "+str(prop[item].address)
                        print "Zip Code: "+str(prop[item].zipCode)
                        print "# Months: "+str(months)
                        morgEst=mortgageEst(prop[item].lastPrice,prop[item].lastDate)[1]
                        print "Mort. Est: "+str(morgEst)
                        outline=str(prop[item].zID)+","+str(prop[item].owner)+","+str(prop[item].address)+","+str(prop[item].zipCode)+","+str(months)+","+str(morgEst)+str("\n")
                        try:
                            matchFile.write(outline)
                        except:
                            logging.exception("Matchfile write failed with line %s",outline)
                    else:
                        print "ZID "+str(prop[item].zID)+" No Good: # months since purchase is "+str(months) 
                        viewedIDs.append(item)
                time.sleep(SLEEP)
            except:
                logging.warning("ZID %s does not have a zip code",item)
                viewedIDs.append(item)
                time.sleep(SLEEP)
                pass
        except:
            viewedIDs.append(item)
            logging.exception('ZID %s did not HTTP open',item)
            proxyUA=getProxy()
            print "New Proxy: "+proxyUA[0]
            time.sleep(SLEEP)
            pass
        if len(viewedIDs)%10==0:
            pickle.dump(viewedIDs,VIDfile)
            VIDfile.flush()
#        if count==500:
#            break
#    csvFile.close()
    VIDfile.close()
