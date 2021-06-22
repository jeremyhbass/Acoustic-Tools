# -*- coding: utf-8 -*-
"""
Program created to read all 10 min data from files from RES SLM at Woolley Hill and
to combine it and then to spit out daily files suitable for analysis by the IOA AMWG software.

Created on Thu Jan 07 14:10:06 2016

@author: bass
"""

#%% - Import all necessary modules

print "INFORMATION: Importing modules...          ",
import pandas as pd
import datetime as dt
import numpy as np
import os
print "...complete."


#%% Function to read input file in chunks
def fileParser(row,dName,fName):
    global firstAddress
    global firstStart
    global firstMeas
    global firstData
    global addressData
    global startData
    global measData
    global fData
    global noEntry
    
    # Read Address line of data, i.e. "Address,   868"
    try:
        lineData = pd.read_csv(os.path.join(dName,fName), skiprows=row, nrows=1, header=None); row += 1
        if firstAddress:
            addressData  = lineData; firstAddress = False
        else:
            addressData  = pd.concat([addressData, lineData])
    except ValueError:
        #print 'TERMINATING: End of data...'
        return noEntry

    # Read start time line of data, i.e. "Start Time,2015/12/08 13:40:00"
    lineData = pd.read_csv(os.path.join(dName,fName), skiprows=row, nrows=1, header=None); row += 1
    if firstStart:
        startData  = lineData; firstStart = False
    else:
        startData  = pd.concat([startData, lineData])    

    # Read measurement interval line of data, i.e. "Measurement Time,00d 00:10:00.0"
    lineData = pd.read_csv(os.path.join(dName,fName), skiprows=row, nrows=1, header=None); row += 1
    if firstMeas:
        measData  = lineData; firstMeas = False
    else:
        measData  = pd.concat([measData, lineData])

    # Read 1/3 octave band lines of data, i.e.
    #,Sub,Main,Partial Over All,12.5 Hz,16 Hz,20 Hz,25 Hz,31.5 Hz,40 Hz,50 Hz,63 Hz,80 Hz,100 Hz,125 Hz,160 Hz,200 Hz,250 Hz,315 Hz,400 Hz,500 Hz,630 Hz,800 Hz,1 kHz,1.25 kHz,1.6 kHz,2 kHz,2.5 kHz,3.15 kHz,4 kHz,5 kHz,6.3 kHz,8 kHz,10 kHz,12.5 kHz,16 kHz,20 kHz,
    #Leq,  -.-, 47.1, 39.8,  8.0, 12.8, 16.5, 19.4, 21.8, 23.0, 24.9, 26.5, 25.9, 26.2, 26.1, 25.5, 25.7, 30.0, 33.6, 36.8, 39.1, 38.3, 39.6, 39.0, 35.6, 32.1, 29.5, 27.8, 26.5, 25.2, 23.6, 21.4, 17.8, 13.5,  8.7,  4.1,  0.9,       
    #lineData = pd.read_csv(os.path.join(dName,fName), skiprows=row, nrows=1); row += 13             # for LEQ only
    lineData = pd.read_csv(os.path.join(dName,fName), skiprows=row, nrows=9, na_values = '_._'); row += 13            # for LEQ,LE,Lmax,Lmin,LN1,LN2,LN3,LN4 & LN5

    # if you want Leq values need 1st line of 9 rows (0th in Python)
    #lineData = lineData[lineData['Unnamed: 0'] == 'Leq']
    # if you want L90/LN4 values need 8th line of 9 rows (7th in Python)
    lineData = lineData[lineData['Unnamed: 0'] == 'LN4']
    
    if firstData:
        fData     = lineData; firstData = False
    else:
        fData  = pd.concat([fData, lineData])    
    
    return row


#%% Function to reset dataframes
def reFormatter(df1, df2):
    if len(df1) == len(df2):
        df1.index     = df2[1]
    else:
        print "WARNING: file length mismatch!"
    return df1


#%% - Initialise key variables

print "INFORMATION: Setting up global variables...",
G_DEBUG       = 1    #0 - no debug info; 1 - full debug info
#rootFolder    = "V:\\Noise\\Woolley Hill"
#rootFolder    = "C:"
#rootFolder    = r'V:\Noise\Garreg Lwyd\Hoare Lea Compliance at Lower House Farm - Summer 2017\Noise data'
#rootFolder    = r'V:\Noise\Garreg Lwyd\RES Statutory Nuisance at Lower House Farm - Winter 2017'
rootFolder    = r'V:\Noise\Garreg Lwyd\RES Statutory Nuisance at Lower House Holt - Autumn 2018'
#rootFolder    = r'C:\Users\bass\Downloads\GarregLwyd'
#rootFolder    = r'C:\Users\bass\Downloads\GarregLwyd\RES-CSV'
#writeFolder   = "C:\\Users\\bass\\Downloads\\Woolley Hill\\OAMX"
#writeFolder   = r'C:\Users\bass\Downloads\GarregLwyd\RES-CSV'
writeFolder   = r'C:\Users\bass\Downloads\GarregLwyd\LHH-CSV'
#writeFolder   = r'C:\Users\bass\Downloads\GarregLwyd\Redundant'
#parentFolders = ['Garreg Lwyd\RES Redundant Meter - Spring 2018']
#parentFolders = ['RES-Download-1']
parentFolders = ['RES-Download-15','RES-Download-16']
#parentFolders = ['New folder 4', 'New folder 5']
#parentFolders = ['NX-42RT']
#parentFolders = ['H7-01']
#parentFolders = ['20170622 - First Equipment Service', '20170706 - Second Equipment Service', '20170721 - Collection']
#parentFolders = ['20170706 - Second Equipment Service']
#parentFolders = ['20170721 - Collection']
#childFolders1 = ['0101','0102','0103','0104']
#childFolders1 = ['0301','0302']
#childFolders2 = ['0105','0106']
#childFolders3 = ['0202','0203']
#childFolders = ['0801','0802', '0803']
#childFolders = ['0801']
childFolders1 = ['0815']
childFolders2 = ['0816']
#childFolders3 = ['0811']
#childFolders4 = ['0812']
#childFolders5 = ['0143']
#childFolders6 = ['0118']
noEntry       = -99
print "...complete."



