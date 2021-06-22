# -*- coding: utf-8 -*-
"""
Program created to read all 100 msec data from 30 min files from RES SLM at Woolley Hill and
to combine it and then to spit out daily files suitable for analysis by the IOA AMWG software.

Note: It is not possible to read in all the 100 msec data in one go and then create daily files
as output - the program fails with a Memory error. Whilst this could be resolved by reading and then
writing the data in batches, which is the sensible, long-term solution, the short-term bodge is
to copy groups of files to separate folders and then to process them in batches of no more
than 500 - 1000.

Created on Thu Jan 07 14:10:06 2016

@author: bass
"""

#%% - Import all necessary modules

from __future__ import division
print "INFORMATION: Importing modules...          ",
import pandas as pd
import datetime as dt
import numpy as np
import os
print "...complete."


#%% Function to calculate energy

def powerUp(x):
    try:
        y = 10**(x/10)
    except:
        y = 0
    return y


#%% - Initialise key variables

print "INFORMATION: Setting up global variables...",
G_DEBUG       = 1    # 0 - no debug info; 1 - full debug info
#G_RANGE       = 0    # 0 for 'Partial Over All' (default); 1 for 50 - 200 Hz; 2 for 100 - 400 Hz & 3 for 200 - 800 Hz
G_RANGE       = 1    # 0 for 'Partial Over All' (default); 1 for 50 - 200 Hz; 2 for 100 - 400 Hz & 3 for 200 - 800 Hz
#G_RANGE       = 2    # 0 for 'Partial Over All' (default); 1 for 50 - 200 Hz; 2 for 100 - 400 Hz & 3 for 200 - 800 Hz
#G_RANGE       = 3    # 0 for 'Partial Over All' (default); 1 for 50 - 200 Hz; 2 for 100 - 400 Hz & 3 for 200 - 800 Hz
DAILY_ITEMS   = 24*60*60*10 # Number of 100 ms items in one day
#rootFolder    = "V:\\Noise\\Den Brook\\Background Noise Data Sep to Oct 2015"
#rootFolder    = r"V:\Noise\Altaveedan\1028 Wind Farm Compliance Measurements Cloughmills"
#rootFolder    = r'V:\Noise\Garreg Lwyd\Hoare Lea Compliance at Lower House Farm - Summer 2017\Noise data'
#rootFolder    = r'V:\Noise'
#rootFolder    = r'V:\Noise\Garreg Lwyd\RES Statutory Nuisance at Lower House Farm - Winter 2017'
#rootFolder    = r'V:\Noise\Garreg Lwyd\Hoare Lea Compliance at Lower House Farm - Summer 2017\Noise data'
rootFolder    = r'V:\Noise\Garreg Lwyd\RES Statutory Nuisance at Lower House Holt - Autumn 2018'
#rootFolder    = r'C:\Users\bass\Downloads\GarregLwyd'
#writeFolder   = r"C:\Users\bass\Downloads\DenBrook\BackgroundNoise-Sep2015\Itton Manor\Data"
#writeFolder   = r"C:\Users\bass\Downloads\DenBrook\BackgroundNoise-Sep2015\Sandford Barton\Data"
#writeFolder   = r"C:\Users\bass\Downloads\Altaveedan\AM-Compliance\DailyCSV"
#writeFolder   = r"C:\Users\bass\Downloads\Altaveedan\AM-Compliance\DailyCSV\Dump"
#writeFolder   = r'C:\Users\bass\Downloads\GarregLwyd\Redundant'
writeFolder   = r'C:\Users\bass\Downloads\GarregLwyd\LHH-CSV'
#writeFolder   = r'C:\Users\bass\Downloads\GarregLwyd\HL-CSV'
#parentFolders = ['H3-03']
#childFolders  = ['0301','0302']
#childFolders  = ['0302','0303']
#parentFolders = ['H7-01']
#parentFolders = ['Garreg Lwyd\RES Redundant Meter - Spring 2018']
parentFolders = ['RES-Download-15','RES-Download-16']
#parentFolders = ['20170622 - First Equipment Service','20170706 - Second Equipment Service','20170721 - Collection']
#childFolders  = ['0101','0102']
#childFolders  = ['0102','0103']
childFolders1 = ['0815']
childFolders2 = ['0816']
#childFolders3 = ['0805']
#childFolders4 = ['0806']
#childFolders5 = ['0807']
#childFolders6 = ['0808']
#childFolders  = ['0101']
#parentFolders = ['H19-02']
#childFolders  = ['0201','0202']
#childFolders  = ['0202','0203']
print "...complete."


#%% - Read main input text file

##############################################################################################################################
############## MAIN CODE STARTS HERE #########################################################################################
##############################################################################################################################

