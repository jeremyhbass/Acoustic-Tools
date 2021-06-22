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
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

#%% Function to draw a radar plot of data - (r,theta)

def polarShow(fig, subplot, df, polarTitle, sWS, eWS, data_type):
    r      = df[df.columns[0]]
    theta  = np.radians(df[df.columns[1]])
    if data_type == 0: # Wind rose
        area = 20
        colors = df[df.columns[0]]
    elif data_type == 1: # AM radar plot
        area   = df[df.columns[52]]**2
        colors = df[df.columns[52]]
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
        ax.set_title('Amplitude Modulation: 100 - 400 Hz')
        #ax.set_title('Amplitude Modulation: 50 - 200 Hz')
  
    drawSector(ax, np.radians(120), np.radians(180), sWS, eWS)
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
    
    ax.plot([np.radians(162.0),np.radians(162.0)], [0,20], color='k', linewidth=2) # T1
#    ax.plot([np.radians(137.7),np.radians(137.7)], [0,20], color='k', linewidth=2) # T3
#    ax.plot([np.radians(132.1),np.radians(132.1)], [0,20], color='k', linewidth=2) # T5
#    ax.plot([np.radians(120.6),np.radians(120.6)], [0,20], color='k', linewidth=2) # T6
    ax.plot([np.radians(125.0),np.radians(125.0)], [0,20], color='k', linewidth=2) # T7
