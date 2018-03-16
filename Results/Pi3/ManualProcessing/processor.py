#!/usr/bin/python


import os,csv
FILENAME="30008.dat"
NEWFILE="30008.proc.dat"

f=open(NEWFILE,"wb")

with open(FILENAME,"rb") as csvFile:
    houseReader = csv.reader(csvFile, delimiter=',')
    for row in houseReader:
        if ("LLC" in row[1] or "PROPERTIES" in row[1] or "RESIDENTIAL" in row[1] or "INC" in row[1]):
            continue
        else:
            try:
                if float(row[4]) > 100.:
                    row[1]=row[1].title()
                    row[2]=row[2].title()
                    f.write(','.join(row)+"\n")
            except:
                pass
f.close()
        
