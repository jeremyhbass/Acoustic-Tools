# -*- coding: utf-8 -*-
"""
Program created to read all 10 min AM data from files created by IOA AMWG software at Woolley Hill and
to combine it and then to spit out daily files suitable for analysis by the IOA AMWG software.

There is a probelm in this code, in that the Rion assumes the data for a day runs: 0:00:00.1 to 24:00:00.0,
whereas the pandas code below, when selecting all the data for a day assumes:      0:00:00.0 to 23:59:59.9
The outcome is that the first day of data, which typically starts at point during the day, is always short
by one 0.1 Hz item of the final 10 min block, because it runs:                     X:XX:XX.1 to 23:59:59.9


Created on Thu Jan 07 14:10:06 2016

@author: bass
"""


#%% - Import all necessary modules

print "INFORMATION-0: Importing modules...          ",
import pandas as pd
import datetime as dt
import numpy as np
import os
print "...complete."


#%% - Initialise key variables

print "INFORMATION-0: Setting up global variables...",
G_DEBUG       = 1    #0 - no debug info; 1 - full debug info
rootFolder    = r'E:\Vardafjellet\Processed'
writeFolder   = rootFolder
allData       = None
print "...complete."


#%% - Read main input text file

##############################################################################################################################
############## MAIN CODE STARTS HERE #########################################################################################
##############################################################################################################################

#print dt.datetime.now()
#if G_DEBUG:
#    t0 = dt.datetime.now()
print "INFORMATION-1: Importing A-weighted 10 min data from NAS drive...  \n\n"
firstTime = True

#Create header line for output data
print "File Name","\t\t\tItems"

# Cycle through necessary folders and add data into Pandas dataframe
fileCounter = 0

# File name example is: data-2016-02-06_10min.txt
# So mask is:           data-201X-XX-XX_10min.txt
orderedDirName = np.sort(os.listdir(rootFolder))
for file in orderedDirName:
    if file.endswith("-10min.csv") and len(file) == 23:
        fileCounter += 1
        print file, "\t", fileCounter
        fileData = pd.read_csv(os.path.join(rootFolder,file), sep=',')
        
        # TIDY UP DATAFRAME BEFORE COMBINING
        # Delete last line if contains timing info, not data        
        fileLength = len(fileData)
        # Add a time stamp so that data time stamped
        #if file[5:15] == '2016-06-13':
        #if file[5:15] == '2017-06-13':
        if file[4:14] == '2018-10-23':
            startTime = dt.datetime.strptime(file[3:13],"%Y-%m-%d") # Need to start at 12:00 on first day
            #startTime = dt.datetime(startTime.year,startTime.month,startTime.day,15,50)
            #startTime = dt.datetime(startTime.year,startTime.month,startTime.day,11,10)
            startTime = dt.datetime(startTime.year,startTime.month,startTime.day,11,0)
        #elif file[5:15] == '2016-10-17':
        #    startTime = dt.datetime.strptime(file[5:15],"%Y-%m-%d") # Need to start at 11:00 on first day
        #    startTime = dt.datetime(startTime.year,startTime.month,startTime.day,11,0)  
        else:
            startTime = dt.datetime.strptime(file[3:13],"%Y-%m-%d")
        timeStamp             = pd.date_range(start = startTime, periods=fileLength, freq='600s')
        fileData['startTime'] = timeStamp
        fileData.index        = fileData['startTime']
        #fileData              = fileData[['startTime', 'Count', 'Average', '10th %', '50th %', '90th %']]            
        fileData              = fileData[['LAeq [dB]']]            

        if firstTime:
            allData  = fileData; firstTime = False
        else:
            allData  = pd.concat([allData, fileData], sort=False)
        del fileData

if allData is not None:

# Make sure data is arranged in data order, just in case it isn't
    # need inplace=True to actually make this sorting happen!
    print "\nINFORMATION-2: Sorting data",
    #del allData['startTime']
    allData.sort_values(by='startTime', inplace = True)
    print "...complete\tLines: {}".format(len(allData))

    # Now pad the data out so that it provides a continuous record from start to finish
    # Note that line deletes the 'Timestamp' column for some reason??
    print "\nINFORMATION-3: Padding data",
    allData = allData.resample('10T').mean()
    print "Total number of lines of 10 min data -   padded: %d" % len(allData)
    print "...complete\tLines: {}".format(len(allData))

    #if G_DEBUG:
    #    t1 = dt.datetime.now()
    #    time_required = (t1-t0).total_seconds()*1.0/60.
    #    print "...complete!  Time required: {0:.4} minutes".format(time_required)
    #else:
    #    print "...complete!"

    #Create header line for output file data
    print "\nINFORMATION-4: Writing data",
    fName =  'VF_AM_LAeq_52.csv'
    print "\nFilename   : %s" % fName
    print   "Total Items: %d" % len(allData)
    #allData.to_csv(os.path.join(writeFolder,fName), index=False, date_format = '%d/%m/%Y %H:%M:%S')
    allData.to_csv(os.path.join(writeFolder,fName), index=True, date_format = r'%d/%m/%Y %H:%M:%S')
    print "...complete\tLines: {}".format(len(allData))
else:
    print "Warning - No data meets the necessary criteria - allData empty!"