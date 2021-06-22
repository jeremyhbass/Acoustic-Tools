# -*- coding: utf-8 -*-
"""

Works on the filtered AM results from vardafjell - 12 Mar 2021

Created on Tue Mar 08 09:20:29 2016

Scenarios:
1   Noise monitoring undertaken by RES - Strategy 1
				
Noise management implemented:					
03/11/2017      Noise monitoring starts at LHF		
Pre-21/11/17    All in Mode 0			
21/11/2017 09:30-11:30	Strategy 1	T1-T4 in Mode 5 when:	
		Time between 18:00 and 09:00	
		Wind direction 232-307	
		Hub height wind speeds of 3-14m/s
04/12/2017 14:00	Strategy 2	As above but all times of day	
05/12/2017 13:30	Strategy 3	T1-T4 in AM Mode when:	
		All times of day		
		Wind direction 232-307	
		Hub height wind speeds of 3-14m/s
13/12/2017 10:00	Strategy 4	T3 & T4 off
20/12/2017 08:30-13:30		Testing various combinations of T3 & T4 on/off. Turbines appear to have been left on afterwards

@author: bass
"""
# %%

from __future__ import division
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt


# %% Function to determine AM penalty for given level of noise immission and AM

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
    return(penalty)


# %% Function to remove all missing/blank data from a Pandas dataframe

def filterData(df):
    count = len(df)
    df = df.dropna()
    print "{:n}\t{:n}\t{:5.1f}".format(count, len(df), 100*len(df)/count)
    return(df, count)


# %%

def polarShow(df, polarTitle, sWS, eWS, data_type):
    r = df[df.columns[0]]
    theta = np.radians(df[df.columns[1]])
    # theta  = df[df.columns[1]] * math.pi / 180.0
    if data_type == 0:  # Wind rose
        # area   = df[df.columns[0]]**2
        area = 20
        colors = df[df.columns[0]]
    elif data_type == 1:  # AM radar plot
        if G_RANGE == 1:  # 50 - 200 Hz
            area = df[df.columns[51]]**2
            colors = df[df.columns[51]]
        elif G_RANGE == 2:  # 100 - 400 Hz
            area = df[df.columns[52]]**2
            colors = df[df.columns[52]]
        elif G_RANGE == 3:  # 200 - 800 Hz
            area = df[df.columns[53]]**2
            colors = df[df.columns[53]]
    fig = plt.figure(figsize=(9, 9))
    fig.suptitle(polarTitle, fontsize=14, fontweight='bold')
    ax = fig.add_subplot(111, projection='polar', polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 16)
    # ax.set_facecolor(color = 'b', alpha = 0.15)
    # ax.set_facecolor(color = 'b')
#    ax.bar(np.radians( 90), eWS-2, width = np.radians(90), alpha = 0.15, bottom=2, color = 'r', edgecolor='k', linewidth=2)
#    ax.bar(np.radians( 90), eWS-2, width = np.radians(90), bottom=2, color = '', edgecolor='k', linewidth=2)
#    ax.bar(np.radians(270), eWS-2, width = np.radians(90), alpha = 0.15, bottom=2, color = 'r')
#    ax.bar(np.radians(270), eWS-2, width = np.radians(90), bottom=2, color = '', edgecolor='k', linewidth=2)
#    ax.bar(np.radians(  0), 16, width = np.radians(90), alpha = 0.15, color = 'b')
#    ax.bar(np.radians(180), 16, width = np.radians(90), alpha = 0.15, color = 'b')
#    ax.bar(np.radians( 90),  6, width = np.radians(90), alpha = 0.15, bottom=10, color = 'b')
#    ax.bar(np.radians(270),  6, width = np.radians(90), alpha = 0.15, bottom=10, color = 'b')
#    ax.bar(np.radians( 90),  2, width = np.radians(90), alpha = 0.15, color = 'b')
#    ax.bar(np.radians(270),  2, width = np.radians(90), alpha = 0.15, color = 'b')

    if data_type == 0:   # Wind rose
        c = plt.scatter(theta, r, s = area, c=colors, cmap=plt.cm.YlOrRd, vmin=0, vmax=16)
        cbar2 = fig.colorbar(c, fraction=0.04, pad=0.15, ticks=[0, 4, 8, 12, 16])
        cbar2.ax.set_yticklabels(['0 m/s', '4 m/s', '8 m/s', '12 m/s', '16 m/s'])
    elif data_type == 1:   # AM radar plot
        c = plt.scatter(theta, r, s = area, c=colors, cmap=plt.cm.YlOrRd, vmin=2, vmax=6)
        cbar2 = fig.colorbar(c, fraction=0.04, pad=0.15, ticks=[2, 4, 6])
        cbar2.ax.set_yticklabels(['2 dB', '4 dB', '6 dB'])
        # create title
        if G_RANGE == 1:
            ax.set_title(' 50 - 200 Hz 1/3 Octave Bands')
        elif G_RANGE == 2:
            ax.set_title('100 - 400 Hz 1/3 Octave Bands')
        elif G_RANGE == 3:
            ax.set_title('200 - 800 Hz 1/3 Octave Bands')

    if data_type == 1:   # AM Radar plot
        # ax.bar(np.radians( 45), eWS-2, width = np.radians(90), alpha = 0.15, bottom=2, color = 'r')
        # ax.bar(np.radians(225), eWS-2, width = np.radians(90), alpha = 0.15, bottom=2, color = 'r')
        drawSector(ax, np.radians(120), np.radians(180), sWS, 11.0, 1)
        drawSector(ax, np.radians(290), np.radians(360), 3.0, 11.0, 0)
        # drawSector(ax, np.radians( 45), np.radians(135), sWS, eWS, 0)      
    return


# %%