if G_DEBUG:
    t0 = dt.datetime.now()
print "INFORMATION: Importing A-weighted data from NAS drive...  \n\n"
firstTime = True

#Create header line for output data
print "P-Folder","\t\tCFld","\tTotal","\tLocal","\tItems","\tFile Name"

# Cycle through necessary folders and add data into Pandas dataframe
fileCounterTotal = 0
for pF in parentFolders:
    if pF == parentFolders[0]:
        childFolders = childFolders1
    elif pF == parentFolders[1]:
        childFolders = childFolders2
#    elif pF == parentFolders[2]:
#        childFolders = childFolders3
#    elif pF == parentFolders[3]:
#        childFolders = childFolders4
#    elif pF == parentFolders[4]:
#        childFolders = childFolders5
#    elif pF == parentFolders[5]:
#        childFolders = childFolders6
    for cF in childFolders:
        dirName = rootFolder + '\\' + pF + '\\Auto_' + cF + '\\AUTO_LP'
        fileCounterLocal = 0
        orderedDirName   = np.sort(os.listdir(dirName))
        #orderedDirName   = orderedDirName[0:10] # Limit no of items processed at once
        fileTotal        = len(orderedDirName)
        for file in orderedDirName:
            if file.endswith(".rnd"):
                fileCounterLocal += 1
                fileCounterTotal += 1
                print pF, "\t\t\t", cF, "\t", fileCounterTotal, "\t", fileCounterLocal, "\t", fileTotal,"\t",file
    
                if file[7:10]  == 'SLM': #Leq data only                  
                    #fileData = pd.read_csv(os.path.join(dirName,file))
                    fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False, usecols = ['Start Time', 'Leq'])                 
                    fileData = fileData.rename(columns={'Start Time' : 'Timestamp'})
                    fileData = fileData.rename(columns={'Leq'        : 'LAeq'})

                elif file[7:10]  == 'OCT': # full octave band data
                    
                    if G_RANGE == 1: # 50 - 200 Hz from octave bands
                        # A - Form LBFeq from  50 -200 Hz 1/3 OBs by addition
                        #fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False,
                        #                       usecols = ['Start Time',  '50 Hz',  '63 Hz',  '80 Hz', '100 Hz', '125 Hz', '160 Hz', '200 Hz'],
                        #                       skiprows = 1)
                        # Use this line for HLA data
                        #fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False, usecols = [1,13, 14,15,16,17,18,19], skiprows = 1)
                        # Use this line for RES data
                        fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False,
                                               usecols = [1,14,15,16,17,18,19,20],
                                               skiprows = 1, na_values = '_._')

                    elif G_RANGE == 2: # 100 - 400 Hz from octave bands
                        # B - Form LBFeq from 100 -400 Hz 1/3 OBs by addition - should be same as Partial Over All
                        #fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False,
                        #                       usecols = ['Start Time', '100 Hz', '125 Hz', '160 Hz', '200 Hz', '250 Hz', '315 Hz', '400 Hz'],
                        #                       skiprows = 1)
                        fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False,
                                               usecols = [1,17,18,19,20,21,22,23],
                                               skiprows = 1, na_values = '_._')

                    elif G_RANGE == 3: # 200 - 800 Hz from octave bands
                        # C - Form LBFeq from 200 -800 Hz 1/3 OBs by addition
                        #fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False,
                        #                       usecols = ['Start Time', '200 Hz', '250 Hz', '315 Hz', '400 Hz', '500 Hz', '630 Hz', '800 Hz'],
                        #                       skiprows = 1)
                        fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False,
                                               usecols = [1,20,21,22,23,24,25,26],
                                               skiprows = 1, na_values = '_._')

                    else: # or G_RANGE == 0 (default)
                        # Standard approach - import 'Partial Over All' which is A-weighted 100 - 400 Hz sum
                        #fileData = pd.read_csv(os.path.join(dirName, file), sep = ',', low_memory = False, usecols = ['Start Time', 'Partial Over All'], skiprows = 1)
                        fileData = pd.read_csv(os.path.join(dirName, file),
                                               sep = ',', low_memory = False, usecols = ['Start Time', 'Partial Over All'],
                                               skiprows = 1, na_values = '_._')

                    # Replace'_._' with zeroes
                    for col in fileData.columns:
                        if col.endswith("Hz"):
                            if '  -.-' in fileData[col].values:
                                fileData.loc[:, col] = fileData[col].replace('  -.-', '0').astype(float)
                    #print fileData.columns


                    if G_RANGE in {1, 2, 3}: # Calculate from octave band levels
                        # Now form energetic / logarithmic sum of octave bands, which are already A-weighted for Rion
                        #fileData['Sum'] = fileData['50 Hz'].apply(powerUp) + fileData['63 Hz'].apply(powerUp) + fileData['80 Hz'].apply(powerUp) + fileData['100 Hz'].apply(powerUp) + fileData['125 Hz'].apply(powerUp) + fileData['160 Hz'].apply(powerUp) + fileData['200 Hz'].apply(powerUp)                  
                        fileData['Sum'] = 0
                        for col in fileData.columns[1:8]:
                            fileData['Sum'] += fileData[col].apply(powerUp)
                        fileData['Sum'] = 10.0*fileData['Sum'].apply(np.log10)
                        fileData        = fileData.rename(columns={'Start Time'       : 'Timestamp'})
                        fileData        = fileData.rename(columns={'Sum'              : 'LAeq'})
                        # Only retain columns which are needed
                        fileData = fileData[['Timestamp', 'LAeq']]
                    else:
                        # Now rename columns to something standard
                        fileData        = fileData.rename(columns={'Start Time'       : 'Timestamp'})
                        fileData        = fileData.rename(columns={'Partial Over All' : 'LAeq'})
                    
                else:
                    print 'Unexpected data format!'

                # Combine input files into single 'master file'            
                if firstTime:
                    allData  = fileData; firstTime = False
                else:
                    allData  = pd.concat([allData, fileData])
                    del fileData

