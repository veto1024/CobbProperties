#!/usr/bin/python
##############################################################################
#
#    Cobb County property data analysis tool
#
#    12/27/2017 - v1.0
#

#    Main Script
#
#    
#    
#    
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
import logging

SLEEP=20
API=["X1-ZWz18tn89ma2h7_3jtqm",
     "X1-ZWz1g6vcmvkyyz_3l8b3",
     "X1-ZWz18tn4bk1yiz_3mmvk",
     "X1-ZWz18tn0dhtukr_3pg0i",
     "X1-ZWz1g6vkj016vf_3qukz"]

MAILERFILE="mailers1.csv"
PIDFILE="cobbList1.dat"
VIDSFILE="viewedIDs1.dat"
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
        with open("viewedIDs.dat","r+") as g:
            viewedIDs=pickle.load(g)
            g.close()
            VIDfile=open(VIDSFILE,"w+")
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

    csvFile=open(MAILERFILE,"w+")
    firstLine="ZID,Name,Address,Zip,Months"
    csvFile.write(firstLine)
    csvFile.flush()
    
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
                if prop[item].zipCode==30008:
                    count+=1
                    months=mortgageEst(prop[item].lastPrice,prop[item].lastDate)[0]
                    if months >=60:
                        print "ZID: "+prop[item].zID
                        print "Property: "+str(prop[item].address)
                        print "Zip Code: "+str(prop[item].zipCode)
                        print "# Months: "+str(months)
                        print "Mort. Est: "+str(mortgageEst(prop[item].lastPrice,prop[item].lastDate)[1])
                        outline=str(prop[item].zID)+","+str(prop[item].owner)+","+str(prop[item].address)+","+str(prop[item].zipCode)+","+str(months)+"\n"
                        csvFile.write(outline)
                        csvFile.flush()
                    else:
                        print "ZID "+str(prop[item].zID)+" No Good: # months since purchase is "+str(months) 
                        viewedIDs.append(item)
                    time.sleep(SLEEP)
                else:
                    print "ZID "+str(prop[item].zID)+" No Good: Zip Code is "+str(prop[item].zipCode)
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
        if count==500:
            break
    csvFile.close()
    VIDfile.close()
