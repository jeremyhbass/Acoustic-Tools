# -*- coding: utf-8 -*-
"""

Works to create a daily dashboartd of all SLM & SCADA data

Created on Thu Feb 08 16:20:29 2018
V1 - first version
V2 - to be added (next step):
    * Andy's code
    * complaints from complaint log visually indicated
    * rain, overload and external source of noise
    * mode turbines are in
    * possible use of 'gridspec' instead of 'subplot'.  This gives more control of screen layout
    * read in various configuration options from 'Status Summary' and use to annote dashboards, as appropriate - started

@author: bass & birchby
"""

from __future__ import division
import os
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib as mpl  # This calls historic defaults for matplotlib
mpl.style.use('classic')  # as above


#%% Function to determine AM penalty for given level of noise immission and AM

def AM_penalty(AM):

    if AM == np.nan:
        penalty = 0
    else:
        if AM < 2:
            penalty = 0
        elif AM >= 2 and AM <= 3:
            penalty = AM
        elif AM > 3 and AM < 10:
            penalty = 3 + ((AM-3)*2.0/7.0)
        elif AM >= 10:
            penalty = 5
        else:
            penalty = 0
    return penalty


#%% Function to draw a radar plot of data - (r,theta)

def polarShow(fig, subplot, df, polarTitle, sWS, eWS, data_type):
    r      = df[df.columns[0]]
    theta  = np.radians(df[df.columns[1]])
    if data_type == 0: # Wind rose
        area = 20
        colors = df[df.columns[0]]
    elif data_type == 1: # AM radar plot
        area   = df[df.columns[6]]**2
        colors = df[df.columns[6]]
    ax = fig.add_subplot(subplot, projection='polar', polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 16)
    
    if data_type == 0:   # Wind rose
        c = plt.scatter(theta, r, s = area, c=colors, cmap=plt.cm.YlOrRd, vmin=0, vmax=16)
        cbar2 = fig.colorbar(c, fraction=0.04, pad=0.15, ticks=[0, 4, 8, 12, 16])
        cbar2.ax.set_yticklabels(['0 m/s', '4 m/s', '8 m/s', '12 m/s', '16 m/s'])
        ax.set_title('Wind Rose')
    elif data_type == 1:   # AM radar plot
        c = plt.scatter(theta, r, s = area, c=colors, cmap=plt.cm.YlOrRd, vmin=2, vmax=6)
        cbar2 = fig.colorbar(c, fraction=0.04, pad=0.15, ticks=[2, 4, 6])
        cbar2.ax.set_yticklabels(['2 dB', '4 dB', '6 dB'])
        ax.set_title('Amplitude Modulation: 50 - 200 Hz')
  
#    drawSector(ax, np.radians(232), np.radians(307), sWS, eWS)       
    drawSector(ax, np.radians(200), np.radians(320), sWS, eWS)       
    return


#%% Function to annotate radar plots to show key information

