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
import time
import numpy as np
import os
from shutil import copy2
print "...complete."


#%% - Initialise key variables

print "INFORMATION: Setting up global variables...",
G_DEBUG       = 0    # 0 - no debug info; 1 - full debug info
DAILY_ITEMS   = 24*60*60*10 # Number of 100 ms items in one day
rootFolder    = r'E:\Vardafjellet\Nor14529247'
writeFolder   = r'E:\Vardafjellet\Daily'
print "...complete."


#%% - Read main input text file

##############################################################################################################################
############## MAIN CODE STARTS HERE #########################################################################################
##############################################################################################################################

if G_DEBUG:
    t0 = dt.datetime.now()
print "INFORMATION: Importing A-weighted data from NAS drive...  \n\n"
firstTime = True
file_details = []

#Create header line for output data
print 'File Name|Blocks'  #Create header line for output data

# Cycle through necessary folders and add data into Pandas dataframe
for folder_name, subfolder_list, file_list in os.walk(rootFolder):
    if G_DEBUG:
        print folder_name, subfolder_list, file_list
    if 'Recording' in folder_name:
        for file in file_list:
            if file.endswith('.WAV') | file.endswith('.wav'):
                file_name = os.path.join(folder_name,file)
                date_m = os.path.getmtime(file_name)
                year, month, day, hour, minute, second = time.localtime(date_m)[:-3]
                new_folder_name = 'Recording_{0:02n}{1:02n}{2:02n}'.format(day,month,year)
                new_file_name = 'VF_{0:02n}{1:02n}{2:02n}_{3:02n}{4:02n}00.wav'.format(day,month,year,hour,minute)
                date_index = dt.datetime.fromtimestamp(date_m)
                if G_DEBUG:
                    print '{0}, {1}, {2}'.format(new_folder_name, new_file_name, date_index)
                file_stuff = [file_name, new_folder_name, new_file_name, date_index]
                file_details.append(file_stuff)

file_details = pd.DataFrame(data = file_details, columns = ['Original','Folder','File','Date_Index'])
file_details.sort_values(by='Date_Index', inplace = True)
file_details.drop(labels=['Date_Index'], axis=1, inplace=True)
if G_DEBUG:
    print file_details.head()
    print file_details.tail()

for index, row in file_details.iterrows():
    # print row['Original'], row['Folder'], row['File']
    print row['Original'], os.path.join(writeFolder, row['Folder'], row['File'])

    # Form folder name string from date and project ID
    if not(os.path.exists(os.path.join(writeFolder, row['Folder']))):
        try:
            os.makedirs(os.path.join(writeFolder, row['Folder']))
        except OSError:
            print('WARNING: Failed to create output CSV folder')
    copy2(row['Original'], os.path.join(writeFolder, row['Folder'], row['File']))