#%% - Read main input text file

##############################################################################################################################
############## MAIN CODE STARTS HERE #########################################################################################
##############################################################################################################################

if G_DEBUG:
    t0 = dt.datetime.now()
print "INFORMATION: Importing A-weighted 10 min data from NAS drive...  \n\n"
firstTime = True

#Create header line for output data
print "P-Folder","\t\tCFld","\tTotal","\tLocal","\tItems","\tFile Name","\t\t\tLines"

# Cycle through necessary folders and add data into Pandas dataframe
fileCounterTotal = 0
for pF in parentFolders:
    if pF == parentFolders[0]:
        cFEnd = childFolders1
    elif pF == parentFolders[1]:
        cFEnd = childFolders2
#    elif pF == parentFolders[2]:
#        cFEnd = childFolders3
#    elif pF == parentFolders[3]:
#        cFEnd = childFolders4
#    elif pF == parentFolders[4]:
#        cFEnd = childFolders5
#    elif pF == parentFolders[5]:
#        cFEnd = childFolders6
    for cF in cFEnd:
#    for cF in childFolders:
        dirName = rootFolder + '\\' + pF + '\\Auto_' + cF + '\\AUTO_LEQ'

        fileCounterLocal = 0
        orderedDirName = np.sort(os.listdir(dirName))
        for file in orderedDirName:
            fileCounterLocal += 1
            fileCounterTotal += 1
            rowCount          = 1
            firstAddress      = True
            firstStart        = True
            firstMeas         = True
            firstData         = True
            
            print pF, "\t", cF, "\t", fileCounterTotal, "\t", fileCounterLocal, "\t", len(os.listdir(dirName)),"\t",file,

            lineCount = 0            
            looper = True
            while looper:            
                rowCount = fileParser(rowCount,dirName,file)
                if rowCount == noEntry:
                    looper = False
                    print "\t", lineCount
#                else:
#                    print xxx
                lineCount += 1

            addressData.index = addressData[1]
            startData         = reFormatter(  startData, addressData)
            measData          = reFormatter(   measData, addressData)
            fData             = reFormatter(      fData, addressData)

            startData = startData[[1]]; startData = startData.rename(columns={1 : 'StartTime'})
            measData  =  measData[[1]];  measData =  measData.rename(columns={1 : 'Interval'})
            fData     =     fData[['Main','Partial Over All',
                                   '50 Hz','63 Hz','80 Hz','100 Hz','125 Hz','160 Hz','200 Hz',
                                   '250 Hz','315 Hz','400 Hz','500 Hz','630 Hz','800 Hz']]
            fileData  = pd.concat([startData, measData, fData], axis=1)

            if firstTime:
                allData  = fileData; firstTime = False
            else:
                allData  = pd.concat([allData, fileData])

# Make sure data is arranged in data order, just in case it isn't
# Make 'Start Time' the dataframe's index
allData['StartTime'] = pd.to_datetime(allData['StartTime'],format = '%Y/%m/%d %H:%M:%S') #Start Time,2015/12/02 12:30:00
allData.index = allData['StartTime']
#del allData['StartTime']
# Make sure data is arranged in data order, just in case it isn't
allData.sort_values(by='StartTime', inplace = True)

# Remove lines for which the 'Interval' data don't equal '00d 00:10:00.0' - i.e less than 10 min and delete them
print "\nTotal number of lines of 10 min data -  initial: %d" % len(allData)
allData  = allData[(allData['Interval'] =='00d 00:10:00.0')]
print "Total number of lines of 10 min data - filtered: %d" % len(allData)

# Now pad the data out so that it provides a continuous record from start to finish
# Note that line deletes any columns which are not of type float64 - check if problems occur
for col in allData.columns[2:17]:
    allData[col] = pd.to_numeric(allData[col], errors = 'coerce')
allData = allData.resample('10T').mean()
print "Total number of lines of 10 min data -   padded: %d" % len(allData)

if G_DEBUG:
    t1 = dt.datetime.now()
    time_required = (t1-t0).total_seconds()*1.0/60.
    print "...complete!  Time required: {0:.4} minutes".format(time_required)
else:
    print "...complete!"

#Create header line for output file data
fName = '10min_data_LHH-L90-16.csv'
#fName = '10min_data_RES-L90-0402.csv'
print "\nFilename   : %s" % fName,
print "\tTotal Items: %d" % len(allData)
allData.to_csv(os.path.join(writeFolder,fName), index=True, date_format = '%d/%m/%Y %H:%M:%S',index_label = 'Timestamp')