# Make 'Start Time' the dataframe's index
allData['Timestamp'] = pd.to_datetime(allData['Timestamp'])
#allData['StartTime'] = pd.to_datetime(allData['StartTime'],format = '%Y/%m/%d %H:%M:%S')
allData.index         = allData['Timestamp']

# Make sure data is arranged in data order, just in case it isn't
#allData.drop(['Timestamp'],inplace=True,axis=1)
allData.sort_values(by='Timestamp', inplace = True)

# Now pad the data out so that it provides a continuous record from start to finish
# Missing timestamps created and filled with NaNs
# Note that line deletes the 'Timestamp' column because it is not of type float
allData = allData.resample('100L').mean()

if G_DEBUG:
    t1 = dt.datetime.now()
    time_required = (t1-t0).total_seconds()*1.0/60.
    print "\n...complete!  Time required: {0:.4} minutes".format(time_required)
else:
    print "\n...complete!"

# Now divide the data up into daily chunks and export into sepearate CSV files for analysis
#dates    = allData['Timestamp']
dates    = allData.index
startDay = dt.datetime(allData.index.min().year,allData.index.min().month,allData.index.min().day)
stopDay  = dt.datetime(allData.index.max().year,allData.index.max().month,allData.index.max().day)
day      = dt.timedelta(days=1)
date1    = startDay

#Create header line for output file data
print "\nFilename","\t\tDate","\tItems","\t% Complete","\tStart Date","\t\tStop Date"
while date1 <= stopDay:
    dailyData = allData[(dates >= date1) & (dates < (date1 + day))]
    if G_RANGE   == 1: #  50 - 200 Hz from octave bands
       fName =  'LHH-' + date1.strftime('%Y-%m-%d') + '-A.csv'
#       fName =  'data-' + date1.strftime('%Y-%m-%d') + '-A.csv'
    elif G_RANGE == 2: # 100 - 400 Hz from octave bands
       fName =  'LHH-' + date1.strftime('%Y-%m-%d') + '-B.csv'
#       fName =  'data-' + date1.strftime('%Y-%m-%d') + '-B.csv'
    elif G_RANGE == 3: # 200 - 800 Hz from octave bands
       fName =  'LHH-' + date1.strftime('%Y-%m-%d') + '-C.csv'
#       fName =  'data-' + date1.strftime('%Y-%m-%d') + '-C.csv'
    else:            # 100 - 400 Hz from Parial Over All
       fName =  'LHH-' + date1.strftime('%Y-%m-%d') + '.csv'
#       fName =  'data-' + date1.strftime('%Y-%m-%d') + '.csv'
    print fName,
    print "\t" + date1.strftime('%Y-%m-%d'),
    print "\t%s" % str(len(dailyData)),
    print "\t%5.1f" % (float(100*len(dailyData))/float(DAILY_ITEMS)),
    print "\t", date1,
    print "\t", date1 + day
    #dailyData.to_csv(os.path.join(writeFolder,parentFolders[0],fName), index=True, date_format = '%H:%M:%S.%f',index_label = 'Timestamp', header=True)
    dailyData.to_csv(os.path.join(writeFolder,fName), index=True, date_format = '%H:%M:%S.%f',index_label = 'Timestamp', header=True)
    date1 = date1 + day