def drawSector(ax, startRad, endRad, startWS, endWS):
    
    #create data set representing curved line
    theta = np.arange(startRad, endRad, 0.01)
    #multiply radius list by 0 to keep correct structure but all zero
    r = (theta * 0)
    ax.plot([startRad,startRad], [startWS,endWS], color='r', linewidth=2)
    ax.plot([endRad,endRad],     [startWS,endWS], color='r', linewidth=2)
    ax.plot(theta, r+startWS, color='r', linewidth=2)
    ax.plot(theta, r+endWS,   color='r', linewidth=2)
    
    ax.plot([np.radians(262),np.radians(262)], [0,20], color='k', linewidth=2) # T1
    #ax.plot([np.radians(265),np.radians(265)], [0,20], color='k', linewidth=2) # T2
    #ax.plot([np.radians(278),np.radians(278)], [0,20], color='k', linewidth=2) # T3
    ax.plot([np.radians(277),np.radians(277)], [0,20], color='k', linewidth=2) # T4
    #ax.plot([np.radians(303),np.radians(303)], [0,20], color='k', linewidth=2) # T13
    ax.plot([np.radians(316),np.radians(316)], [0,20], color='k', linewidth=2) # T18
    ax.text(np.radians(262), 20,  'T1', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    #ax.text(np.radians(265), 20,  'T2', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    #ax.text(np.radians(279), 20,  'T3', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(276), 20,  'T4', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    #ax.text(np.radians(303), 20, 'T13', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(316), 20, 'T18', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    #ax.fill([np.radians(262),np.radians(316)], [2,12], facecolor='b', alpha=0.25)
    
    return


#%% Routine to create daily dashboard of data

def dash_board(daily_data):

    # Set up day label
    day_label = "{:04n}-{:02n}-{:02n}".format(daily_data.index[0].year,
                                              daily_data.index[0].month,
                                              daily_data.index[0].day)

    #Work out if on or off from power:
    daily_data.loc[:, 'T1_On'] = daily_data.loc[:, 'T1-Power'].apply(lambda x: 1 if x>0 else 0)
    daily_data.loc[:, 'T2_On'] = daily_data.loc[:, 'T2-Power'].apply(lambda x: 1 if x>0 else 0)
    daily_data.loc[:, 'T3_On'] = daily_data.loc[:, 'T3-Power'].apply(lambda x: 1 if x>0 else 0)
    daily_data.loc[:, 'T4_On'] = daily_data.loc[:, 'T4-Power'].apply(lambda x: 1 if x>0 else 0)
    
    # Create daily dash board
    fig = plt.figure(1, figsize=(11.69, 16.54)) # Has 6 subplots
    fig.suptitle('LHH : Dashboard for Day: ' + day_label, fontsize=14, fontweight='bold')

    daily_data.loc[:,'TimeOnly'] = [time.time() for time in daily_data.index]
    xticks = ['0:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00', '23:50']
    #fig.title("Results for Entire Survey Period For: ")
    
    # Create wind rose plot in top left position
    title_date = "Wind Polar Plot: " + day_label
    polarShow(fig, 421, daily_data, title_date, 2, 9, 0)

    # Create AM radar plot in top right position
    title_date = "AM Radar Plot: " + day_label
    polarShow(fig, 422, daily_data, title_date,  2, 9, 1)

    # Create Acoustic plot as row two (middle-top)
    ax  = fig.add_subplot(4, 2, (3, 4))
    ax2 = ax.twinx()
    ax.plot(daily_data['TimeOnly'], daily_data['Noise'], 'b-', label='LA90-HL', linewidth=2)

    #ax.plot(daily_data['TimeOnly'], daily_data['Rated(50-200Hz)/dB'], 'k-', label='Rated(50)', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['LA90(RES)'], 'c-', label='LA90-RES', linewidth=2)

    ax.plot(np.nan, 'ro-', label = 'AM: 50-200Hz-HL', linewidth=2)
    ax.plot(np.nan, 'go-', label = 'AM:100-400Hz-HL', linewidth=2)
    ax.plot(np.nan, 'ro-', label = 'AM: 50-200Hz-RES', linewidth=2)
    ax.plot(np.nan, 'go-', label = 'AM:100-400Hz-RES', linewidth=2)

    #ax.plot(np.nan, 'c-', label = 'Rainfall', linewidth=2, alpha=0.15)
    ax.set_ylabel('LA90 Noise Immission Level / dB', color ='b')
    ax.set_ylim(25,60)
    ax.grid('on',which=u'major', axis=u'both')
    ax2.plot(daily_data['TimeOnly'], daily_data['AM(50-200Hz)/dB'],  'ro-', linewidth=2)
    ax2.plot(daily_data['TimeOnly'], daily_data['AM(100-400Hz)/dB'], 'go-', linewidth=2)
    ax2.plot(daily_data['TimeOnly'], daily_data['AM-RES (50-200Hz)'],  'mx-', linewidth=2)
    ax2.plot(daily_data['TimeOnly'], daily_data['AM-RES (100-400Hz)'], 'yx-', linewidth=2)
    ax2.set_ylabel('AM, Modulation Depth / dB', color ='r')
    ax2.set_ylim(0,7)
    #ax.set_xlim(dailyData['TimeOnly'].min(), dailyData['TimeOnly'].max())
    ax.set_xlim(xticks[0], xticks[8])
    ax.set_xticks(xticks, minor = False)
    ax.set_xticklabels( xticks)
    ax.set_xlabel('')
    #ax2.set_xlim(dailyData['TimeOnly'].min(), dailyData['TimeOnly'].max())
    ax2.set_xlim(xticks[0], xticks[8])
    ax2.set_xticks(xticks, minor = False)
    ax2.set_xticklabels( xticks)
    ax2.set_xlabel('')
    ax.legend(loc='best')
    
    # # Rainfall stuff
    # tenMin = dt.timedelta(minutes=10)
    # for clockTime in daily_data.index:
    #     if daily_data.loc[clockTime, 'Rain'] > 0:
    #         nextClockTime = clockTime + tenMin
    #         if nextClockTime.time() > clockTime.time():
    #             plt.axvspan(clockTime.time(), nextClockTime.time(), facecolor='c', alpha=0.25,linewidth=0)

    # Create meteorological plot as row three (middle-bottom)
    ax  = fig.add_subplot(4,2,(5,6))
    ax2 = ax.twinx()
    ax.plot(daily_data['TimeOnly'], daily_data['Wind Speed'], 'b-', label='Wind Speed', linewidth=2)
    #ax.plot(daily_data['TimeOnly'], daily_data['V-20'], 'g-', label='LIDAR-WS (20m)', linewidth=2)
    ax.plot(np.nan, 'r-', label = 'Wind Direction', linewidth=2)
    #ax.plot(np.nan, 'm-', label = 'LIDAR-Dir (20m)', linewidth=2)
#    ax.set_ylabel('Hub Height Wind Speed / m/s', color ='b')
#    ax.set_ylim(0,40)
#    yticks = range(0,45,5)
    ax.set_ylabel('Standardised 10m Wind Speed / m/s', color ='b')
    ax.set_ylim(0,20)
    yticks = range(0,25,5)
    ax.set_yticks(yticks, minor=False)
    ax.grid('on',which=u'major', axis=u'both')
#    ax.axhspan(3, 14, facecolor='b', alpha=0.25)
#    ax.axhspan(2, 10, facecolor='b', alpha=0.25)
    ax.axhspan(2, 9, facecolor='b', alpha=0.25)
    ax2.plot(daily_data['TimeOnly'], daily_data['Wind Direction'], 'r-', linewidth=2)
    #ax2.plot(daily_data['TimeOnly'], daily_data['Dir-20'], 'm-', label='LIDAR-Dir(20m)', linewidth=2)
#    ax2.axhspan(232, 307, facecolor='r', alpha=0.25)
    ax2.axhspan(200, 320, facecolor='r', alpha=0.25)
    ax2.set_ylabel('Wind Direction / deg', color = 'r')
    ax2.set_ylim(0,360)
    yticks2 = range(0,405,45)
    ax2.set_yticks(yticks2, minor=False)
    ax.set_xlim(xticks[0], xticks[8])
    ax.set_xticks(xticks, minor = False)
    ax.set_xticklabels( xticks)
    ax.set_xlabel('')
    ax2.set_xlim(xticks[0], xticks[8])
    ax2.set_xticks(xticks, minor = False)
    ax2.set_xticklabels( xticks)
    ax2.set_xlabel('')
    ax.legend(loc='best')


    # Create SCADA plot as row four (bottom)
    ax  = fig.add_subplot(4,2,(7,8))
    ax2 = ax.twinx()
    ax.plot(daily_data['TimeOnly'], daily_data['T1-Power'], 'r-', label='T1', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T2-Power'], 'b-', label='T2', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T3-Power'], 'g-', label='T3', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T4-Power'], 'm-', label='T4', linewidth=2)
    ax.plot(np.nan, 'r:', label = 'Shear-UR', linewidth=2)
    ax.plot(np.nan, 'b:', label = 'Shear-LR', linewidth=2)
    ax.set_ylim(0,2200)
    yticks = range(0,2400,200)
    ax.set_yticks(yticks, minor=False)
    ax.set_xlim(xticks[0], xticks[8])
    ax.set_xticks(xticks, minor = False)
    ax.set_xticklabels( xticks)
    ax.set_xlabel('Time (24 hour clock)')
    ax.set_ylabel('Turbine Power / kW')

    # ax2.plot(daily_data['TimeOnly'], daily_data['Shear-UR'], 'r:', linewidth=2)
    # ax2.plot(daily_data['TimeOnly'], daily_data['Shear-LR'], 'b:', linewidth=2)
    # ax2.set_ylabel('Wind Shear Exponent', color = 'r')
    # ax2.set_ylim(-0.1,1.0)
    # #yticks2 = range(0,405,45)
    # yticks2 = [-0.1, 0.0, 0.1, 0.2, 0.3, 0.4,
    #             0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    # ax2.set_yticks(yticks2, minor=False)
    # ax2.set_xlim(xticks[0], xticks[8])
    # ax2.set_xticks(xticks, minor = False)
    # ax2.set_xticklabels( xticks)
    # ax2.set_xlabel('')

    ax.grid('on', which=u'major', axis=u'both')
    ax.legend(loc='best')

    FigName = "LHF-Dashboard for " + day_label + ".png"
    FigName = DIRECTORY_NAME + "\\" + FigName
    plt.savefig(FigName, dpi=600, facecolor='w', edgecolor='w',
                orientation='portait', papertype='a3', format='png',
                transparent=False, frameon=None)
    plt.close(1)
    return daily_data

    
#%% Input variables

#DIRECTORY_NAME = r'V:\Noise\Garreg Lwyd\RES Statutory Nuisance at Lower House Farm - Winter 2017\Key-Results'
#DIRECTORY_NAME = r'C:\Users\bass\Downloads'
DIRECTORY_NAME = r'C:\Users\bass\Downloads\GarregLwyd\LHH-CSV'
#input_file     = r'Survey Progress - Lower House Farm.xlsx'
input_file     = r'Survey Progress - Lower House Holt.xlsx'
input_sheet    = r'Raw Data'
config_sheet   = r'Status Summary'

# # LIDAR Data
DIRECTORY2     = r'C:\Users\bass\Downloads\GarregLwyd\RES-CSV'
#input_file2    = r'M812WALglh005 - Garreg Lwyd Hill-Latest.xlsx'
#input_file2    = r'M812WALglh160718-270918.xlsx'
input_file2    = r'M812WALglh160718-121218.xlsx'
input_sheet2   = r'1'


#%% Read input data

data = pd.read_excel(os.path.join(DIRECTORY_NAME,input_file),input_sheet, header = [0])
#data = pd.read_excel(os.path.join(DIRECTORY_NAME,inputFile),inputSheet, index_col = [0], header = [0])
print "Dataset    - Initial length (hours):{:6n}".format(len(data))
data = data.rename(columns = {data.columns[0]:'Time'})


#%% Read config data

config       = pd.read_excel(os.path.join(DIRECTORY_NAME,input_file),config_sheet, header = [3,4])
config.index = config[config.columns[0]]
del config[config.columns[0]]
#config = config.rename(columns={config.columns[16][0]: 'Description'})
print "Strategies - Total number available:{:6n}".format(len(config))


#%% Read LIDAR data

lidar = pd.read_excel(os.path.join(DIRECTORY2,input_file2),input_sheet2, skiprows = 1)
#data = pd.read_excel(os.path.join(DIRECTORY_NAME,inputFile),inputSheet, index_col = [0], header = [0])
print "LIDAR data - Initial length (hours):{:6n}".format(len(lidar))
#data = data.rename(columns = {data.columns[0]:'Time'})

#lidar['Date & Time Stamp'] = pd.to_datetime(data['Date & Time Stamp'])
lidar['Date & Time Stamp'] = pd.to_datetime(lidar['Date & Time Stamp'], dayfirst = True, format = '%d/%m/%Y %H:%M:%S', exact = True)
lidar.index   = lidar['Date & Time Stamp']
del lidar['Date & Time Stamp']

for header in lidar.columns:
    if ('m812WALglh' in header) and ('AnemometerMean' in header) and ('Horizontal_Wind_Speed' in header):
        if '125m' in header:
            lidar = lidar.rename(columns = {header:'V-125'})
        elif '75m' in header:
            lidar = lidar.rename(columns = {header:'V-75'})
        elif '25m' in header:
            lidar = lidar.rename(columns = {header:'V-25'})
        elif '20m' in header:
            lidar = lidar.rename(columns = {header:'V-20'})
    if ('m812WALglh' in header) and ('WindvaneMean' in header) and ('Wind_Direction' in header):
        if '20m' in header:
            lidar = lidar.rename(columns = {header:'Dir-20'})

# Get rid of everything other than mean horizontal wind speeds at 25, 75 and 125 m
lidar = lidar[['V-125', 'V-75', 'V-25', 'V-20', 'Dir-20']]

# Now calculate wind shear for upper and lower halves of rotor
#lidar['Shear-UR'] = math.log(lidar['V_125'] / lidar['V_75'])/math.log(125.0/75.0)
#lidar['Shear-LR'] = math.log(lidar[ 'V_75'] / lidar['V_25'])/ math.log( 75.0/25.0)
#temp = lidar.loc[(lidar['V_125'] != np.nan) & (lidar['V_75'] != np.nan) & (lidar['V_75'] > 0), ['Std', 'Avg']]
temp = lidar.loc[(lidar['V-125'] >=0) & (lidar['V-75'] > 0), ['V-125', 'V-75']]
temp['Shear-UR']  = np.log(lidar['V-125']/lidar['V-75'])/ np.log(125.0/75.0)
temp = temp[['Shear-UR']]
lidar = pd.concat([lidar,temp], axis = 1)
del temp

temp = lidar.loc[(lidar['V-75'] >=0) & (lidar['V-25'] > 0), ['V-75', 'V-25']]
temp['Shear-LR']  = np.log(lidar['V-75']/lidar['V-25']) / np.log(75.0/25.0)
temp = temp[['Shear-LR']]
lidar = pd.concat([lidar,temp], axis = 1)
del temp

#temp.loc[:,'TI-3'] = (100.0 * temp.loc[:,'Std']) / temp.loc[:,'Avg']
#lidar['Shear-UR'] = 0.25
#lidar['Shear-LR'] = 0.35


#%% Now delete any bad data resulting from rainfall or external sources of noise

#data = data[data['Rain'] == 0]             # Pull out data not influenced by rainfall
#del data['Rain']                           # No longer need this column since all '0'
#print "Dataset - No rain length (hours):{:6n}".format(len(data))

#data = data[data['Over'] == '-']           # Pull out data not suffering from under/over lad
#del data['Over']                           # No longer need this column since all '-'
#del data['Wind speed at SLM height']       # No longer need this column
#print "Dataset - No overloads   (hours):{:6n}".format(len(data))

#data = data[data['External'] == 0]         # Pull out data not suffering from external corruption
#del data['External']                       # No longer need this column since all '0'
#print "Dataset - No external    (hours):{:6n}".format(len(data))

#data = data[data['Good Data'] == 1]         # Pull out data not suffering from external corruption
#del data['Good Data']                      # No longer need this column since all '0'
#print "Dataset - Good Data        (10min) :{:6n}".format(len(data))


#%% Process data and create a dashboard for each day of data

data['Time'] = pd.to_datetime(data['Time'], dayfirst=True, format='%d/%m/%Y %H:%M:%S', exact=True)
data.index   = data['Time']
del data['Time']

data['Hour'] = data.index.hour
#data         = data[data.columns[0:22]] # Focus on those columns containing useful data
data         = data.replace('No Data', np.nan)

# Add in LIDAR data
# data = pd.concat([data, lidar], axis=1)
#
# data['Penalty(100-400Hz)/dB'] = data['AM(100-400Hz)/dB'].apply(AM_penalty)
# data['Penalty(50-200Hz)/dB']  = data['AM(50-200Hz)/dB'].apply(AM_penalty)
# data['Rated(100-400Hz)/dB']   = data['Noise'].add(data['Penalty(100-400Hz)/dB'])
# data['Rated(50-200Hz)/dB']    = data['Noise'].add(data['Penalty(50-200Hz)/dB'])


#%% Print out individual days

dates    = data.index
startDay = dt.datetime(data.index.min().year,data.index.min().month,data.index.min().day)
stopDay  = dt.datetime(data.index.max().year,data.index.max().month,data.index.max().day)
day      = dt.timedelta(days=1)
date1    = startDay

while date1 <= stopDay:
    if date1 >= dt.datetime(2018, 12, 12, 0, 0) and date1 < dt.datetime(2019, 1, 11, 0, 0):  # line for testing only
        dailyData = data[(dates >= date1) & (dates < (date1 + day))]
        daily_data = dash_board(dailyData)
        print "%s" % str(len(dailyData)),
        print "\t%5.1f" % (float(100*len(dailyData))/float(144)),
        print "\t", date1,
        print "\t", date1 + day
    date1 = date1 + day