#    ax.plot([np.radians(124.2),np.radians(124.2)], [0,20], color='k', linewidth=2) # T8
    ax.plot([np.radians(112.6),np.radians(112.6)], [0,20], color='k', linewidth=2) # T9
    ax.text(np.radians(162.0), 20, 'T1', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
#    ax.text(np.radians(137.7), 20, 'T3', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
#    ax.text(np.radians(132.1), 20, 'T5', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
#    ax.text(np.radians(120.6), 20, 'T6', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(125.0), 20, 'T7', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
#    ax.text(np.radians(124.2), 20, 'T8', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(112.6), 20, 'T9', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    
    return


#%% Routine to create daily dashboard of data

def dash_board(daily_data):

    # Set up day label
    day_label = "{:04n}-{:02n}-{:02n}".format(daily_data.index[0].year,
                                              daily_data.index[0].month,
                                              daily_data.index[0].day)
   
    # Create daily dash board
    fig = plt.figure(1, figsize=(11.69, 16.54)) # Has 6 subplots
    fig.suptitle("Dashboard for Day: " + day_label, fontsize=14, fontweight='bold')

    # daily_data.loc[:,'TimeOnly'] = [time.time() for time in daily_data.index]
    daily_data.loc[:, 'TimeOnly'] = pd.date_range('0:00', '23:50', freq='10min')
    # daily_data['TimeOnly'].date_range('0:00', '23:50', freq='10min')
    # xxx = [time.time() for time in daily_data.index]
    # print xxx, len(xxx), len(daily_data)
    # daily_data['TimeOnly'] = xxx
    # xxx = pd.date_range('0:00', '23:50', freq='10min')
    # daily_data.loc[:, 'TimeOnly'] = xxx[:]
    # daily_data.TimeOnly = xxx
    # pd.date_range('0:00', '23:50', freq='10min')

    xticks = ['0:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00', '23:50']
    # fig.title("Results for Entire Survey Period For: ")
    
    #df.TimeOnly = pd.to_timedelta(df.Time + ':00', unit='h')
    #df.index = df.index + df.Time
    #df = df.drop('Time', axis=1)
    #df.index.name = 'Date'
    #print (df)
  
    # Create wind rose plot in top left position
    title_date = "Wind Polar Plot: " + day_label
    polarShow(fig, 421, daily_data, title_date, 3, 11, 0)


    # Create AM radar plot in top right position
    title_date = "AM Radar Plot: " + day_label
    polarShow(fig, 422, daily_data, title_date,  3, 11, 1)


    # Create Acoustic plot as row two (middle-top)   
    ax  = fig.add_subplot(4,2,(3,4))
    ax2 = ax.twinx()
    ax.plot(daily_data['TimeOnly'], daily_data['LAeq-dB(A)'], 'b-', label='LAeq', linewidth=2)
    ax.plot(np.nan, 'ro-', label = 'AM: 50-200Hz', linewidth=2)
    ax.plot(np.nan, 'go-', label = 'AM:100-400Hz', linewidth=2)
    ax.set_ylabel('LAeq Noise Immission Level / dB', color ='b')
    ax.set_ylim(25,65)
    ax.grid('on',which=u'major', axis=u'both')
    ax2.plot(daily_data['TimeOnly'], daily_data['F-AM(50-200Hz)/dB'],  'ro-', linewidth=2)
    ax2.plot(daily_data['TimeOnly'], daily_data['F-AM(100-400Hz)/dB'], 'go-', linewidth=2)
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


    # Create meteorological plot as row three (middle-bottom)
    ax  = fig.add_subplot(4,2,(5,6))
    ax2 = ax.twinx()
    ax.plot(daily_data['TimeOnly'], daily_data['Wind Speed'], 'b-', label='Wind Speed', linewidth=2)
    ax.plot(np.nan, 'r-', label = 'Wind Direction', linewidth=2)
#    ax.set_ylabel('Hub Height Wind Speed / m/s', color ='b')
#    ax.set_ylim(0,40)
#    yticks = range(0,45,5)
    ax.set_ylabel('Hub Height (91.5m) Wind Speed / m/s', color ='b')
    ax.set_ylim(0,25)
    yticks = range(0,30,5)
    ax.set_yticks(yticks, minor=False)
    ax.grid('on',which=u'major', axis=u'both')
#    ax.axhspan(3, 14, facecolor='b', alpha=0.25)
    ax.axhspan(3, 11, facecolor='b', alpha=0.25)
    ax2.plot(daily_data['TimeOnly'], daily_data['Wind Direction'], 'r-', linewidth=2)
    ax2.axhspan(120, 180, facecolor='r', alpha=0.25)
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
    ax.plot(daily_data['TimeOnly'], daily_data['T01-Power'], 'r-', label='T1', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T03-Power'], 'b-', label='T3', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T05-Power'], 'g-', label='T5', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T06-Power'], 'm-', label='T6', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T07-Power'], 'c-', label='T7', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T08-Power'], 'y-', label='T8', linewidth=2)
    ax.plot(daily_data['TimeOnly'], daily_data['T09-Power'], 'k-', label='T9', linewidth=2)
    ax.set_ylim(0,4500)
    yticks = range(0,5000,500)
    ax.set_yticks(yticks, minor=False)
    ax.set_xlim(xticks[0], xticks[8])
    ax.set_xticks(xticks, minor = False)
    ax.set_xticklabels( xticks)
    ax.set_xlabel('Time (24 hour clock)')
    ax.set_ylabel('Turbine Power / kW')
    ax.grid('on', which=u'major', axis=u'both')
    ax.legend(loc='best')


    FigName = "Dashboard for " + day_label + ".png"
    FigName = DIRECTORY_NAME + "\\" + FigName
    plt.savefig(FigName, dpi=600, facecolor='w', edgecolor='w',
                orientation='portait', papertype='a3', format='png',
                transparent=False, frameon=None)
    plt.close(1)
    return

    
#%% Input variables

#DIRECTORY_NAME = r'V:\Noise\Garreg Lwyd\RES Statutory Nuisance at Lower House Farm - Winter 2017\Key-Results'
DIRECTORY_NAME = r'E:\Vardafjellet\Analysis'
inputFile      = r'SurveyResults-Vardafjell.xlsx'
inputSheet     = r'MainData'
# config_sheet   = r'Status Summary'


#%% Read input data

data = pd.read_excel(os.path.join(DIRECTORY_NAME, inputFile), inputSheet, header = [0])
#data = pd.read_excel(os.path.join(DIRECTORY_NAME,inputFile),inputSheet, index_col = [0], header = [0])
print "Dataset    - Initial length (hours):{:6n}".format(len(data))
data = data.rename(columns = {data.columns[0]:'Time'})

#data = pd.read_excel(os.path.join(DIRECTORY_NAME,inputFile),inputSheet)


#%% Read config data