def drawSector(ax, startRad, endRad, startWS, endWS, index):

    # ax.set_theta_direction(-1)    
    # create data set representing curved line
    theta = np.arange(startRad, endRad, 0.01)
    # multiply radius list by 0 to keep correct structure but all zero
    r = (theta * 0)
    if index:
        ax.plot([startRad, startRad], [startWS, endWS], color='r', linewidth=2)
        ax.plot([endRad, endRad],     [startWS, endWS], color='r', linewidth=2)
        ax.plot(theta, r+startWS, color='r', linewidth=2)
        ax.plot(theta, r+endWS,   color='r', linewidth=2)
        # ax.fill([startRad,endRad], [startWS,endWS], facecolor='r', alpha=0.5)
    else:
        ax.plot([startRad, startRad], [startWS, endWS], color='b', linewidth=2)
        ax.plot([endRad, endRad],     [startWS, endWS], color='b', linewidth=2)
        ax.plot(theta, r+startWS, color='b', linewidth=2)
        ax.plot(theta, r+endWS,   color='b', linewidth=2)
        # ax.fill([startRad,endRad], [startWS,endWS], facecolor='b', alpha=0.5)

    ax.plot([np.radians(162.0),np.radians(162.0)], [0,20], color='k', linewidth=2)  # T1
    ax.plot([np.radians(137.7),np.radians(137.7)], [0,20], color='k', linewidth=2)  # T3
    ax.plot([np.radians(132.1),np.radians(132.1)], [0,20], color='k', linewidth=2)  # T5
    ax.plot([np.radians(120.6),np.radians(120.6)], [0,20], color='k', linewidth=2)  # T6
    ax.plot([np.radians(125.0),np.radians(125.0)], [0,20], color='k', linewidth=2)  # T7
    ax.plot([np.radians(124.2),np.radians(124.2)], [0,20], color='k', linewidth=2)  # T8
    ax.plot([np.radians(112.6),np.radians(112.6)], [0,20], color='k', linewidth=2)  # T9
    ax.text(np.radians(162.0), 20, 'T1', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(137.7), 20, 'T3', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(132.1), 20, 'T5', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(120.6), 20, 'T6', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(125.0), 20, 'T7', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(124.2), 20, 'T8', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(112.6), 20, 'T9', bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    # ax.fill([np.radians(262),np.radians(316)], [2,12], facecolor='b', alpha=0.25)

    # Helful descriptors of relationship of turbine and nearest houses in terms of wind direciotn
    ax.text(np.radians(312), 16,    'UPWIND', bbox={'facecolor':'green', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(132), 14,  'DOWNWIND', bbox={'facecolor':'green', 'alpha':0.5, 'pad':2})
    ax.text(np.radians(222), 16, 'CROSSWIND', bbox={'facecolor':'green', 'alpha':0.5, 'pad':2})
    ax.text(np.radians( 42), 14, 'CROSSWIND', bbox={'facecolor':'green', 'alpha':0.5, 'pad':2})

    # Draw some 30 deg sectors
    #start_angle = 278
#    start_angle = 0
#    angles = np.arange(0,360,45) + start_angle
#    angles = angles % 360
#    for i in angles:
#        ax.bar(np.radians(i), 4, width = np.radians(45), alpha = 0.25)
#        ax.bar(np.radians(i), 4, width = np.radians(45), alpha = 0.25, bottom=4)
#        ax.bar(np.radians(i), 4, width = np.radians(45), alpha = 0.25, bottom=8)
#        ax.bar(np.radians(i), 4, width = np.radians(45), alpha = 0.25, bottom=12)
#        ax.plot([np.radians(i),np.radians(i),np.radians(i+45),np.radians(i+45)], [0,10,10,0], color='g', linewidth=2, alpha = 0.25)
#        ax.text(np.radians(i), 20,  i, bbox={'facecolor':'red', 'alpha':0.5, 'pad':2})
    return


#%% Create some boxplots for each mitigation option

def box_plot(box_data, freq_range, in_file, index):
    plt.figure()
    box_data['WS-Int'] = box_data['Wind Speed'].round(0)
    box_dict = box_data.boxplot(column = box_data.columns[6], by=['WS-Int'], return_type = 'dict')
    plt.axis([plt.axis()[0], plt.axis()[1], 0, 10])
    xticks = range(0,13,1)
    plt.xticks(xticks, xticks)
    plt.xlabel('Wind Speed / (m/s)')
    plt.ylabel('Modulation Depth (AM) / dB') 
    plt.grid('on',which=u'major', axis=u'both')
    plt.axhline(y=3, label='Limit',color='k',linewidth=1,linestyle='dashed')
    if freq_range == 1:
        fig_name = in_file + "_050_Boxplot_" + str(index) + ".png"
    elif freq_range == 2:
        fig_name = in_file + "_100_Boxplot_" + str(index) + ".png"
    elif freq_range == 3:        
        fig_name = in_file + "_200_Boxplot_" + str(index) + ".png"
    fig_name = os.path.join(DIRECTORY_NAME, fig_name)
    plt.savefig(fig_name, dpi=600, facecolor='w', edgecolor='w',
          orientation='landscape', papertype='a3', format='png',
          transparent=False, frameon=None)
    plt.clf() # Clear figure of data for re-use
    return box_dict


#%% Convert dict from pandas boxplot into a simple to use format 

def box_extract(box_dict):
    box_medians = [(median.get_xdata(), median.get_ydata()) for median in box_dict[0]["medians"]]
    box_x       = [(box_medians[i][0][0] + box_medians[i][0][1])/2 for i in range(0,len(box_medians))]
    box_y       = [box_medians[i][1][0] for i in range(0,len(box_medians))]
    return box_x,box_y


#%% Create polar plots

def polar_plot(plot_data, plot_title, v_low, v_high, freq_range, in_file, index, data_type):
    # create nice polar plot of data
    polarShow(plot_data, plot_title, v_low, v_high, data_type)
    if data_type == 0:
        fig_type = 'Rose'  # plot a wind rose
    elif data_type == 1:
        fig_type = 'Radar' # plot an AM radar chart
    if freq_range == 1:
        fig_name = in_file + "_050_" + fig_type + "_" + str(index) + ".png"
    elif freq_range == 2:
        fig_name = in_file + "_100_" + fig_type + "_" + str(index) + ".png"
    elif freq_range == 3:        
        fig_name = in_file + "_200_" + fig_type + "_" + str(index) + ".png"
    fig_name = os.path.join(DIRECTORY_NAME, fig_name)
    plt.savefig(fig_name, dpi=600, facecolor='w', edgecolor='w',
          orientation='landscape', papertype='a3', format='png',
          transparent=False, frameon=None)
    plt.clf() # Clear figure of data for re-use
    return


#%% Routine to fit polynomila and draw on a plot

def poly_plot(x_data, y_data, order, colour):
    poly_fit = np.poly1d(np.polyfit(x_data, y_data, order))
    min_value = max(x_data.min(),  2)
    max_value = min(x_data.max(), 10)
    x_values = np.linspace(min_value, max_value, 80)
    plt.plot(x_values, poly_fit(x_values), c=colour, linewidth = 2)
    return


#%% Routine to bin data and extract key results/inferences
    
def data_binning(df):
    if G_RANGE == 1:
        df_bin = df.groupby('WSBin')['LAeq-dB(A)', 'F-AM(50-200Hz)/dB'].agg(['count', np.mean])
    elif G_RANGE == 2:
        df_bin = df.groupby('WSBin')['LAeq-dB(A)', 'F-AM(100-400Hz)/dB'].agg(['count', np.mean])
    elif G_RANGE == 3:
        df_bin = df.groupby('WSBin')['LAeq-dB(A)', 'F-AM(200-800Hz)/dB'].agg(['count', np.mean])      
    df_bin['Rel Freq'] = df_bin[df_bin.columns[2]]/df_bin[df_bin.columns[0]] # Relative frequency of AM
    df_bin['Avg AM']   = df_bin[df_bin.columns[3]]*df_bin[df_bin.columns[4]] # Average level of AM
    df_bin['CVal']     = df_bin.index + 0.5 # Useful for plotting
    return df_bin

    
#%% Define input / static variables

G_DEBUG = 1    #0 - No            ; 1 - Yes
G_CUMUL = 0    #0 - Not cumulative; 1 - Cumulative
G_NORM  = 1    #0 - Not normalised; 1 - Normalised
# G_RANGE = 1    #1 - 50-200 Hz     ; 2 - 100-400 Hz
G_RANGE = 2    #1 - 50-200 Hz     ; 2 - 100-400 Hz ; 3 - 200-800 Hz
# G_RANGE = 3    #1 - 50-200 Hz     ; 2 - 100-400 Hz ; 3 - 200-800 Hz
DIRECTORY_NAME = r'E:\Vardafjellet\Analysis'
inputFile      = r'SurveyResults-Vardafjell.xlsx'
inputSheet     = r'MainData'
minLength      = 5 # Min number of data points before a box plot entry is drawn


#%% Read input data

##data = pd.read_excel(os.path.join(DIRECTORY_NAME,inputFile),inputSheet, index_col = 0)
data = pd.read_excel(os.path.join(DIRECTORY_NAME,inputFile), inputSheet)
print "Dataset - Initial length (hours):{:6n}".format(len(data))
data = data.rename(columns={data.columns[0]:'Time'})
data['Time'] = pd.to_datetime(data['Time'], format = r'%d/%m/%Y %H:%M:%S', exact=True)
data.index   = data['Time']
del data['Time']


#%% Now delete any bad data resulting from rainfall or external sources of noise

# Determine wind speed bin (0-1, 1-2, 2-3 etc)
data['Wind Speed'].replace('', np.nan, inplace=True)
data.dropna(subset=['Wind Speed'], inplace = True)
data['WSBin'] = data['Wind Speed'].apply(lambda x: int(x//1))

# Filter data for overall noise level
# data = data[data['LAeq-dB(A)'] >= 55]

#data[         'Penalty(LAeq'] = data[     'AM(LAeq)/dB'].apply(AM_penalty)
data[ 'Penalty(50-200Hz)/dB'] = data[ 'AM(50-200Hz)/dB'].apply(AM_penalty)
data['Penalty(100-400Hz)/dB'] = data['AM(100-400Hz)/dB'].apply(AM_penalty)
#data['Penalty(200-800Hz)/dB'] = data['AM(200-800Hz)/dB'].apply(AM_penalty)
#data[ 'Rated(50-200Hz)/dB']   = data['LAeq-dB(A)'].add(data['Penalty(50-200Hz)/dB'])
#data['Rated(100-400Hz)/dB']   = data['LAeq-dB(A)'].add(data['Penalty(100-400Hz)/dB'])

if G_DEBUG:                                       # Check columns
    print  '0: {}'.format(data.columns[ 0])       # HH Wind speed
    print  '1: {}'.format(data.columns[ 1])       # HH Wind Direction
    print '50: {}'.format(data.columns[50])       # AM: LAeq (filtered)
    print '51: {}'.format(data.columns[51])       # AM:  50-200 Hz (filtered)
    print '52: {}'.format(data.columns[52])       # AM: 100-400 Hz (filtered)
    print '53: {}'.format(data.columns[53])       # AM: 200-800 Hz (filtered)
#    print '58: {}'.format(data.columns[58])       # Rated Level:  50-200 Hz (filtered)
#    print '59: {}'.format(data.columns[59])       # Rated level: 100-400 Hz (filtered)

# if G_DEBUG:
#     for indy, col in enumerate(data.columns):
#         print indy, col

# Remove all empty strings and replace with NaNs
# data         = data.replace('', np.nan)

# #%% Convert index to pandas datetime & add hour of day

# # IGNORE THIS SECTION - REDUNDANT CODE

# ##data.index = pd.to_datetime(data.index)
data['Hour'] = data.index.hour

# startDay = dt.datetime(data.index.min().year,data.index.min().month,data.index.min().day).strftime('%d/%m/%Y')
# stopDay  = dt.datetime(data.index.max().year,data.index.max().month,data.index.max().day).strftime('%d/%m/%Y')
# if G_DEBUG:
#     print 'Start Date:{0:s}\tStop Date:{1:s}'.format(startDay, stopDay)

# ##data = data[data.columns[:19]]
# #data = data[data[data.columns[1]].isnull()]
# #data[data.columns[1]] = data[data.columns[1]].astype('float64')
# #data = data[data[data.columns[7]]<>'-']
# #data[data.columns[7]] = data[data.columns[7]].astype('int64')
# #data[data.columns[2]] = data[data.columns[2]].astype('float64')

# #%% Divide data up into different status groups

# # 0 - Baseline period;      All turbines in 42 dB Lden Mode
# # 1 - Mitigation Option 1;  As baseline, but T7 off 19:00-07:00
# # 2 - Mitigation Option 2;  T1-T4 in AM2
# # 3 - Mitigation Option 3;  T1-T4 in AM3.5
# # 4 - Mitigation Option 4;  T1-T4 in GLH-Test-01 (Composite mode)

# #data_0 = data[(data['Status'] ==  0)];                             del data_0['Status']
data_D = data[(data['Hour'] >=  7) & (data['Hour'] <  19)]
data_E = data[(data['Hour'] >= 19) & (data['Hour'] <  23)]
data_N = data[(data['Hour'] <   7) | (data['Hour'] >= 23)]

if G_DEBUG:
    print 'Count-All:{0:6n}'.format(len(data))
    print 'Count-D  :{0:6n}'.format(len(data_D))
    print 'Count-E  :{0:6n}'.format(len(data_E))
    print 'Count-N  :{0:6n}'.format(len(data_N))

# data_0 = data[(data['Status'] == 16) | (data['Status'] ==  17)]
# #del data_0['Status']


#%% Now divide data up into individual groupings

#0 - All baseline - no division required
data_1   =   data[  data['Status'] ==  1]
data_1_D = data_D[data_D['Status'] ==  1]
data_1_E = data_E[data_E['Status'] ==  1]
data_1_N = data_N[data_N['Status'] ==  1]
startDay_1 = dt.datetime(data_1.index.min().year,data_1.index.min().month,data_1.index.min().day).strftime('%d/%m/%Y')
stopDay_1  = dt.datetime(data_1.index.max().year,data_1.index.max().month,data_1.index.max().day).strftime('%d/%m/%Y')

#1 - NM5 - spearate curtailment active (1) from not active (0) or stopped (2)
data_2   =   data[  data['Status'] ==  9]
data_2_D = data_D[data_D['Status'] ==  9]
data_2_E = data_E[data_E['Status'] ==  9]
data_2_N = data_N[data_N['Status'] ==  9]
startDay_2 = dt.datetime(data_2.index.min().year,data_2.index.min().month,data_2.index.min().day).strftime('%d/%m/%Y')
stopDay_2  = dt.datetime(data_2.index.max().year,data_2.index.max().month,data_2.index.max().day).strftime('%d/%m/%Y')

if G_DEBUG:
    print 'S1: Count-All:{0:6n}'.format(len(data_1))
    print 'S1: Count-D  :{0:6n}'.format(len(data_1_D))
    print 'S1: Count-E  :{0:6n}'.format(len(data_1_E))
    print 'S1: Count-N  :{0:6n}'.format(len(data_1_N))
    print '{0:s} - {1:s}'.format(startDay_1, stopDay_1)

if G_DEBUG:
    print 'S2: Count-All:{0:6n}'.format(len(data_2))
    print 'S2: Count-D  :{0:6n}'.format(len(data_2_D))
    print 'S2: Count-E  :{0:6n}'.format(len(data_2_E))
    print 'S2: Count-N  :{0:6n}'.format(len(data_2_N))
    print '{0:s} - {1:s}'.format(startDay_2, stopDay_2)

# ##2 - AM2 - Separate into T1-T4 in AM2 (_2_C_A) and T1-T2 in Am2 and T3-T4 disabled (_2_C_P)
# #data_2_C_A  = data_2[(data_2['T1-Curtail'] ==  1) & (data_2['T2-Curtail'] ==  1) & (data_2['T3-Curtail'] ==  1) & (data_2['T4-Curtail'] ==  1)]
# #data_2_C_P  = data_2[(data_2['T1-Curtail'] ==  1) & (data_2['T2-Curtail'] ==  1) & (data_2['T3-Curtail'] ==  2) & (data_2['T4-Curtail'] ==  2)]
# #
# ##3 - AM3.5 - Separate into T1-T4 in AM3.5 (_3_C_A) and T1-T2 in Am2 and T3-T4 disabled (_3_C_P)
# #data_3_C_A  = data_3[(data_3['T3-Power'] >=  0) & (data_3['T4-Power'] >= 0)]
# #data_3_C_P  = data_3[(data_3['T3-Power'] <   0) & (data_3['T4-Power'] <  0)]

# #data_0_Off = data_0[(data_0['T1-Power'] >=   0) & (data_0['T2-Power'] >=  0) & (data_0['T3-Power'] >=   0) & (data_0['T4-Power'] >=  0)])
# #data_0_On  =
# #data_0_T3  =

# #4 - All GLH-Test-01 - no division required


#%% Generate wind roses using unfiltered data for each period

# Create some polar plots of wind speed and direction
# polar_plot(data_1,   "Wind Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - D/E/N", 3, 12, G_RANGE, inputFile[:-5], 0, 0)
# polar_plot(data_1_D, "Wind Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - D",     3, 12, G_RANGE, inputFile[:-5], 1, 0)
# polar_plot(data_1_E, "Wind Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - E",     3, 12, G_RANGE, inputFile[:-5], 2, 0)
# polar_plot(data_1_N, "Wind Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - N",     3, 12, G_RANGE, inputFile[:-5], 3, 0)

polar_plot(data_2,   "Wind Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - D/E/N", 3, 12, G_RANGE, inputFile[:-5], 90, 0)
polar_plot(data_2_D, "Wind Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - D",     3, 12, G_RANGE, inputFile[:-5], 91, 0)
polar_plot(data_2_E, "Wind Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - E",     3, 12, G_RANGE, inputFile[:-5], 92, 0)
polar_plot(data_2_N, "Wind Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - N",     3, 12, G_RANGE, inputFile[:-5], 93, 0)

# #%% Filter data to remove periods with no AM

# # IGNORE THIS SECTION - BIASES RESULTS

# #print "\nFILTERED DATA\nBefore\tAfter\t% Remain"
#data, data_cnt = filterData(data)
#data_1, data_1_cnt = filterData(data_1)
#data_2, data_2_cnt = filterData(data_2)
# #data_4, data_4_cnt = filterData(data_4)
# #data_5, data_5_cnt = filterData(data_5)


# #%% Now do all necessary analysis and plotting

# Create some polar plots of AM by wind speed and direciton
# polar_plot(data_1,   "AM Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - D/E/N", 3, 12, G_RANGE, inputFile[:-5],  0, 1)
# polar_plot(data_1_D, "AM Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - D",     3, 12, G_RANGE, inputFile[:-5],  1, 1)
# polar_plot(data_1_E, "AM Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - E",     3, 12, G_RANGE, inputFile[:-5],  2, 1)
# polar_plot(data_1_N, "AM Polar Plot: " + startDay_1 + "-" + stopDay_1 + " - 42 dB(A) Lden Limit - N",     3, 12, G_RANGE, inputFile[:-5],  3, 1)

polar_plot(data_2,   "AM Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - D/E/N", 3, 12, G_RANGE, inputFile[:-5],  90, 1)
polar_plot(data_2_D, "AM Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - D",     3, 12, G_RANGE, inputFile[:-5],  91, 1)
polar_plot(data_2_E, "AM Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New AM Mode 2 - E",     3, 12, G_RANGE, inputFile[:-5],  92, 1)
polar_plot(data_2_N, "AM Polar Plot: " + startDay_2 + "-" + stopDay_2 + " - 42 dB(A) Lden Limit + New Am Mode 2 - N",     3, 12, G_RANGE, inputFile[:-5],  93, 1)

# #%% Now do some average plots

# #import warnings
# #warnings.simplefilter('ignore', np.RankWarning)

# plt.figure()
# plt.axis([0, 16, 0, 10])        
# plt.plot(data[data.columns[0]], data[data.columns[52]],'r.', alpha=0.3, label ='D/E/N')
# plt.plot(data_1[data_1.columns[0]], data_1[data_1.columns[52]],'b.', alpha=0.3, label ='D')
# plt.plot(data_2[data_2.columns[0]], data_2[data_2.columns[52]],'g.', alpha=0.3, label ='E')
# plt.plot(data_3[data_3.columns[0]], data_3[data_3.columns[52]],'k.', alpha=0.3, label ='N')
# #plt.plot(data_3[data_3.columns[0]], data_3[data_3.columns[6]],'m.', alpha=0.3, label ='AM3.5 All')
# #plt.plot(data_4[data_4.columns[0]], data_4[data_4.columns[6]],'y.', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Wind Speed / (m/s)')
# plt.ylabel('Modulation Depth (AM) / dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.axvspan(3, 12, facecolor='g', alpha=0.2, label = 'Curtailment Range')
# #poly_plot(data_0[data_0.columns[0]], data_0[data_0.columns[6]], 2, 'r')
# #poly_plot(data_1[data_1.columns[0]], data_1[data_1.columns[6]], 2, 'b')
# #poly_plot(data_2[data_2.columns[0]], data_2[data_2.columns[6]], 2, 'g')
# #poly_plot(data_3[data_3.columns[0]], data_3[data_3.columns[6]], 2, 'm')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM as Function of Wind Speed')
# plt.tight_layout()
# if G_RANGE == 1:
#    surveyFigName = inputFile[:-5] + "_050_Scatter.png"
# elif G_RANGE == 2:
#    surveyFigName = inputFile[:-5] + "_100_Scatter.png"
# elif G_RANGE == 3:        
#    surveyFigName = inputFile[:-5] + "_200_Scatter.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#      orientation='landscape', papertype='a3', format='png',
#      transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
# #

# ##%% Create some boxplots for each mitigation option

# #bd0         = box_plot(data_0, G_RANGE, inputFile[:-5], 0); bd0_x,bd0_y = box_extract(bd0)
# #bd1         = box_plot(data_1_C, G_RANGE, inputFile[:-5], 1); bd1_x,bd1_y = box_extract(bd1)
# #bd2         = box_plot(data_2_C_P, G_RANGE, inputFile[:-5], 2); bd2_x,bd2_y = box_extract(bd2)
# #bd3         = box_plot(data_3_C_P, G_RANGE, inputFile[:-5], 3); bd3_x,bd3_y = box_extract(bd3)
# ##bd2         = box_plot(data_2_C_A, G_RANGE, inputFile[:-5], 2); bd2_x,bd2_y = box_extract(bd2)
# ##bd3         = box_plot(data_3_C_A, G_RANGE, inputFile[:-5], 3); bd3_x,bd3_y = box_extract(bd3)
# #
# #plt.figure()
# #plt.plot(bd0_x,bd0_y,'r-', label = 'Baseline')
# #plt.plot(bd1_x,bd1_y,'b-', label = 'NM5')
# #plt.plot(bd2_x,bd2_y,'g-', label = 'AM2')
# #plt.plot(bd3_x,bd3_y,'m-', label = 'AM3.5')
# #plt.xlabel('Wind Speed / (m/s)')
# #plt.ylabel('Modulation Depth (AM) / dB') 
# #plt.grid('on',which=u'major', axis=u'both')
# #plt.axvspan(2, 10, facecolor='g', alpha=0.2, label = 'Curtailment Range')
# #plt.legend(loc='best')
# #plt.title('Comparison of Average Levels of AM by Wind Speed')
# #plt.tight_layout()
# #if G_RANGE == 1:
# #    surveyFigName = inputFile[:-5] + "_050_Means-P.png"
# ##    surveyFigName = inputFile[:-5] + "_050_Means-A.png"
# #elif G_RANGE == 2:
# #    surveyFigName = inputFile[:-5] + "_100_Means-A.png"
# #elif G_RANGE == 3:        
# #    surveyFigName = inputFile[:-5] + "_200_Means-A.png"
# #surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# #plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
# #      orientation='landscape', papertype='a3', format='png',
# #      transparent=False, frameon=None)
# #plt.clf() # Clear figure of data for re-use
# #
# #
# #%% Now do some frequency distributions

# #plt.figure()
# #hist_data = [data_0[data_0.columns[6]],
# #             data_1[data_1.columns[6]],
# #             data_2[data_2.columns[6]],
# #             data_3[data_3.columns[6]],
# #             data_4[data_3.columns[6]]]
# ##hist_data = [data_0[data_0.columns[6]],
# ##             data_1_C[data_1_C.columns[6]],
# ##             data_2_C_A[data_2_C_A.columns[6]],
# ##             data_3_C_A[data_3.columns[6]]]
# #bins = np.linspace(0,10,11)
# #if G_CUMUL:       
# #    if G_NORM:
# #        plt.hist(hist_data, bins, range = (0,10), normed = True, cumulative=True, alpha = 0.5, color = ['r','b','g','m','y'], 
# #                 label =['Baseline', 'NM5 Only', 'AM2 T1-T4','AM3.5 T1-T4','GLH-Test-01'])
# #        plt.ylabel('Cumulative Frequency') 
# #    else:
# #        plt.hist(hist_data, bins, range = (0,10), cumulative=True, alpha = 0.5, color = ['r','b','g','m','y'], 
# #                 label =['Baseline', 'NM5 Only', 'AM2 T1-T4','AM3.5 T1-T4','GLH-Test-01'])
# #        
# #        plt.ylabel('Cumulative Items') 
# #else:
# #    if G_NORM:
# #        plt.hist(hist_data, bins, range = (0,10), normed = True, alpha = 0.5, color = ['r','b','g','m','y'], 
# #                 label =['Baseline', 'NM5 Only', 'AM2 T1-T4','AM3.5 T1-T4','GLH-Test-01'])
# #        plt.ylabel('Relative Frequency')
# #    else:
# #        plt.hist(hist_data, bins, range = (0,10), alpha = 0.5, color = ['r','b','g','m','y'], 
# #                 label =['Baseline', 'NM5 Only', 'AM2 T1-T4','AM3.5 T1-T4','GLH-Test-01'])
# #        plt.ylabel('No. of Items')
# #xticks = range(0,11,1)
# #plt.xticks(xticks, xticks)
# #plt.legend(loc='best')
# #plt.grid('on',which=u'major', axis=u'both')
# #plt.xlabel('Modulation Depth (AM) / dB')
# #plt.title('Comparison of AM Frequency Distributions')
# #plt.tight_layout()
# #if G_RANGE == 1:
# #    surveyFigName = inputFile[:-5] + "_050_Distros.png"
# #elif G_RANGE == 2:
# #    surveyFigName = inputFile[:-5] + "_100_Distros.png"
# #elif G_RANGE == 3:        
# #    surveyFigName = inputFile[:-5] + "_200_Distros.png"
# #surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# #plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
# #      orientation='landscape', papertype='a3', format='png',
# #      transparent=False, frameon=None)
# #plt.clf()

# data_bin   = data_binning(data)       # Baseline D/E/N
# data_1_bin = data_binning(data_1)     # Baseline D/E
# data_2_bin = data_binning(data_2)     # Baseline N
# print data_bin.columns
# print data_1_bin.column
# print data_2_bin.column

# #data_3_bin     = data_binning(data_3)     # AM3.5
# #data_3_C_A_bin = data_binning(data_3_C_A) # AM3.5
# #data_3_C_P_bin = data_binning(data_3_C_P) # AM3.5
# #data_4_bin     = data_binning(data_4)     # GLH-Test-01
# #
# plt.figure()
# plt.axis([0, 20, 0, 0.6])        
# plt.plot(  data_bin[  data_bin.columns[6]],   data_bin[  data_bin.columns[4]], 'r.-', alpha=0.3, label ='D/E/N')
# plt.plot(data_1_bin[data_1_bin.columns[6]], data_1_bin[data_1_bin.columns[4]], 'b.-', alpha=0.3, label ='D/E')
# plt.plot(data_2_bin[data_2_bin.columns[6]], data_2_bin[data_2_bin.columns[4]], 'g.-', alpha=0.3, label ='N')
# # #plt.plot(data_3_bin[data_3_bin.columns[6]], data_3_bin[data_3_bin.columns[4]], 'm.-', alpha=0.3, label ='AM3.5 All')
# # #plt.plot(data_4_bin[data_4_bin.columns[6]], data_4_bin[data_4_bin.columns[4]], 'y.-', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Hub Height Wind Speed / (m/s)')
# plt.ylabel('Relative Frequency of AM') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Relative Frequency of Occurence of AM')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_RelFreq.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_RelFreq.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_RelFreq.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use


# plt.figure()
# plt.axis([0, 20, 0, 0.6])        
# plt.plot(data_0_bin[data_0_bin.columns[6]], data_0_bin[data_0_bin.columns[4]], 'r.-', alpha=0.3, label ='Baseline')
# plt.plot(data_1_bin[data_1_bin.columns[6]], data_1_bin[data_1_bin.columns[4]], 'b.-', alpha=0.3, label ='NM5 All')
# plt.plot(data_2_bin[data_2_bin.columns[6]], data_2_bin[data_2_bin.columns[4]], 'g.-', alpha=0.3, label ='AM2 All')
# plt.plot(data_3_C_A_bin[data_3_C_A_bin.columns[6]], data_3_C_A_bin[data_3_C_A_bin.columns[4]], 'c.-', alpha=0.3, label ='AM3.5 T3-T4 On')
# plt.plot(data_3_C_P_bin[data_3_C_P_bin.columns[6]], data_3_C_P_bin[data_3_C_P_bin.columns[4]], 'm.-', alpha=0.3, label ='AM3.5 T3-T4 Off')
# plt.plot(data_4_bin[data_4_bin.columns[6]], data_4_bin[data_4_bin.columns[4]], 'y.-', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Standardised Wind Speed at 10 m Height / (m/s)')
# plt.ylabel('Relative Frequency of AM') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Relative Frequency of Occurence of AM')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_RelFreq_D.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_RelFreq_D.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_RelFreq_D.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
#
#
# plt.figure()
# plt.axis([0, 14, 0, 2])        
# plt.plot(data_0_bin[data_0_bin.columns[6]], data_0_bin[data_0_bin.columns[5]] ,'r.-', alpha=0.3, label ='Baseline')
# plt.plot(data_1_bin[data_1_bin.columns[6]], data_1_bin[data_1_bin.columns[5]], 'b.-', alpha=0.3, label ='NM5 All')
# plt.plot(data_2_bin[data_2_bin.columns[6]], data_2_bin[data_2_bin.columns[5]], 'g.-', alpha=0.3, label ='AM2 All')
# plt.plot(data_3_bin[data_3_bin.columns[6]], data_3_bin[data_3_bin.columns[5]], 'm.-', alpha=0.3, label ='AM3.5 All')
# plt.plot(data_4_bin[data_4_bin.columns[6]], data_4_bin[data_4_bin.columns[5]], 'y.-', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Standardised Wind Speed at 10 m Height / (m/s)')
# plt.ylabel('Average Level of AM Over All Periods/dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM Over Entire Periods')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_AvAM_1.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_AvAM_1.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_AvAM_1.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#      orientation='landscape', papertype='a3', format='png',
#      transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
#
#
# plt.figure()
# plt.axis([0, 14, 0, 2])        
# plt.plot(data_0_bin[data_0_bin.columns[6]], data_0_bin[data_0_bin.columns[5]] ,'r.-', alpha=0.3, label ='Baseline')
# plt.plot(data_1_bin[data_1_bin.columns[6]], data_1_bin[data_1_bin.columns[5]], 'b.-', alpha=0.3, label ='NM5 All')
# plt.plot(data_2_bin[data_2_bin.columns[6]], data_2_bin[data_2_bin.columns[5]], 'g.-', alpha=0.3, label ='AM2 All')
# plt.plot(data_3_C_A_bin[data_3_C_A_bin.columns[6]], data_3_C_A_bin[data_3_C_A_bin.columns[5]], 'c.-', alpha=0.3, label ='AM3.5 T3-T4 On')
# plt.plot(data_3_C_P_bin[data_3_C_P_bin.columns[6]], data_3_C_P_bin[data_3_C_P_bin.columns[5]], 'm.-', alpha=0.3, label ='AM3.5 T3-T4 Off')
# plt.plot(data_4_bin[data_4_bin.columns[6]], data_4_bin[data_4_bin.columns[5]], 'y.-', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Standardised Wind Speed at 10 m Height / (m/s)')
# plt.ylabel('Average Level of AM Over All Periods/dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM Over Entire Periods')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_AvAM_1_D.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_AvAM_1_D.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_AvAM_1_D.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
#
#
# plt.figure()
# plt.axis([0, 14, 1, 5])        
# plt.plot(data_0_bin[data_0_bin.columns[6]], data_0_bin[data_0_bin.columns[3]] ,'r.-', alpha=0.3, label ='Baseline')
# plt.plot(data_1_bin[data_1_bin.columns[6]], data_1_bin[data_1_bin.columns[3]], 'b.-', alpha=0.3, label ='NM5 All')
# plt.plot(data_2_bin[data_2_bin.columns[6]], data_2_bin[data_2_bin.columns[3]], 'g.-', alpha=0.3, label ='AM2 All')
# plt.plot(data_3_bin[data_3_bin.columns[6]], data_3_bin[data_3_bin.columns[3]], 'm.-', alpha=0.3, label ='AM3.5 All')
# plt.plot(data_4_bin[data_4_bin.columns[6]], data_4_bin[data_4_bin.columns[3]], 'y.-', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Standardised Wind Speed at 10 m Height / (m/s)')
# plt.ylabel('Average Level of AM When Present/dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM Over AM Periods')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_AvAM_2.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_AvAM_2.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_AvAM_2.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
#
# plt.figure()
# plt.axis([0, 14, 1, 5])
# plt.plot(data_0_bin[data_0_bin.columns[6]], data_0_bin[data_0_bin.columns[3]] ,'r.-', alpha=0.3, label ='Baseline')
# plt.plot(data_1_bin[data_1_bin.columns[6]], data_1_bin[data_1_bin.columns[3]], 'b.-', alpha=0.3, label ='NM5 All')
# plt.plot(data_2_bin[data_2_bin.columns[6]], data_2_bin[data_2_bin.columns[3]], 'g.-', alpha=0.3, label ='AM2 All')
# plt.plot(data_3_C_A_bin[data_3_C_A_bin.columns[6]], data_3_C_A_bin[data_3_C_A_bin.columns[3]], 'c.-', alpha=0.3, label ='AM3.5 T3-T4 On')
# plt.plot(data_3_C_P_bin[data_3_C_P_bin.columns[6]], data_3_C_P_bin[data_3_C_P_bin.columns[3]], 'm.-', alpha=0.3, label ='AM3.5 T3-T4 Off')
# plt.plot(data_4_bin[data_4_bin.columns[6]], data_4_bin[data_4_bin.columns[3]], 'y.-', alpha=0.3, label ='GLH-Test-01')
# plt.xlabel('Standardised Wind Speed at 10 m Height / (m/s)')
# plt.ylabel('Average Level of AM When Present/dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM Over AM Periods')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_AvAM_2_D.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_AvAM_2_D.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_AvAM_2_D.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use


#%%Determine AM bin
# data_0['WSBin'] = data_0[data_0.columns[0]].apply(lambda x: int(x//1))
# data_0['WSBin'] = data_0[data_0.columns[0]].apply(lambda x: round(x))
# df.column1 = df.column1.fillna('')
# ss = pd.pivot_table(data_0, values='Noise', index =['Wind Speed'], aggfunc=[len, np.mean], margins=True)
# qq = pd.pivot_table(data_0, values='AM(50-200Hz)/dB', index =['Wind Speed'], aggfunc=[len, np.mean], margins=True)

# Cutailed Only - All Turbines
# plt.figure()
# hist_data = [data_0[data_0.columns[6]],
#              data_1_C[data_1_C.columns[6]],
#              data_2_C_P[data_2_C_A.columns[6]],
#              data_3_C_P[data_3.columns[6]]]
# bins = np.linspace(0,10,11)
# if G_CUMUL:       
#     if G_NORM:
#         plt.hist(hist_data, bins, range = (0,10), normed = True, cumulative=True, alpha = 0.5, color = ['r','b','g','m'], 
#                  label =['Baseline', 'NM5 Only', 'AM2 T1-T2','AM3.5 T1-T2'])
#         plt.ylabel('Cumulative Frequency') 
#     else:
#         plt.hist(hist_data, bins, range = (0,10), cumulative=True, alpha = 0.5, color = ['r','b','g','m'], 
#                  label =['Baseline', 'NM5 Only', 'AM2 T1-T2','AM3.5 T1-T2'])
#        
#         plt.ylabel('Cumulative Items') 
# else:
#     if G_NORM:
#         plt.hist(hist_data, bins, range = (0,10), normed = True, alpha = 0.5, color = ['r','b','g','m'], 
#                  label =['Baseline', 'NM5 Only', 'AM2 T1-T2','AM3.5 T1-T2'])
#         plt.ylabel('Relative Frequency')
#     else:
#         plt.hist(hist_data, bins, range = (0,10), alpha = 0.5, color = ['r','b','g','m'], 
#                  label =['Baseline', 'NM5 Only', 'AM2 T1-T2','AM3.5 T1-T2'])
#         plt.ylabel('No. of Items')
# xticks = range(0,11,1)
# plt.xticks(xticks, xticks)
# plt.legend(loc='best')
# plt.grid('on',which=u'major', axis=u'both')
# plt.xlabel('Modulation Depth (AM) / dB')
# plt.title('Comparison of AM Frequency Distributions')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_Distros-P.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_Distros_P.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_Distros_P.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf()


# #%% Now do some time of day plots - counts
# #
# hourlyAM   = data.groupby('Hour').agg({data.columns[52]: [np.size, np.mean, np.std]})
# #hourlyAM   = data.groupby('Hour').agg({data.columns[52]: [count, np.mean, np.std]})
# print hourlyAM
# hourlyAM_1 = data_1.groupby('Hour').agg({data_1.columns[52]: [np.size, np.mean, np.std]})
# hourlyAM_2 = data_2.groupby('Hour').agg({data_2.columns[52]: [np.size, np.mean, np.std]})
# hourlyAM_4 = data_4.groupby('Hour').agg({data_4.columns[2]: [np.size, np.mean, np.std]})
# #hourlyAM_5 = data_5.groupby('Hour').agg({data_5.columns[2]: [np.size, np.mean, np.std]})
#
# # Normalise for entire period into %
# hourlyAM_0[data_0.columns[2]]['size'] = 100* hourlyAM_0[data_0.columns[2]]['size'] / data_0_cnt
# hourlyAM_1[data_1.columns[2]]['size'] = 100* hourlyAM_1[data_1.columns[2]]['size'] / data_1_cnt
# hourlyAM_3[data_3.columns[2]]['size'] = 100* hourlyAM_3[data_3.columns[2]]['size'] / data_3_cnt
# hourlyAM_4[data_4.columns[2]]['size'] = 100* hourlyAM_4[data_4.columns[2]]['size'] / data_4_cnt
#
#
# #%% 
# 
# bar_width = 0.2
# plt.figure()
# plt.bar(hourlyAM_0.index, hourlyAM_0[data_0.columns[2]]['size'], bar_width, color = 'r', label ='Baseline')
# plt.bar(hourlyAM_1.index + bar_width, hourlyAM_1[data_1.columns[2]]['size'], bar_width, color = 'b', label = 'Mitigation 1 (NM5)')
# plt.bar(hourlyAM_3.index + (2*bar_width), hourlyAM_3[data_3.columns[2]]['size'], bar_width, color = 'g', label = 'Mitigation 3 (AM)')
# plt.bar(hourlyAM_4.index + (3*bar_width), hourlyAM_4[data_4.columns[2]]['size'], bar_width, color = 'm', label = 'Mitigation 4 (off)')
# plt.xlabel('Hour of Day')
# plt.ylabel('% of 10 min items with AM')
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Frequency of AM by Time of Day')
# #plt.xticks(hourlyAM_0.index + bar_width / 2, hourlyAM_0.index, rotation = 'vertical')
# plt.xticks(hourlyAM_0.index + 0.3, hourlyAM_0.index, rotation = 'vertical')
# #plt.xticks(hourlyAM_0.index + bar_width / 2, hourlyAM_0.index, rotation = 45)
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_TOD_N.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_TOD_N.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_TOD_N.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
#
#
# #%% Now do some time of day plots - mean values
#
# plt.figure()
# plt.plot(hourlyAM_0.index, hourlyAM_0[data_0.columns[2]]['mean'], 'r-', label ='Baseline', linewidth=2)
# plt.plot(hourlyAM_1.index, hourlyAM_1[data_1.columns[2]]['mean'], 'b-', label ='Mitigation 1 (NM5)')
# plt.plot(hourlyAM_3.index, hourlyAM_3[data_3.columns[2]]['mean'], 'g-', label ='Mitigation 3 (AM)')
# plt.plot(hourlyAM_4.index, hourlyAM_4[data_4.columns[2]]['mean'], 'm-', label ='Mitigation 4 (Off)')
# plt.xlabel('Hour of Day')
# plt.ylabel('Average Modulation Depth (AM) / dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM by Time of Day')
# plt.tight_layout()
# if G_RANGE == 1:
#     surveyFigName = inputFile[:-5] + "_050_TOD_M.png"
# elif G_RANGE == 2:
#     surveyFigName = inputFile[:-5] + "_100_TOD_M.png"
# elif G_RANGE == 3:        
#     surveyFigName = inputFile[:-5] + "_200_TOD_M.png"
# surveyFigName = os.path.join(DIRECTORY_NAME, surveyFigName)
# plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
#       orientation='landscape', papertype='a3', format='png',
#       transparent=False, frameon=None)
# plt.clf() # Clear figure of data for re-use
#
# plt.figure()
# plt.plot(bd0_x,bd0_y,'r-', label = 'Baseline')
# plt.plot(bd1_x,bd1_y,'b-', label = 'Mit 1 - NM5')
# plt.plot(bd3_x,bd3_y,'g-', label = 'Mit 2 - AM')
# plt.plot(bd4_x,bd4_y,'m-', label = 'Mit 4 - Off')
# plt.xlabel('Wind Speed / (m/s)')
# plt.ylabel('Modulation Depth (AM) / dB') 
# plt.grid('on',which=u'major', axis=u'both')
# plt.axvspan(2, 10, facecolor='g', alpha=0.2, label = 'Curtailment Range')
# plt.legend(loc='best')
# plt.title('Comparison of Average Levels of AM by Wind Speed')