# config       = pd.read_excel(os.path.join(DIRECTORY_NAME,input_file),config_sheet, header = [3,4])
# config.index = config[config.columns[0]]
# del config[config.columns[0]]
# config = config.rename(columns={config.columns[16][0]: 'Description'})
# print "Strategies - Total number available:{:6n}".format(len(config))


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
print "Dataset - Good Data        (10min) :{:6n}".format(len(data))


#%% Process data and createa dashboard for each day of data

data['Time'] = pd.to_datetime(data['Time'], dayfirst = True, format = '%d/%m/%Y %H:%M:%S', exact = True)
data.index   = data['Time']
del data['Time']

data['Hour'] = data.index.hour
#data         = data[data.columns[0:22]] # Focus on those columns containing useful data
data         = data.replace('No Data', np.nan)

# dates    = data.index
# startDay = dt.datetime(data.index.min().year,data.index.min().month,data.index.min().day)
# stopDay  = dt.datetime(data.index.max().year,data.index.max().month,data.index.max().day)
# day      = dt.timedelta(days=1)
# date1    = startDay

# while date1 <= stopDay:
#     if date1 >= dt.datetime(2021, 6, 6, 0, 0):  # line for testing only
#         dailyData = data[(dates >= date1) & (dates < (date1 + day))]
#         dash_board(dailyData)
#         print "%s" % str(len(dailyData)),
#         print "\t%5.1f" % (float(100*len(dailyData))/float(144)),
#         print "\t", date1,
#         print "\t", date1 + day
#     date1 = date1 + day


#%% Create some overall plots to capture progress towards solution

#for indy, col in enumerate(data.columns):
#    print indy, col

# data = data.resample('1D').count()
# data = data.resample('1W').count()
data = data.resample('1M').count()
#print data['F-AM(100-400Hz)/dB'].head()
#print data['F-AM(100-400Hz)/dB'].tail()
print data

# xxx = pd.DataFrame()
# ##xxx['AM-HF'] = data[data.columns[8]].resample('D').count()
# xxx['AM-LF'] = data[data.columns['F-AM(50-200Hz)/dB']].resample('1D').count()
# #xxx['AM-HF'] = data[data.columns['F-AM(100-400Hz)/dB']].resample('M').mean()
# #xxx['AM-LF'] = data[data.columns['F-AM(50-200Hz)/dB']].resample('M').mean()
# ##xxx['AM-HF'] = data[data.columns[8]].resample('W').count()
# ##xxx['AM-LF'] = data[data.columns[6]].resample('W').count()
# ##xxx['AM-HF'] = data[data.columns[8]].resample('M').count()
# ##xxx['AM-LF'] = data[data.columns[6]].resample('M').count()
plt.figure()
#plt.plot(data.index, data[ 'F-AM(50-200Hz)/dB'], label= '50-200 Hz')
#plt.plot(data.index, data['F-AM(100-400Hz)/dB'], label='100-400 Hz')
# plt.bar(data.index, data['F-AM(100-400Hz)/dB'], width=0.5, color='g', label='100-400 Hz', align='edge')
# plt.bar(data.index,  data['F-AM(50-200Hz)/dB'], width=-0.5, color='b', label='50-200 Hz', align='edge')
# plt.bar(data.index, data['F-AM(100-400Hz)/dB'], width=3.5, color='g', label='100-400 Hz', align='edge')
# plt.bar(data.index,  data['F-AM(50-200Hz)/dB'], width=-3.5, color='b', label='50-200 Hz', align='edge')
plt.bar(data.index, data['F-AM(100-400Hz)/dB'], width=15, color='g', label='100-400 Hz', align='edge')
plt.bar(data.index,  data['F-AM(50-200Hz)/dB'], width=-15, color='b', label='50-200 Hz', align='edge')
#plt.bar(data.index, data['F-AM(100-400Hz)/dB'], width=7, color='g', label='100-400 Hz')
plt.title('Change in Frequency of Occurence of OAM with Time')
plt.ylabel('No. of 10 min periods containing OAM')
plt.xlabel('Week of Measurement')
plt.grid('on',which=u'major', axis=u'both')
plt.legend(loc='best')
plt.tight_layout()
plt.show()