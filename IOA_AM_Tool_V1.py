#%% - User Notes

""" 
##Function:##
Program is designed to implement Method 3A - the 'Hybrid Hybrid' - 
recommended by the UK Institute of Acoustics Amplitude Modulation Working
Group, and originally proposed by Dave Coles of 24acoustics in Sep 2015.

##Background:##
  Based on method from following video:
  https://www.youtube.com/watch?v=jEYDBb3XkkY
  Also sample scripts provided by Dave Coles and Matthew Cand
  
##Assumptions:##
  Assume that input data are A-weighted sum of 100- 400 Hz acoustic data, as
  required by main methodology. In practice you should compare 50 - 200 and
  200 - 800 Hz ranges against 100 - 400 Hz and choose that range which leads to
  systemmatically highest values of AM. This can be done by running this code
  3 times with appropriate input data.

Author: J H Bass, RES Glasgow
Date:   24 November 2015
Version 1.002

    
###Version History:###
1.000   JHB   29/10/15   Initial version (non-Pandas)
1.001   JHB   20/11/15   Initial version (Pandas! Thank you FutureLearn)
1.002   JHB   24/11/15   More emphasis on storing results in Pandas dataframes
1.003   JHB   08/12/15   Further Work...
1.004   JHB   10/12/15   First version residing in Tortoise SVN. Implementing final stages
                         of the IOA AM WG analysis process
1.005   JHB   14/12/15   Save key variables in pickle files so that results can be easily re-analysed
                         Waterfall; AMminor, AMmajor???
1.006   JHB   05/01/16   Modified as follows:
                         * reduce run time by taking out repeated calculations: pull from minorAM into main code
                         * changes from last meeting re L95-L5 and additional lines for 3rd harmonic
                         * fix waterfall plot issues, i.e. put data into dB terms prior to plotting
1.007   JHB   11/03/16   Improve output format to more easily be read by other Python programs
1.008   JHB   13/04/16   Add better control of timestamp throughout code and stamp output appropriately
1.009   JHB   23/06/16   Fixed cosmetic bug in positions (Hz) of 2nd & 3rd harmonics
1.010   JHB   26/09/2016 Changed peak search method to be consistent with IOA software and added some
                         range checking for user defined max and min modulation frequencies.

Things to get implemented (profiling):
import matplotlib as mpl
mpl.rcParams['font.size'] = 15
mpl.rcParams['font.family'] = 'Century Gothic'
"""


#%% - Import all necessary modules

#from __future__ import division  # prevents integer division by default
print "INFORMATION: Importing modules...                          ",
import matplotlib.style
import matplotlib as mpl
mpl.style.use('classic')
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import tkFileDialog
import Tkinter
import numpy as np
import scipy.fftpack as fft
from scipy.signal import argrelmax
#from scipy import signal
import time
import matplotlib.pyplot as plt
import pandas as pd
import os
#import sys
print "...complete."


#%% - Initialise key variables

print "INFORMATION: Setting up global variables...                ",
#G_TEST                = True         # True-test code operative; False - test code ignored
G_TEST                = False        # True-test code operative; False - test code ignored
#G_DEBUG               = True         # True-verbose output; False - Minimal output
G_DEBUG               = False        # True-verbose output; False - Minimal output
G_DETREND             = True         # True-subtract trend; False-no detrending
#G_DETREND             = False        # True-subtract trend; False-no detrending
G_DETREND_ID          = 1            # 0 - Mean; 1 - 3rd Order Poly; 2 - 5th Order Poly
#G_LEGEND              = True        # True-show legend; False - don't show legend
G_LEGEND              = False        # True-show legend; False - don't show legend
G_CUMUL               = False        # True-cumulative distro; False-Probability density
#G_CUMUL               = True         # True-cumulative distro; False-Probability density
#G_FORMAT_ID           =   0          # 0 - 'Simple' format; 1 - 24acoustics format
G_FORMAT_ID           =   1          # 0 - 'Simple' format; 1 - 24acoustics format
#G_PEAK                =   0          # 0 - Av Pks - Av Trs; 1 - L95 - L5
#G_PEAK                =   1          # 0 - Av Pks - Av Trs; 1 - L95 - L5
#G_METHOD              =   0          # 0 - RES method for peaks in range; 1 - IOA 'correct' method
G_METHOD              =   1          # 0 - RES method for peaks in range; 1 - IOA 'correct' method
#G_PLOT                = True          # False - Don't plot 10 sec charts; True - plot 10 sec charts
#G_PLOT                = False         # False - Don't plot 10 sec charts; True - plot 10 sec charts
#G_PLOT                = 0            # 0 - No plot at all
G_PLOT                = 1            # 1 - Plot only survey (daily) results
#G_PLOT                = 2            # 2 - Plot survey (daily) results & 10 min results
#G_PLOT                = 3            # 3 - Plot survey (daily) results, 10 min & 10 sec results

#G_SURVEY              = True         # False - Dont plot key times; True - plot key times on survey chart
G_SURVEY              = False        # False - Dont plot key times; True - plot key times on survey chart
G_MAP                 =   0          # 0-Jet; 1-Viridis; 2-afmhot; 3 - Reds (bad)
#G_MAP                 =   1          # 0-Jet; 1-Viridis; 2-afmhot; 3 - Reds (bad)
#G_MAP                 =   2          # 0-Jet; 1-Viridis; 2-afmhot; 3 - Reds (bad)
#G_MAP                 =   3          # 0-Jet; 1-Viridis; 2-afmhot; 3 - Reds (bad)
SAMPLE_FREQ           =  10          # Sample rate in Hz (10 Hz is 100 ms data)
MINOR_INTERVAL        =  10          # Length of data chunks for analysis (in seconds)
MAJOR_INTERVAL        = 600          # Length of data chunk for overall analysis (in seconds)
MAJOR_INTERVAL_COUNTS =  30          # Number of valid periods required in major intervals (30 pref)
PROMINENCE_RATIO      =   4          # Prominence ratio check value from IOA AM WG
HARMONICS_P2P_LIMIT   = 1.5          # Harmonics peak to peak check value from IOA AM WG

# USE THIS AREA TO STORE ROTATIONAL SPEEDS FOR DIFFERNT ANALYSES
# Roos         -
# Tallentire   -
# Woolley Hill - 
# Den Brook    - Vestas V90 2MW runs from 9.6 - 17.0 rpm, which equates to 0.48 - 0.85 Hz (0.4 - 0.9)
# Vardafjellet-Vestas V117 4 MW runs from 6.7 - 17.5 rpm, which equates to 0.33 - 0.88 Hz (0.3 - 0.9)

MIN_MOD_FREQ          = 0.3          # Constrain range for finding peak (lower)
MAX_MOD_FREQ          = 0.9          # Cconstrain range for finding peak (upper)
BLOCK_SIZE      = MINOR_INTERVAL*SAMPLE_FREQ  # No of samples in a minor interval (block)
CHUNK_SIZE      = MAJOR_INTERVAL*SAMPLE_FREQ  # No of samples in a major interval (chunk)
SAMPLE_INTERVAL = 1.0/SAMPLE_FREQ             # Time (sec) between samples
FREQ_RESOLUTION = 1.0/MINOR_INTERVAL          # Frequency resolution of PSD (in Hz)
START_TIME      = "2021-02-17"       # Start time used for Pandas dataframes where no time exists

# Range checks on MIN & MAX_MOD_FREQ
if MIN_MOD_FREQ < 0.3:
    raise ValueError('Invalid minimum modulation frequency - should be >= 0.3 Hz')
if MAX_MOD_FREQ > 1.6:
    raise ValueError('Invalid maximum modulation frequency - should be <= 1.6 Hz')
if MAX_MOD_FREQ <= MIN_MOD_FREQ:
    raise ValueError('Maximum modulation frequency must be greater than minimum')

print "...complete."


#%% - Allow user to select file to process
def getFile(userMessage, userDir, userFileType, allowMultiple=False, debug = True):    
    root = Tkinter.Tk() # Set the Tkinter root
    root.withdraw() # this stops a small window popping up

    # This line opens the file open dialog
    full_path = tkFileDialog.askopenfilename(parent=root, title= userMessage, defaultextension = userFileType,
                                             initialdir = userDir, multiple=allowMultiple,
                                             filetypes=[('CSV files','*.csv'),('Text files','*.txt'), ('All files','*.*')])
    # If allowMultiple is true response is a tuple, otherwise a string
    
    if full_path: # full-path contains at least one filename
        if allowMultiple:
            totalFiles    = len(full_path)
            pathName      = []
            fileName      = []
            fileExtension = []
            for file in range(totalFiles):
                dummy, dummyX = os.path.split(full_path[file]); pathName.append(dummy)
                dummy, dummyX = os.path.splitext(dummyX);       fileName.append(dummy)
                fileExtension.append(dummyX[1:])
        else:
            totalFiles = 1
            pathName, fileName       = os.path.split(full_path)
            fileName, fileExtension  = os.path.splitext(fileName)
            fileExtension            = fileExtension[1:]
    else:         # full_path doesn't contain any filenames because user pressed cancel
        totalFiles = 0
        pathName      = None
        fileName      = None
        fileExtension = None

    if debug: # Prints out list of selected files, for debugging purposes
        print totalFiles
        print pathName
        print fileName
        print fileExtension
        if totalFiles > 0:
            for fItem in range(totalFiles):
                print 'File: %d' % fItem,
                print       '%s' %      pathName[fItem],
                print      '/%s' %      fileName[fItem],
                print      '.%s' % fileExtension[fItem]
    
    # Return key information to main programme
    return totalFiles, pathName, fileName, fileExtension    


#%% - Function to determine position of fundamental

def fundamentalLocation(powerSpectrum, frequency):  
    iMax, = np.where(powerSpectrum == max(powerSpectrum[(frequency >= MIN_MOD_FREQ) & (frequency <= MAX_MOD_FREQ)]))
    firstHarmonicLocation = iMax[0]
    return firstHarmonicLocation


#%% - Function to determine position of subsequent harmonics

def harmonicLocation(powerSpectrum, frequency, hFreq, lines):
    delta_freq = lines*FREQ_RESOLUTION
    iMax, = np.where(powerSpectrum == max(powerSpectrum[(frequency >= (hFreq - delta_freq)) & (frequency <= (hFreq + delta_freq))]))
    harmonicLocation = iMax[0]
    return harmonicLocation


#%% - Function to determine whether an individual harmonic (1 to 3) should be included in analysis

def testHarmonic(FFTData, freq, frqPos, testValue, debug = True):
    
    # Test if fundamental or harmonic is to be included
    if frqPos <> None:    
        FFT_cut = np.zeros_like(FFTData)
          
        # For inverse transforms, we must include indices around a peak
        #indexRange = [-1, 0, 1]  # these are the indices around the peak
        # Now get the absolute indices around the peak, checking they're valid
        #ind_freq   = [frqPos + x for x in indexRange if (frqPos + x >= 0) and
        #                                                (frqPos + x < len(psd))]       
        ind_freq = [frqPos-1, frqPos, frqPos+1]
        FFT_cut[ freq[ind_freq]] = FFTData[ freq[ind_freq]] # first put the positive frequencies in
        FFT_cut[-freq[ind_freq]] = FFTData[-freq[ind_freq]] # next put the negative frequencies in (FFT gives pos and neg freqs)
    
        # Create time series of harmonic only and identify the min/max        
        fft_cut  = np.real(fft.ifft(FFT_cut)) # this is the inverse FFT calculation for the fundamental/harmonic alone
        #range_fft_cut = np.max(fft_cut.real) - np.min(fft_cut.real)
        range_fft_cut = np.max(fft_cut) - np.min(fft_cut)
        if range_fft_cut > testValue:
            includeHarmonic = True
        else:
            includeHarmonic = False
            
        # Print out key results, if required
        if debug:
            print frqPos      
            #print len(fft_cut), fft_cut.real
            print len(fft_cut), fft_cut
            print np.min(fft_cut), np.max(fft_cut), range_fft_cut
            #print np.min(fft_cut.real), np.max(fft_cut.real), range_fft_cut
    
        #return includeHarmonic, fft_cut
        return includeHarmonic
    else:
        return False


#%% - Function to determine level of AM within a minor intervals, eg 10 sec

def minorAM(testData, debug = True, detrend = False):
    """ 
    ##Function:###
    Function 'fitGoodness' is designed to take in two frequency distributions

    ##Background:###
    This method comes from a paper called 'Copula Graphical Models for Wind 
    Resource Estimation' circulated in Slack by JHB on 21 July 2015. The KL
    divergence method itself is a measure of the divergence, or difference, or
    distance between two distributions and the lower this value, the more
    similar the two distributions are. Note that:
    - this metric is identical to the objective function you minimise when
      using the 'maximum likeness method of fitting parameters to a distribution
    - see: http://ecm1/livelink/llisapi.dll/properties/5991360
    - the 'maximum likeness' method is equivalent to the 'maximum likelihood'
      method for the same data in time series, rather than frequency
      distribution form.

    ##Inputs:###
    - testData: an array containing 50 integer or floating point

    ###Outputs:###
    - indexAM: the function returns, through the function name:

    Author: J H Bass, RES Glasgow
    Date:   29 September 2015
    Version 1.000   
        
    ###Version History:###
    1.000   JHB   29/09/15   Initial version
    """

    # Replace any no-entry values, i.e. -99 with 'nan'
    testData = np.array(testData)
    testData[testData <= -99] = float('NaN')
    
    # Check that testData has enough data to process
    print testData           
    if len(testData[~np.isnan(testData)]) == BLOCK_SIZE: # number of points in array
    #if len(testData) == BLOCK_SIZE: # number of points in array
                
        # Fit 3rd order polynomial and detrend data
        if detrend:
            if G_DETREND_ID == 0: # Detrend by mean
                trendLine   = np.average(testData)
            elif G_DETREND_ID == 1: # Detrend by 3rd order polynomial
                polyVals    = np.polyfit(t, testData, 3) # get linear fit to give good starting point for slope
                trendLine   = np.polyval(polyVals,t)
            elif G_DETREND_ID == 2: # Detrend by 5th order polynomial
                polyVals    = np.polyfit(t, testData, 5) # get linear fit to give good starting point for slope
                trendLine   = np.polyval(polyVals,t)
            deTrendData     = testData - trendLine
   
        # Now calculate FFT of data with SAMPLE_FREQ resolution over 'minorInterval' seconds
        # Note: need both real and imaginary parts, both postive and negative frequencies
        #ind_freq = np.arange(1, BLOCK_SIZE/2)
        ind_freq = np.arange(0, (BLOCK_SIZE/2) + 1) 
        freqs = fft.fftfreq(BLOCK_SIZE, SAMPLE_INTERVAL)
        psd_freqs = abs(freqs[ind_freq])
        
        if detrend:        
            Hn = fft.fft(deTrendData) # This is the FFT calculation
        else:
            Hn = fft.fft(testData)    # This is the FFT calculation
    
        # Calculate the Power Spectrum (Density)
        psd       = abs(Hn[ind_freq])**2 + abs(Hn[-ind_freq])**2
        #psd       = float(2) * psd / BLOCK_SIZE**2 # Normalise according to IOA AM WG
        psd       = psd / BLOCK_SIZE**2 # Normalise according to IOA AM WG - corrected 21 Sep 2016
                
        # Now deterine location of first three harmonics
        iMax1     = fundamentalLocation(psd, psd_freqs)  # Find first harmonic (fundamental)
        maxFreq1  = psd_freqs[iMax1]
        peakValue = psd[iMax1]
        continuum = np.average(psd[[iMax1-3, iMax1-2, iMax1+2, iMax1+3]])
        #Check prominence ratio is less than PROMINENCE_RATIO
        
        if G_DEBUG:        
            print '{:3d} Prominence ratio= {:.2f}'.format(minorInterval, peakValue/continuum), 
        
        if peakValue/continuum >= PROMINENCE_RATIO: # Promince ratio exceeded - accept 10 sec period as valid
            #print "Data good: %2d  Pk Posn= %2d   PV= %5.2f   CL= %5.2f" % (minorInterval, iMax1, peakValue, continuum)
            goodData = True
            waterfall.append(2*np.sqrt(2*FREQ_RESOLUTION*psd))  # Add current psd to waterfall
            #waterfall.append(psd)                   # Add current psd to waterfall
        else:                                       # Prominance ratio insufficient - reject 10 sec as invalid
            #print "Data BAD!: %2d  Pk Posn= %2d   PV= %5.2f   CL= %5.2f" % (minorInterval, iMax1, peakValue, continuum)
            goodData = False
            dummy_psd = np.zeros_like(psd)          # Create an empty psd
            waterfall.append(dummy_psd)             # Add dummy data to waterfall
		
        ## Create minorInterval charting
        if G_PLOT == 3:
            plt.figure(1, figsize=(16, 12)) # Has 4 subplots - time series of LHS; FDs on RHS
            
            #SUBPLOT #1
            plt.subplot(2,2,1) # Plot Time series in TLHS
            plt.tight_layout()
            plt.plot(t, testData,  'g-', label = 'Raw data')
            if detrend:
                if G_DETREND_ID   == 0: # Detrend by mean
                    plt.plot(t, trendLine, 'r-', label = 'Mean')
                elif G_DETREND_ID == 1: # Detrend by 3rd order polynomial
                    plt.plot(t, trendLine, 'r-', label = '3th Ord Poly')
                elif G_DETREND_ID == 2: # Detrend by 5th order polynomial
                    plt.plot(t, trendLine, 'r-', label = '5th Ord Poly')
            plt.ylabel('LAeq SPL / dB')
            plt.title('Results for Chunk:Block: %3d:%2d' % (majorInterval, minorInterval))
            plt.grid('on',which=u'major', axis=u'both')
            if G_LEGEND:
                plt.legend(loc='best')
            
            #SUBPLOT #3
            if detrend:        
                plt.subplot(2,2,3) # Plot Time series in BLHS, if required
                plt.tight_layout()
                plt.plot(t, deTrendData, 'b-', label = 'Detrended')
                plt.xlabel('Time / sec')
                plt.ylabel('LAeq SPL / dB')
                plt.grid('on',which=u'major', axis=u'both')
             
            #SUBPLOT #2 - Do some charting and create pretty output - plot the psd
            plt.subplot(2,2,2) # Plot Power Spectrum in TRHS
            plt.tight_layout()
            plt.plot(psd_freqs, psd, 'g', label='PSD')
            #plt.plot(psd_freqs, 2*np.sqrt(2*0.1*psd), 'g', label='PSD')
            plt.axvspan(MIN_MOD_FREQ, MAX_MOD_FREQ, facecolor='g', alpha=0.5, label = 'Search Range')
            plt.grid('on',which=u'major', axis=u'both')
            plt.ylabel('Power Spectrum (Arb Units)')  
            if G_LEGEND:
                plt.legend(loc='best')
    
            #SUBPLOT #4        
            plt.subplot(2,2,4) # Plot Power Spectrum in TRHS
            plt.tight_layout()
            plt.plot(psd_freqs, psd, 'b', label='PSD')
            plt.grid('on',which=u'major', axis=u'both')
            plt.xlabel('Modulation Frequency / Hz')
            plt.ylabel('Power Spectrum (Arb units)',)
            if G_LEGEND:
                plt.legend(loc='best')
      
        # Only do following if data is good
        if goodData: # Kill everything that follows if bad data
            
            considerHarmonics = testHarmonic(Hn, ind_freq, iMax1, 1.5, G_DEBUG)
            #tryPeaks   = signal.argrelmax(hn_cut_fundamental.real); tryPeaks   = tryPeaks[0]
            #tryTroughs = signal.argrelmin(hn_cut_fundamental.real); tryTroughs = tryTroughs[0]
            
            if G_DEBUG:
                print iMax1, maxFreq1        
                #print len(tryPeaks);   print tryPeaks
                #print len(tryTroughs); print tryTroughs
                #print len(hn_cut_fundamental[  tryPeaks]); print hn_cut_fundamental[  tryPeaks].real
                #print len(hn_cut_fundamental[tryTroughs]); print hn_cut_fundamental[tryTroughs].real
    
            # Now decide whether to include individual harmonics
            if not considerHarmonics:
                considerSecond = False
                considerThird  = False
            else:
                # Find locations of 2nd & 3rd harmonics
                maxFreq2  = maxFreq1 * 2; iMax2 = harmonicLocation(psd, psd_freqs, maxFreq2, 1) # Find second harmonic
                maxFreq3  = maxFreq1 * 3; iMax3 = harmonicLocation(psd, psd_freqs, maxFreq3, 2) # Find  third harmonic
                # Now resolve mismatch between indices and frequencies of harmonics
                maxFreq2  = psd_freqs[iMax2]
                maxFreq3  = psd_freqs[iMax3]

                if G_DEBUG:
                    print iMax1, iMax2, iMax3, maxFreq1, maxFreq2, maxFreq3
   
                # Test if second harmonic is to be included & ignore returned array
                considerSecond = testHarmonic(Hn, ind_freq, iMax2, HARMONICS_P2P_LIMIT, G_DEBUG)
                
                # Test if third harmonic is to be included & ignore returned array
                considerThird  = testHarmonic(Hn, ind_freq, iMax3, HARMONICS_P2P_LIMIT, G_DEBUG)
    
            # Print debugging info
            if G_DEBUG:
                print "1 %s" % considerHarmonics
                print "2 %s" % considerSecond
                print "3 %s" % considerThird
                
            ind_harm          = [iMax1]                       # Create array of locations of harmonic #1
            ind_harm_extended = [iMax1-1, iMax1, iMax1+1]
            if considerSecond:
                ind_harm          = [iMax1, iMax2]            # Create array of locations of harmonics #1 - #2
                ind_harm_extended = [iMax1-1, iMax1, iMax1+1, iMax2-1, iMax2, iMax2+1]
                if considerThird:
                    ind_harm          = [iMax1, iMax2, iMax3] # Create array of locations of harmonics #1 - #3
                    ind_harm_extended = [iMax1-1, iMax1, iMax1+1, iMax2-1, iMax2, iMax2+1, iMax3-1, iMax3, iMax3+1]
            else:
                if considerThird:
                    ind_harm          = [iMax1, iMax3]        # Create array of locations of harmonics #1 & #3
                    ind_harm_extended = [iMax1-1, iMax1, iMax1+1, iMax3-1, iMax3, iMax3+1]

            # Print debugging info
            if G_DEBUG:
                print ind_harm
                print ind_harm_extended
                
            # Now plot slected harmonics
            if G_PLOT == 3:
                plt.subplot(2,2,2) # Plot Power Spectrum in TRHS
                plt.plot(psd_freqs[ind_harm], psd[ind_harm], 'ro', label='Harmonics')
           
                # Recreate time series in here using selected harmonics
           #if G_PLOT == 3:
                plt.subplot(2,2,4) # Plot Power Spectrum in TRHS
                plt.plot(psd_freqs[ind_harm_extended], psd[ind_harm_extended], 'ro', label='Filtered')
                #if G_TEST:        
                #    print ind_harm_extended
                for index_he in ind_harm_extended:
                    testFreq  = psd_freqs[index_he]
                    if G_TEST:            
                        print index_he, testFreq, psd[index_he]
                    plt.axvline(x=testFreq, ymin=0, ymax=psd[index_he]/plt.axis()[3], label='Used',color='r',linewidth=1.5)
                          
            # Create array with just selected harmonics in
            Hn_cut = np.zeros_like(Hn)
            Hn_cut[ ind_freq[ind_harm_extended]] = Hn[ ind_freq[ind_harm_extended]] # first put the positive frequencies in
            Hn_cut[-ind_freq[ind_harm_extended]] = Hn[-ind_freq[ind_harm_extended]] # next put the negative frequencies in (FFT gives pos and neg freqs)
            
            # Inverse Fourier transform
            hn_cut = fft.ifft(Hn_cut) # this is the inverse FFT calculation
            
            # Calculate the average peak and trough values
            peaksMean   = float(np.percentile(hn_cut.real,95))
            troughsMean = float(np.percentile(hn_cut.real,5))
    
            # Calculate the average peak to average trough difference over the minorInterval period
            minorAM = peaksMean - troughsMean
                
            # Plot the result
            if G_PLOT == 3:
                plt.subplot(2,2,3) # Plot reconstructed time series
                plt.plot(t, hn_cut, 'r-', linewidth=1.5, label='Reconstructed')
                plt.axhline(y=peaksMean,   xmin=0, xmax=1, label=  'Peaks-Av', color='k', linewidth=1,linestyle='dashed')
                plt.axhline(y=troughsMean, xmin=0, xmax=1, label='Trough -Av', color='k', linewidth=1,linestyle='dashed')
                if G_LEGEND:
                    plt.legend(loc='best')
        else:
            minorAM           = float('NaN')
            maxFreq1          = float('NaN')
            considerHarmonics = False
            considerSecond    = False
            considerThird     = False

        if G_PLOT == 3:            
            #plt.show() # Refreshes figure with all data
    
            #Set up name for figure and save hard copy
            minorFigName = FILE_NAME[fItem] + "_10sec_%d_%d.png" % (majorInterval, minorInterval)
            minorFigName = DIRECTORY_NAME[fItem] + "\\" + minorFigName
            plt.savefig(minorFigName, dpi=600, facecolor='w', edgecolor='w',
                  orientation='landscape', papertype='a3', format='png',
                  transparent=False, frameon=None)
            plt.clf()    # Clear figure of all data before re-use

        # Create nice output storing results of minorInterval caluclations        
        dline  =    "%6d" % majorInterval
        dline +=    "%6d" % minorInterval
        dline +=    "%8d" % startChunk
        dline +=    "%8d" % (stopChunk-1)
        dline +=    "%8d" % (startBlock + (majorInterval*CHUNK_SIZE))
        dline +=    "%8d" % (stopBlock  + (majorInterval*CHUNK_SIZE) -1)        
        if goodData:
            if considerHarmonics:
                if considerSecond:
                    if considerThird:
                        dline +=       "%8d%8d%8d" % (iMax1, iMax2, iMax3)
                        dline += "%8.1f%8.1f%8.1f" % (maxFreq1, maxFreq2, maxFreq3)
                        dline += "%12.2f" % minorAM
                    else:
                        dline +=       "%8d%8d     XXX" % (iMax1, iMax2)
                        dline += "%8.1f%8.1f    XXXX" % (maxFreq1, maxFreq2)
                        dline += "%12.2f" % minorAM
                else:
                    if considerThird:
                        dline +=       "%8d     XXX%8d" % (iMax1, iMax3)
                        dline += "%8.1f    XXXX%8.1f" % (maxFreq1, maxFreq3)
                        dline += "%12.2f" % minorAM
                    else:
                        dline +=       "%8d     XXX     XXX" % (iMax1)
                        dline += "%8.1f    XXXX    XXXX" % (maxFreq1)
                        dline += "%12.2f" % minorAM
            else:
                dline +=       "%8d     XXX     XXX" % (iMax1)
                dline += "%8.1f    XXXX    XXXX" % (maxFreq1)
                dline += "%12.2f" % minorAM
            #Write out decision made regarding inclusion of harmonics
            dline += "%8s" % True
            dline += "%8s" % considerSecond
            dline += "%8s" % considerThird
        else:
            dline +=       "%8d     XXX     XXX" % (iMax1)
            dline += "%8.1f    XXXX    XXXX" % (maxFreq1)
            dline += "        XXXX"
            dline += "%8s" % considerHarmonics
            dline += "%8s" % considerSecond
            dline += "%8s" % considerThird

        dline += "\n"     
        fMinor.write(dline)
        return minorAM, maxFreq1
        #return minorAM, maxFreq1, psd, psd_freqs

    else: # Not the expected amount of data
        print "\nTERMINATING: Process requires %d data points and only %d provided!" % (BLOCK_SIZE ,len(testData[~np.isnan(testData)]))
        #sys.exit() # Exit with warning message    
        #raise Exception("TERMINATING due to insufficient data!")
        return float("Nan"), float("Nan")
        #return float("Nan"), float("Nan"), float("Nan"), float("Nan")

    
#%% - Function to determine level of AM within a minor intervals, eg 10 sec

def IOAminorAM(testData, debug = True, detrend = False):
    """ 
    ##Function:###
    Function 'IOAminorAM' is designed to determine the average level of AM
    within a 10 sec period

    ##Background:###
    Based on the method presented in the IOA mandated code, for consistency

    Author: J H Bass, RES Glasgow
    Date:   26 September 2016
    Version 1.000
        
    ###Version History:###
    1.000   JHB   26/09/16   Initial version
    """

    # Replace any no-entry values, i.e. -99 with 'nan'
    testData = np.array(testData)
    testData[testData <= -99] = float('NaN')
    
    # Check that testData has enough data to process
    if len(testData[~np.isnan(testData)]) == BLOCK_SIZE: # number of points in array
    #if len(testData) == BLOCK_SIZE: # number of points in array
                
        # Fit 3rd order polynomial and detrend data
        if detrend:
            if G_DETREND_ID == 0: # Detrend by mean
                trendLine   = np.average(testData)
            elif G_DETREND_ID == 1: # Detrend by 3rd order polynomial
                polyVals    = np.polyfit(t, testData, 3) # get linear fit to give good starting point for slope
                trendLine   = np.polyval(polyVals,t)
            elif G_DETREND_ID == 2: # Detrend by 5th order polynomial
                polyVals    = np.polyfit(t, testData, 5) # get linear fit to give good starting point for slope
                trendLine   = np.polyval(polyVals,t)
            deTrendData     = testData - trendLine
   
        # Now calculate FFT of data with SAMPLE_FREQ resolution over 'minorInterval' seconds
        # Note: need both real and imaginary parts, both postive and negative frequencies
        #ind_freq = np.arange(1, BLOCK_SIZE/2)
        ind_freq = np.arange(0, (BLOCK_SIZE/2) + 1) 
        freqs = fft.fftfreq(BLOCK_SIZE, SAMPLE_INTERVAL)
        psd_freqs = abs(freqs[ind_freq])       
        
        if detrend:        
            Hn = fft.fft(deTrendData) # This is the FFT calculation
        else:
            Hn = fft.fft(testData)    # This is the FFT calculation
    
        # Calculate the Power Spectrum (Density)
        psd       = abs(Hn[ind_freq])**2 + abs(Hn[-ind_freq])**2
        #psd       = float(2) * psd / BLOCK_SIZE**2 # Normalise according to IOA AM WG
        psd       = psd / BLOCK_SIZE**2 # Normalise according to IOA AM WG - corrected 21 Sep 2016
        
        # Calculate poistion of all maxima (+ve turning points) in psd
        # NB: argrelmax returns tuple, only need result for 0th index, hence [0]
        iMax    = argrelmax(psd)[0] # get indices of all local maxima in psd
        maxFreq = psd_freqs[iMax]   # frequencies corresponding to all local maxima in psd

        # Now determine location of fundamental, ie get indices of peaks within user-defined range              
        peaksInRange = (maxFreq >= MIN_MOD_FREQ) & (maxFreq <= MAX_MOD_FREQ)
        validFreq    = maxFreq[peaksInRange]  # just take the frequencies within user-defined range
    
        # Check if there are any peaks in the user-defined range
        if np.any(validFreq):

            # Determine indices of values peaks in user-defined range
            iMax_UDR   = [np.where(psd_freqs == x)[0][0] for x in validFreq]
        
            # Now identify absolute peak in range
            peakValue  = max(psd[iMax_UDR])                # amplitude of highest peak in range
            iMax1      = np.where(psd == peakValue)[0][0]  # index highest peak in psd in range
            maxFreq1   = psd_freqs[iMax1]
    
            # Check for prominence
            indicesOfContinuum = [iMax1 + x for x in [-3, -2, +2, +3] if iMax1 + x in range(len(psd))]
            continuum  = np.average(psd[indicesOfContinuum])  # linear average for masking level
            prominence = peakValue / float(continuum)         # Prominence is ratio of peak level to masking level
            
            if G_DEBUG:        
                print '{:3d} Prominence ratio= {:.2f}'.format(minorInterval, prominence), 

            #Check prominence ratio is >= than PROMINENCE_RATIO        
            if prominence >= PROMINENCE_RATIO: # Promince ratio exceeded - accept 10 sec period as valid
                #print "Data good: %2d  Pk Posn= %2d   PV= %5.2f   CL= %5.2f" % (minorInterval, iMax1, peakValue, continuum)
                goodData = True
                #waterfall.append(2*np.sqrt(2*FREQ_RESOLUTION*psd))  # Add current psd to waterfall
                #waterfall.append(psd)                   # Add current psd to waterfall
            else:                              # Prominance ratio insufficient - reject 10 sec as invalid
                #print "Data BAD!: %2d  Pk Posn= %2d   PV= %5.2f   CL= %5.2f" % (minorInterval, iMax1, peakValue, continuum)
                goodData = False
                #dummy_psd = np.zeros_like(psd)          # Create an empty psd
                #waterfall.append(dummy_psd)             # Add dummy data to waterfall
        else:                                       
            #print "Data BAD!: %2d  Pk Posn= %2d   PV= %5.2f   CL= %5.2f" % (minorInterval, iMax1, peakValue, continuum)
            goodData = False
            #dummy_psd = np.zeros_like(psd)          # Create an empty psd
            #waterfall.append(dummy_psd)             # Add dummy data to waterfall
        waterfall.append(2*np.sqrt(2*FREQ_RESOLUTION*psd))  # Add current psd to waterfall
        #waterfall.append(psd)  # Add current psd to waterfall

        ## Create minorInterval charting
        if G_PLOT == 3:
            #plt.figure(1, figsize=(16, 12)) # Has 4 subplots - time series of LHS; FDs on RHS
            plt.figure(figsize=(16, 12)) # Has 4 subplots - time series of LHS; FDs on RHS
            
            #SUBPLOT #1
            plt.subplot(2,2,1) # Plot Time series in TLHS
            plt.tight_layout()
            plt.plot(t, testData,  'g-', label = 'Raw data')
            if detrend:
                if G_DETREND_ID   == 0: # Detrend by mean
                    plt.plot(t, trendLine, 'r-', label = 'Mean')
                elif G_DETREND_ID == 1: # Detrend by 3rd order polynomial
                    plt.plot(t, trendLine, 'r-', label = '3th Ord Poly')
                elif G_DETREND_ID == 2: # Detrend by 5th order polynomial
                    plt.plot(t, trendLine, 'r-', label = '5th Ord Poly')
            plt.ylabel('LAeq SPL / dB')
            plt.title('Results for Chunk:Block: %3d:%2d' % (majorInterval, minorInterval))
            plt.grid('on',which=u'major', axis=u'both')
            if G_LEGEND:
                plt.legend(loc='best')
            
            #SUBPLOT #3
            if detrend:        
                plt.subplot(2,2,3) # Plot Time series in BLHS, if required
                plt.tight_layout()
                plt.plot(t, deTrendData, 'b-', label = 'Detrended')
                plt.xlabel('Time / sec')
                plt.ylabel('LAeq SPL / dB')
                plt.grid('on',which=u'major', axis=u'both')
             
            #SUBPLOT #2 - Do some charting and create pretty output - plot the psd
            plt.subplot(2,2,2) # Plot Power Spectrum in TRHS
            plt.tight_layout()
            plt.plot(psd_freqs, psd, 'g', label='PSD')
            #plt.plot(psd_freqs, 2*np.sqrt(2*0.1*psd), 'g', label='PSD')
            plt.axvspan(MIN_MOD_FREQ, MAX_MOD_FREQ, facecolor='g', alpha=0.5, label = 'Search Range')
            plt.grid('on',which=u'major', axis=u'both')
            plt.ylabel('Power Spectrum (Arb Units)')  
            if G_LEGEND:
                plt.legend(loc='best')
    
            #SUBPLOT #4        
            plt.subplot(2,2,4) # Plot Power Spectrum in TRHS
            plt.tight_layout()
            plt.plot(psd_freqs, psd, 'b', label='PSD')
            plt.grid('on',which=u'major', axis=u'both')
            plt.xlabel('Modulation Frequency / Hz')
            plt.ylabel('Power Spectrum (Arb units)',)
            if G_LEGEND:
                plt.legend(loc='best')
      
        # Only do following if data is good
        if goodData: # Kill everything that follows if bad data
            
            considerHarmonics = testHarmonic(Hn, ind_freq, iMax1, 1.5, G_DEBUG)
                
            # Now decide whether to include individual harmonics
            if not considerHarmonics:
                considerSecond = False
                considerThird  = False
            else:
                # Cycle round second and third harmonics
                for ii in [2, 3]:
        
                    # Initial estimate of frequency of harmonic
                    harmonicFreq = maxFreq1 * float(ii)
                                        
                    # Find index of harmonic
                    harmonicIndex   = (np.abs(psd_freqs - harmonicFreq)).argmin()
                    iHarm, harmFreq = harmonicIndex, psd_freqs[harmonicIndex]
                    if G_DEBUG:
                        print ii, iMax1, harmonicIndex, iHarm, maxFreq1, harmonicFreq, harmFreq

                    # Check if it's a local maximum
                    if iHarm not in iMax:
                        # Estimated harmonic frequency is not a peak. Check surrounding indices in case they are
                        iHarmNew = None  # this is a flag to see if any of the surrounding indices are peaks
        
                        # Redefine inds_around to look further around for third harmonic
                        if ii == 2:
                            indexSearch =     [-1, 0, 1]     # 3 lines for 2nd harmonic
                        elif ii == 3:
                            indexSearch = [-2, -1, 0, 1, 2]  # wider search for 3rd harmonic

                        # Get absolute indices to search for peak around estimated harmonic frequency
                        indexHarmonicSearch = [iHarm + x for x in indexSearch if (iHarm + x >= 0) and
                                                                                 (iHarm + x < len(psd))]
        
                        if np.any([x in iMax for x in indexHarmonicSearch]):
                            # One or more of the adjacent indices are local maxima - find the maximum
                            iHarmPeaks    = [x for x in indexHarmonicSearch if x in iMax]  # list of indices which are peaks
                            peakHarmValue = psd[iHarmPeaks]  # get the corresponding amplitudes
                            # Get the index of the maximum value of valid peaks around the initial harmonic location

                            #peaHkValue = max(peakHarmValue)                # amplitude of highest peak in range
                            #iHarmNew   = np.where(psd == peakHValue)[0][0]  # index highest peak in psd in range
                            iHarmNew   = iHarmPeaks[peakHarmValue.tolist().index(max(peakHarmValue))]
        
                        # If one of the surrounding indices was a local maximum, i_harmonic_new will not be None
                        if iHarmNew:
                            # Set flag accordingly for this harmonic
                            if ii == 2:
                                iMax2 = iHarmNew
                            elif ii == 3:
                                iMax3  = iHarmNew
                            # Set flag accordingly for this harmonic
                        else:
                            if ii == 2:
                                #considerSecond = False
                                iMax2 = None
                            elif ii == 3:
                                #considerThird  = False
                                iMax3  = None

                    else:
                        # Set flag accordingly for this harmonic
                        if ii == 2:
                            iMax2 = iHarm
                        elif ii == 3:
                            iMax3  = iHarm

                # Find locations of 2nd & 3rd harmonics
                if iMax2 <> None:
                    maxFreq2 = psd_freqs[iMax2]
                else:
                    maxFreq2 = None
                if iMax3 <> None:
                    maxFreq3 = psd_freqs[iMax3]
                else:
                    maxFreq3 = None

                if G_DEBUG:
                    print iMax1, iMax2, iMax3, maxFreq1, maxFreq2, maxFreq3
   
                # Test if second harmonic is to be included & ignore returned array
                considerSecond = testHarmonic(Hn, ind_freq, iMax2, HARMONICS_P2P_LIMIT, G_DEBUG)
                
                # Test if third harmonic is to be included & ignore returned array
                considerThird  = testHarmonic(Hn, ind_freq, iMax3, HARMONICS_P2P_LIMIT, G_DEBUG)
    
            # Print debugging info
            if G_DEBUG:
                print "1 %s" % considerHarmonics
                print "2 %s" % considerSecond
                print "3 %s" % considerThird
                
            ind_harm          = [iMax1]                       # Create array of locations of harmonic #1
            ind_harm_extended = [iMax1-1, iMax1, iMax1+1]
            if considerSecond:
                ind_harm          = [iMax1, iMax2]            # Create array of locations of harmonics #1 - #2
                ind_harm_extended = [iMax1-1, iMax1, iMax1+1, iMax2-1, iMax2, iMax2+1]
                if considerThird:
                    ind_harm          = [iMax1, iMax2, iMax3] # Create array of locations of harmonics #1 - #3
                    ind_harm_extended = [iMax1-1, iMax1, iMax1+1, iMax2-1, iMax2, iMax2+1, iMax3-1, iMax3, iMax3+1]
            else:
                if considerThird:
                    ind_harm          = [iMax1, iMax3]        # Create array of locations of harmonics #1 & #3
                    ind_harm_extended = [iMax1-1, iMax1, iMax1+1, iMax3-1, iMax3, iMax3+1]

            # Print debugging info
            if G_DEBUG:
                print ind_harm
                print ind_harm_extended
                
            # Now plot slected harmonics
            if G_PLOT == 3:
                plt.subplot(2,2,2) # Plot Power Spectrum in TRHS
                plt.plot(psd_freqs[ind_harm], psd[ind_harm], 'ro', label='Harmonics')
           
                # Recreate time series in here using selected harmonics
           #if G_PLOT == 3:
                plt.subplot(2,2,4) # Plot Power Spectrum in TRHS
                plt.plot(psd_freqs[ind_harm_extended], psd[ind_harm_extended], 'ro', label='Filtered')
                #if G_TEST:        
                #    print ind_harm_extended
                for index_he in ind_harm_extended:
                    testFreq  = psd_freqs[index_he]
                    if G_TEST:            
                        print index_he, testFreq, psd[index_he]
                    plt.axvline(x=testFreq, ymin=0, ymax=psd[index_he]/plt.axis()[3], label='Used',color='r',linewidth=1.5)
                          
            # Create array with just selected harmonics in
            Hn_cut = np.zeros_like(Hn)
            Hn_cut[ ind_freq[ind_harm_extended]] = Hn[ ind_freq[ind_harm_extended]] # first put the positive frequencies in
            Hn_cut[-ind_freq[ind_harm_extended]] = Hn[-ind_freq[ind_harm_extended]] # next put the negative frequencies in (FFT gives pos and neg freqs)
            
            # Inverse Fourier transform
            hn_cut = fft.ifft(Hn_cut) # this is the inverse FFT calculation
            
            # Calculate the average peak and trough values
            peaksMean   = float(np.percentile(hn_cut.real,95))
            troughsMean = float(np.percentile(hn_cut.real,5))
    
            # Calculate the average peak to average trough difference over the minorInterval period
            minorAM = peaksMean - troughsMean
                
            # Plot the result
            if G_PLOT == 3:
                plt.subplot(2,2,3) # Plot reconstructed time series
                plt.plot(t, hn_cut, 'r-', linewidth=1.5, label='Reconstructed')
                plt.axhline(y=peaksMean,   xmin=0, xmax=1, label=  'Peaks-Av', color='k', linewidth=1,linestyle='dashed')
                plt.axhline(y=troughsMean, xmin=0, xmax=1, label='Trough -Av', color='k', linewidth=1,linestyle='dashed')
                if G_LEGEND:
                    plt.legend(loc='best')
        else:
            minorAM           = float('NaN')
            iMax1             = -99
            maxFreq1          = float('NaN')
            considerHarmonics = False
            considerSecond    = False
            considerThird     = False

        if G_PLOT == 3:            
            #plt.show() # Refreshes figure with all data
    
            #Set up name for figure and save hard copy
            minorFigName = FILE_NAME[fItem] + "_10sec_%d_%d.png" % (majorInterval, minorInterval)
            minorFigName = DIRECTORY_NAME[fItem] + "\\" + minorFigName
            plt.savefig(minorFigName, dpi=600, facecolor='w', edgecolor='w',
                  orientation='landscape', papertype='a3', format='png',
                  transparent=False, frameon=None)
            plt.clf()    # Clear figure of all data before re-use

        # Create nice output storing results of minorInterval caluclations        
        dline  =    "%6d" % majorInterval
        dline +=    "%6d" % minorInterval
        dline +=    "%8d" % startChunk
        dline +=    "%8d" % (stopChunk-1)
        dline +=    "%8d" % (startBlock + (majorInterval*CHUNK_SIZE))
        dline +=    "%8d" % (stopBlock  + (majorInterval*CHUNK_SIZE) -1)        
        if goodData:
            if considerHarmonics:
                if considerSecond:
                    if considerThird:
                        dline +=       "%8d%8d%8d" % (iMax1, iMax2, iMax3)
                        dline += "%8.1f%8.1f%8.1f" % (maxFreq1, maxFreq2, maxFreq3)
                        dline += "%12.2f" % minorAM
                    else:
                        dline +=       "%8d%8d     XXX" % (iMax1, iMax2)
                        dline += "%8.1f%8.1f    XXXX" % (maxFreq1, maxFreq2)
                        dline += "%12.2f" % minorAM
                else:
                    if considerThird:
                        dline +=       "%8d     XXX%8d" % (iMax1, iMax3)
                        dline += "%8.1f    XXXX%8.1f" % (maxFreq1, maxFreq3)
                        dline += "%12.2f" % minorAM
                    else:
                        dline +=       "%8d     XXX     XXX" % (iMax1)
                        dline += "%8.1f    XXXX    XXXX" % (maxFreq1)
                        dline += "%12.2f" % minorAM
            else:
                dline +=       "%8d     XXX     XXX" % (iMax1)
                dline += "%8.1f    XXXX    XXXX" % (maxFreq1)
                dline += "%12.2f" % minorAM
            #Write out decision made regarding inclusion of harmonics
            dline += "%8s" % True
            dline += "%8s" % considerSecond
            dline += "%8s" % considerThird
        else:
            dline +=       "%8d     XXX     XXX" % (iMax1)
            dline += "%8.1f    XXXX    XXXX" % (maxFreq1)
            dline += "        XXXX"
            dline += "%8s" % considerHarmonics
            dline += "%8s" % considerSecond
            dline += "%8s" % considerThird

        dline += "\n"     
        fMinor.write(dline)
        return minorAM, maxFreq1
        #return minorAM, maxFreq1, psd, psd_freqs

    else: # Not the expected amount of data
    
        # Create nice output storing results of minorInterval caluclations        
        dline  =    "%6d" % majorInterval
        dline +=    "%6d" % minorInterval
        dline +=    "%8d" % startChunk
        dline +=    "%8d" % (stopChunk-1)
        dline +=    "%8d" % (startBlock + (majorInterval*CHUNK_SIZE))
        dline +=    "%8d" % (stopBlock  + (majorInterval*CHUNK_SIZE) -1)        
        dline += "\n"     
        fMinor.write(dline)
    
        print "\nTERMINATING: Process requires %d data points and only %d provided!" % (BLOCK_SIZE ,len(testData[~np.isnan(testData)]))
        #sys.exit() # Exit with warning message    
        #raise Exception("TERMINATING due to insufficient data!")
        #dummy_psd = np.zeros_like(psd)          # Create an empty psd
        dummy_psd = np.zeros((BLOCK_SIZE/2) + 1) # Create an empty psd
        waterfall.append(dummy_psd)              # Add dummy data to waterfall
        return float("Nan"), float("Nan")
        #return float("Nan"), float("Nan"), float("Nan"), float("Nan")  


#%% - Function to determine majorInterval value of AM from minorInterval values
def majorAM(minorAM):
    
    # Clean up data and remove any no-entry values  
    AM = np.array(minorAM)  
    AM = AM[~np.isnan(AM)]
    #AM = AM.dropna() # alternative if storing data in pandas dataframe
    
    dline  = "%6d|" % majorInterval
    dline += "%8d|" % startChunk
    dline += "%8d|" % (stopChunk-1)
    dline += "%8d|" % len(AM)
    dline += "%8d|" % np.count_nonzero(AM)    
    # Ensure that there are majorIntervalCounts or more periods
    if len(AM) >= MAJOR_INTERVAL_COUNTS:
        majorAM = np.percentile(AM,90)  # calculate 90th percentile value
        # Write results to text file
        dline += "%12.2f|" % np.average(AM)
        dline += "%12.2f|" % np.percentile(AM,10)
        dline += "%12.2f|" % np.percentile(AM,50)
        dline += "%12.2f"  % majorAM
        dline += "\n"
        fMajor.write(dline)
        return majorAM, np.average(AM), np.percentile(AM,10),np.percentile(AM,50)
    else:
        #majorAM = float("NaN")  # Reject entire major period and output null
        dline += "%12.2f|" % float("Nan")
        dline += "%12.2f|" % float("Nan")
        dline += "%12.2f|" % float("Nan")
        dline += "%12.2f"  % float("Nan")
        dline += "\n"
#        dline +=  " <=== WARNING: Insufficent data to determine level of AM\n"
        fMajor.write(dline)
        return float("Nan"), float("Nan"), float("Nan"), float("Nan")


#%% - Function to determine level of AM within a minor intervals, eg 10 sec
def plotMajorAM(testAM, testData, AvgAM, L10AM, L50AM, debug = True):
    
    # Check that testData has enough data to process    
    if len(testData) == CHUNK_SIZE/BLOCK_SIZE: # number of points in array
        ## Create majorInterval charting
        #plt.figure(2, figsize=(16, 12)) # Has 4 subplots - time series on LHS; FDs on RHS
        plt.figure(figsize=(16, 12)) # Has 4 subplots - time series on LHS; FDs on RHS
        
        #SUBPLOT #1
        plt.subplot(2,2,1) # Plot Time series of minorInterval AM in TLHS
        plt.tight_layout()
        cIndex = np.linspace(0, MAJOR_INTERVAL - MINOR_INTERVAL, len(testData))
        plt.plot(cIndex, testData,  'bo-', label = '10 sec AM')
        plt.axhline(y=testAM, label='L90',color='r',linewidth=3)
        plt.axhline(y=L50AM,  label='L50',color='k',linewidth=2,linestyle='dashed')
        plt.axhline(y=L10AM,  label='L10',color='k',linewidth=2,linestyle='dashed')
        plt.axhline(y=AvgAM,  label= 'Av',color='g',linewidth=2)
        plt.ylabel('Modulation Depth (AM) / dB')
        plt.xlabel('Time / sec')
        plt.title('Results for Chunk: %3d' % majorInterval)
        plt.grid('on',which=u'major', axis=u'both')
        if G_LEGEND:
            plt.legend(loc='best')
        
        #SUBPLOT #3
        plt.subplot(2,2,3) # Plot Time series of SPL in BLHS
        plt.tight_layout()
        plotTime = np.arange(len(majorData['LAeq']))/10
        plt.plot(plotTime, majorData['LAeq'], 'g-', label = 'SPL',linewidth=0.25)
        plt.xlabel('Time / sec')
        plt.ylabel('LAeq / dB')
        plt.grid('on',which=u'major', axis=u'both')
        if G_LEGEND:
            plt.legend(loc='best')
         
        #SUBPLOT #2
        plt.subplot(2,2,2) # Plot distribution of AM in TRHS
        plt.tight_layout()
        if G_CUMUL:        
            n, bins, patches = plt.hist(testData, normed = True, range = (0,10), cumulative=True, alpha = 0.5)
            #n, bins, patches = plt.hist(testData, range = (0,10), cumulative=True, alpha = 0.5)
            plt.ylabel('Cumulative Probability') 
        else:
            n, bins, patches = plt.hist(testData, range = (0,10), alpha = 0.5)
            #n, bins, patches = plt.hist(testData, normed = True, range = (0,10), alpha = 0.5)
            plt.ylabel('No. of Items') 
        plt.axvline(x=testAM, label='L90',color='r',linewidth=3)
        plt.axvline(x=L50AM, label='L50',color='k',linewidth=2,linestyle='dashed')
        plt.axvline(x=L10AM, label='L10',color='k',linewidth=2,linestyle='dashed')
        plt.axvline(x=AvgAM, label= 'Av',color='g',linewidth=2)
        plt.grid('on',which=u'major', axis=u'both')
        plt.xlabel('Modulation Depth (AM) / dB')
        if G_LEGEND:
            plt.legend(loc='best')

        # Tweak spacing to prevent clipping of ylabel
        #plt.subplots_adjust(left=0.15)

        #SUBPLOT #4        
        plt.subplot(2,2,4) # Modulation Frequency Plot in TRHS
        plt.tight_layout()
        # For data points lying within the min-max range
        plt.plot(HZminorInterval, testData, 'bo', label='PSD')
        # For data points lying outside the min-max range which may require listening
        #plt.plot(HZminorInterval, testData, 'r+', label='PSD')
        plt.axis([0, 5, plt.axis()[2],plt.axis()[3]])        
        plt.axvline(x=MIN_MOD_FREQ, label='Min',color='k',linewidth=1,linestyle='dashed')
        plt.axvline(x=MAX_MOD_FREQ, label='Max',color='k',linewidth=1,linestyle='dashed')
        plt.grid('on',which=u'major', axis=u'both')
        plt.xlabel('Modulation Frequency / Hz')
        plt.ylabel('Modulation Depth (AM) / dB')
        if G_LEGEND:
            plt.legend(loc='best')      
        #plt.show()
        
        # Create nice output storing results of majorInterval caluclations        
        majorFigName = FILE_NAME[fItem] + "_10min_%d.png" % majorInterval
        majorFigName = DIRECTORY_NAME[fItem] + "\\" + majorFigName
        plt.savefig(majorFigName, dpi=600, facecolor='w', edgecolor='w',
              orientation='landscape', papertype='a3', format='png',
              transparent=False, frameon=None)

        plt.clf() # Clear figure of data for re-use
    else:
        print "\nWARNING:     Expecting %d data points but only %d provided!" % (CHUNK_SIZE/BLOCK_SIZE, len(testData))
        #sys.exit() # Exit with warning message
        #raise Exception("Ending!")                         - Need to fix this ultimately!!!!!!!!
    return


#%% - Function to show level of AM over entire survey period, eg 24 hours
def plotSurveyAM(majorAM, testData, debug = True):

    # Create majorInterval charting
    #plt.figure(3, figsize=(16, 12)) # Has 2 subplots - time series on top; waterfall on bottom
    plt.figure(figsize=(16, 12)) # Has 2 subplots - time series on top; waterfall on bottom
    
    #SUBPLOT #1 - Plot time series of minor & major AM over survey
    plt.subplot(2,1,1) 
    plt.tight_layout()

    # Plot the minorInterval data as red dots
    xticks = ['0:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00', '23:50']
    daily_time = pd.date_range('0:00:00', '23:59:50', freq='10S')
    start_time = daily_time[0]
    end_time = daily_time[-1]
    if debug:
        print start_time, end_time

    #plt.plot(np.arange(len(testData)), testData, 'r.', label='Minor') # Plots red dots
    plt.plot(daily_time, testData, 'r.', label='Minor') # Plots red dots

    # Plot the majorInterval data as a blue line with markers
    #tStep = np.linspace(0,len(testData)-(MAJOR_INTERVAL//MINOR_INTERVAL),len(majorAM))
    #tStep = tStep + ((MAJOR_INTERVAL//MINOR_INTERVAL)//2)
    daily_time = pd.date_range('0:05', '23:55', freq='10T')
    #daily_time = daily_time + (daily_time[1]/2)
    if debug:
        print daily_time, len(daily_time)

    #plt.plot(tStep, majorAM,  'bo-', label = 'Major', linewidth=2)
    plt.plot(daily_time, majorAM,  'bo-', label = 'Major', linewidth=2)
    plt.axis([start_time, end_time, plt.axis()[2],plt.axis()[3]])
    if G_SURVEY:
        plt.axvspan(' 0:00', '07:00', facecolor='g', alpha=0.5, label = 'Search Range')
        plt.axvspan('07:00', '19:00', facecolor='g', alpha=0.5, label = 'Search Range')
    plt.ylabel('Modulation Depth / dB')
    plt.title("Results for Entire Survey Period For: %s" % FILE_NAME[fItem])
    #plt.set_xlim(xticks[0], xticks[8])
    #plt.set_xticks(xticks, minor = False)
    #plt.set_xticklabels(xticks)
    #plt.ticklabel_format()
    plt.grid('on',which=u'major', axis=u'both')
    if G_LEGEND:
        plt.legend(loc='best')     

#    levels = [0.0, 0.2, 0.5, 0.9, 1.5, 2.5, 3.5]
#    contour = plt.contour(X, Y, Z, levels, colors='k')
#    plt.clabel(contour, colors = 'k', fmt = '%2.1f', fontsize=12)
#    contour_filled = plt.contourf(X, Y, Z, levels)
#    plt.colorbar(contour_filled)

    #SUBPLOT 2 - Create waterfall plot of all results on bottom
    plt.subplot(2,1,2)
    plt.tight_layout()
    wfall = np.array(waterfall)
    wsize = len(wfall)
    wfall = wfall.T #transpose array
    daily_time = pd.date_range('0:00:00', '23:59:50', freq='10S')
    daily_time = daily_time[0:wsize]
    frz = np.linspace(0.0, 5.0, 51) # Bodge - need to fix this and remove literals
    #levels = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    levels = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    if G_MAP  == 0:  # jet
        #plt.contourf(np.arange(wsize),frz,wfall)
        #plt.contourf(np.arange(wsize),frz,wfall, levels = levels)
        #plt.contourf(np.arange(wsize),frz,wfall,cmap=plt.cm.afmhot, levels = levels)
        plt.contourf(daily_time,frz,wfall,cmap=plt.cm.afmhot, levels = levels)
        #plt.contourf(np.arange(wsize),frz,wfall,cmap=plt.cm.afmhot)
    elif G_MAP == 1: # viridis
        #plt.contourf(np.arange(wsize),frz,wfall,cmap=plt.cm.viridis, levels = levels)
        plt.contourf(daily_time,frz,wfall,cmap=plt.cm.viridis, levels = levels)
    elif G_MAP == 2: # afmhot
        #plt.contourf(np.arange(wsize),frz,wfall,cmap=plt.cm.afmhot, levels = levels)
        plt.contourf(daily_time,frz,wfall,cmap=plt.cm.afmhot, levels = levels)
    else:            # Reds (crap)
        plt.contour(np.arange(wsize),frz,wfall,cmap=plt.cm.Reds)   # Useless as doesn't show variation well
    cbar = plt.colorbar(orientation = 'horizontal', aspect = 60)
    cbar.set_label('Peak to Trough AM / dB')
    #cbar.ax.set_ylabel('Peak to Trough AM / dB')
    #cbar.ay.set_xlabel('Peak to Trough AM / dB')
    # plt.ticklabel_format(axis='both', style='plain', scilimits=(0,0))
    plt.ylabel('Modulation Frequency / Hz')
    #plt.xlabel("Time Interval / %d second periods" % MINOR_INTERVAL)
    plt.xlabel("Time of Day / HH:MM:SS")
    plt.grid('on',which='major', axis='both',color='0.5', linestyle='--', linewidth=0.5)
    # linewidth previously 2
    plt.axhline(y=MIN_MOD_FREQ, label='Min',color='w',linewidth=1,linestyle='dashed')
    plt.axhline(y=MAX_MOD_FREQ, label='Max',color='w',linewidth=1,linestyle='dashed')
    if G_SURVEY:
        plt.axvspan(   0, 2520, facecolor='w', alpha=0.15, label = 'Search Range')
        plt.axvspan(7200, 8640, facecolor='w', alpha=0.15, label = 'Search Range')
    if G_LEGEND:
        plt.legend(loc='best')
    #plt.show()
    
    # Create nice output storing results of entire survey
    surveyFigName = FILE_NAME[fItem] + "_Survey.png"
    surveyFigName = DIRECTORY_NAME[fItem] + "\\" + surveyFigName
    plt.savefig(surveyFigName, dpi=600, facecolor='w', edgecolor='w',
          orientation='landscape', papertype='a3', format='png',
          transparent=False, frameon=None)

    plt.clf() # Clear figure of data for re-use
        
    return


#%% - Write Headers for Minor File Routine
def writeMinorHeader(f):

    ## Write all input parameters to output file
    dline = "INPUT SETTINGS:\n\n";  f.write(dline)
    
    if G_TEST:   # G_TEST 
        dline = "G_TEST       - Status of Test Code: Operative"
    else:
        dline = "G_TEST       - Status of Test Code: Ignored"
    f.write(dline + "\n")
    
    if G_DEBUG:    #G_DEBUG
        dline = "G_DEBUG      - Verbose output"
    else:
        dline = "G_DEBUG      - Minimal output"
    f.write(dline + "\n")
    
    if G_DETREND:  #G_DETREND  
        dline = "G_DETREND    - Detrend data prior to analysis"
    else:
        dline = "G_DETREND    - Dont' detrend data prior to analysis"
    f.write(dline + "\n")
    
    if G_DETREND_ID == 0: #G_DETREND_ID    
        dline = "G_DETREND_ID - Trend line is mean value"
    elif G_DETREND_ID == 1:
        dline = "G_DETREND_ID - Trend line is 3rd order polynomial"
    elif G_DETREND_ID == 2:
        dline = "G_DETREND_ID - Trend line is 5th order polynomial"
    f.write(dline + "\n")
    
    if G_LEGEND:    
        dline = "G_LEGEND     - Show legends on all plots"
    else:
        dline = "G_LEGEND     - Don't show legends on plots"
    f.write(dline + "\n")

    if G_CUMUL:    
        dline = "G_CUMUL      - Plot cumulative distribution function"
    else:
        dline = "G_CUMUL      - Plot probability density function"
    f.write(dline + "\n")

    if G_FORMAT_ID == 0: #G_DETREND_ID    
        dline = "G_FORMAT_ID  - Simple data format: no header and 1 data value per line"
    elif G_FORMAT_ID == 1:
        dline = "G_FORMAT_ID  - 24acoustics data format: header and 00:00:00.0,39.8,30.3"
    f.write(dline + "\n\n")
        
    dline = "Original data sample rate:      %9d /      Hz"   % SAMPLE_FREQ;                           f.write(dline+"\n")
    dline = "Length of minor interval(block):%9d / seconds"   % MINOR_INTERVAL;                        f.write(dline+"\n")
    dline = "Length of major interval(chunk):%9d / seconds"   % MAJOR_INTERVAL;                        f.write(dline+"\n")
    dline = "No. of valid periods required:  %9d / samples"   % MAJOR_INTERVAL_COUNTS;                 f.write(dline+"\n")
    dline = "Lower limit on modulation freq: %9.1f /      Hz" % MIN_MOD_FREQ;                          f.write(dline+"\n")
    dline = "Upper limit on modulation freq):%9.1f /      Hz" % MAX_MOD_FREQ;                          f.write(dline+"\n")
    dline = "Length of block:                %9d / samples"   % BLOCK_SIZE;                            f.write(dline+"\n")
    dline = "Length of chunk:                %9d / samples"   % CHUNK_SIZE;                            f.write(dline+"\n")
    dline = "Time between samples:           %9.1f / seconds" % SAMPLE_INTERVAL;                       f.write(dline+"\n")
    dline = "Start time used for dframes:    %9s"             % START_TIME;                            f.write(dline+"\n")
    dline = "Input file name:                %s\%s.%s"        % (DIRECTORY_NAME[fItem], FILE_NAME[fItem],FILE_EXTN[fItem]); f.write(dline+"\n\n")
    
    ## Write header line for main data block    
    # Minor - Header Line 1
    dline  = "<---Step--->"
    dline += "<-Chunk(10min)->"
    dline += "<-Block(10sec)->"
    dline += "<---Harmonics (Index)-->"
    dline += "<----Harmonics (Hz)---->"
    dline += "<--AM(P-T)->"
    dline += "<--Include Harmonics?-->\n"
    f.write(dline)

    # Minor Header line 2
    dline  = " Major Minor"
    dline += "   Start    Stop"
    dline += "   Start    Stop"
    dline += "       1"
    dline += "       2"
    dline += "       3"
    dline += "       1"
    dline += "       2"
    dline += "       3"
    dline += "          dB"
    dline += "       1"
    dline += "       2"
    dline += "       3\n"
    f.write(dline)   
    return


#%% - Write Headers for Minor File Routine
def writeMajorHeader(f):

    ## Write all input parameters to output file
    dline = "INPUT SETTINGS:\n\n";  f.write(dline)
    
    if G_TEST:   # G_TEST 
        dline = "G_TEST       - Status of Test Code: Operative"
    else:
        dline = "G_TEST       - Status of Test Code: Ignored"
    f.write(dline + "\n")
    
    if G_DEBUG:    #G_DEBUG
        dline = "G_DEBUG      - Verbose output"
    else:
        dline = "G_DEBUG      - Minimal output"
    f.write(dline + "\n")
    
    if G_DETREND:  #G_DETREND  
        dline = "G_DETREND    - Detrend data prior to analysis"
    else:
        dline = "G_DETREND    - Dont' detrend data prior to analysis"
    f.write(dline + "\n")
    
    if G_DETREND_ID == 0: #G_DETREND_ID    
        dline = "G_DETREND_ID - Trend line is mean value"
    elif G_DETREND_ID == 1:
        dline = "G_DETREND_ID - Trend line is 3rd order polynomial"
    elif G_DETREND_ID == 2:
        dline = "G_DETREND_ID - Trend line is 5th order polynomial"
    f.write(dline + "\n")
    
    if G_LEGEND:    
        dline = "G_LEGEND     - Show legends on all plots"
    else:
        dline = "G_LEGEND     - Don't show legends on plots"
    f.write(dline + "\n")
    
    if G_CUMUL:    
        dline = "G_CUMUL      - Plot cumulative distribution function"
    else:
        dline = "G_CUMUL      - Plot probability density function"
    f.write(dline + "\n")

    if G_FORMAT_ID == 0: #G_DETREND_ID    
        dline = "G_FORMAT_ID  - Simple data format: no header and 1 data value per line"
    elif G_FORMAT_ID == 1:
        dline = "G_FORMAT_ID  - 24acoustics data format: header and 00:00:00.0,39.8,30.3"
    f.write(dline + "\n\n")
        
    dline = "Original data sample rate:      %9d /      Hz"   % SAMPLE_FREQ;                           f.write(dline+"\n")
    dline = "Length of minor interval(block):%9d / seconds"   % MINOR_INTERVAL;                        f.write(dline+"\n")
    dline = "Length of major interval(chunk):%9d / seconds"   % MAJOR_INTERVAL;                        f.write(dline+"\n")
    dline = "No. of valid periods required:  %9d / samples"   % MAJOR_INTERVAL_COUNTS;                 f.write(dline+"\n")
    dline = "Lower limit on modulation freq: %9.1f /      Hz" % MIN_MOD_FREQ;                          f.write(dline+"\n")
    dline = "Upper limit on modulation freq):%9.1f /      Hz" % MAX_MOD_FREQ;                          f.write(dline+"\n")
    dline = "Length of block:                %9d / samples"   % BLOCK_SIZE;                            f.write(dline+"\n")
    dline = "Length of chunk:                %9d / samples"   % CHUNK_SIZE;                            f.write(dline+"\n")
    dline = "Time between samples:           %9.1f / seconds" % SAMPLE_INTERVAL;                       f.write(dline+"\n")
    dline = "Start time used for dframes:    %9s"             % START_TIME;                            f.write(dline+"\n")
    dline = "Input file name:                %s\%s.%s"        % (DIRECTORY_NAME[fItem], FILE_NAME[fItem],FILE_EXTN[fItem]); f.write(dline+"\n\n")
    
    ## Write header line for main data block    
    # Major - Header Line 1
    dline  = "  Step|"
    dline += "    Chunk (10min)|"
    dline += "     No. of Items|"
    dline += "             Measures of AM(Pk-Tr) / dB            \n"
    f.write(dline)
    dline  = " Major|"
    dline += "   Start|    Stop|"
    dline += "     Len|   Count|"
    dline += "     Average|      10th %|      50th %|      90th %\n"
    f.write(dline)
    return

    
#%% - Write Headers for Minor File Routine

def tidyup(debug=True):
    
    now = time.asctime()
    if debug:
        print "\nFinished writing data to output files on %s" % now
    
# Screen, Major & Minor - Final Line
    dline  = "\nFinished writing data to output files on %s" % now
    #print dline
    fMinor.write(dline)    
    fMajor.write(dline)
    fMinor.close()
    fMajor.close()
    plt.close(1) # Close figure 1
    plt.close(2) # Close figure 2
    plt.close(3) # Close figure 3
    return

    
#%% Ensures the dataframe for each day is time sequenced correctly and padded to 24 hours

def framePad(df):
    print 'Padding file',
    if not ((df.index[0].hour  ==  0) and (df.index[0].minute  ==  0) and (df.index[0].second  ==  0)): # file starts later than beginning of day
        print 'from start with 0:00:00' # # Add line at the beginning with starting timestamp, i.e. 0:00:00
        
        newTime          = df.index[0]
        date             = pd.datetime(newTime.year, newTime.month, newTime.day, 0, 0, 0, 0)
        #date             = pd.to_datetime(date)
        df2              = pd.DataFrame([date], columns = ['Timestamp'])
        df2['LAeq']      = 0
        df2['Timestamp'] = pd.to_datetime(df2['Timestamp'])
        df2.index        = df2['Timestamp']
        # Add extra blank line to beginning of file
        df = df2.append(df)
        
    if not ((df.index[-1].hour == 23) and (df.index[-1].minute == 59) and (df.index[-1].second == 59)): # file ends before end of day
        print 'at end with 23:59:59.900000' # Add line at the end with ending timestamp, i.e. 23:59:59.900000
        newTime          = df.index[-1]
        date             = pd.datetime(newTime.year, newTime.month, newTime.day, 23, 59, 59, 900000)
        #date             = pd.to_datetime(date)
        df2              = pd.DataFrame([date], columns = ['Timestamp'])
        df2['LAeq']      = 0
        df2['Timestamp'] = pd.to_datetime(df2['Timestamp'])
        df2.index        = df2['Timestamp']
        # Add extra blank line to end of file
        df = df.append(df2)

    # Now resample to fill dataframe    
    df = df.resample('100L').mean()
    return df


#%% - Read main input text file

##############################################################################################################################
############## MAIN CODE STARTS HERE #########################################################################################
##############################################################################################################################

# Get user to verify range of modulation frequencies prior to analysis/assessment
print "Range of modulation frequencies assessed is:{:4.1f} - {:4.1f} Hz".format(MIN_MOD_FREQ, MAX_MOD_FREQ)
print "This corresponds to LSS rotor speeds of:    {:4.1f} - {:4.1f} rpm".format(MIN_MOD_FREQ*20, MAX_MOD_FREQ*20)
#continueExit = int(raw_input("Frequencies correct? (0 - Continue; 1 - Exit): "))
continueExit = 0
if continueExit == 0: # User chose to carry on

    # Ask user what file they want to process
    NO_OF_FILES, DIRECTORY_NAME, FILE_NAME, FILE_EXTN = getFile('Select data file...',
                                                                r'C:\Users\bass\Downloads\DenBrook\PreCompliance-Sep2016\CrookeBurnell\IOA\ThirdPass-Live!',
                                                                'csv', True, G_DEBUG)
    # If there are files to process, then cycle through them all                                              
    if NO_OF_FILES > 0:
        
        # Get data format from user and ensure that it is an integer, not a sting, hence int()
        # G_FORMAT_ID = int(raw_input("Enter data format ID (0 - Simple; 1 - 24acoustics): "))
        # Put some validation in here to ensure user only enters 0 or 1
        if G_DEBUG:
            print "You entered %s" % G_FORMAT_ID
            
        for fItem in range(NO_OF_FILES):
    
            # Create filename string
            fName = FILE_NAME[fItem] + '.' + FILE_EXTN[fItem]
            # Start clock to work out run time
            profileStartTime = time.time()
    
            # Create arrays for storing key results
            waterfall  = [] # Array to store all minorInterval psds for entire survey
            AllAMminor = [] # Array to store all minorInterval data for entire survey
    
            # Open text file (100ms LAeq data) using Pandas read_csv command
            print "INFORMATION: Importing A-weighted data for file %d of %d...  " % (fItem + 1, NO_OF_FILES),
    
            if G_FORMAT_ID == 0:   # 'Simple text format, one data entry (@ sampleFreq) per line
                allData = pd.read_csv(os.path.join(DIRECTORY_NAME[fItem],fName), names = ['LAeq'], header =None)
            
                # Add a time stamp throughout data period
                msecTimeStep = str(int(SAMPLE_INTERVAL*1000))+'ms'
                timeStamp = pd.date_range(start = START_TIME, periods = len(allData), freq = msecTimeStep) # i.e. 100 ms
                allData['Timestamp'] = timeStamp
            
                # Make timestamp the dataframe's index
                allData.index = allData['Timestamp']
            
            elif G_FORMAT_ID == 1: # 24acoustics data format: Timestamp,LAeq,LBFeq: 00:00:00.0,39.8,30.3
                # allData = pd.read_csv(os.path.join(DIRECTORY_NAME[fItem],fName),usecols=['Timestamp','LAeq'])
                #allData = pd.read_csv(os.path.join(DIRECTORY_NAME[fItem],fName),usecols=['Timestamp','LBeq'])
                allData = pd.read_csv(os.path.join(DIRECTORY_NAME[fItem],fName))
                #allData = allData[['Timestamp','LBFeq']]
                # Change name of LBFeq to LAeq for compatibility
                allData = allData.rename(columns={allData.columns[1] : 'LAeq'})
                # Convert timestamp to datetime64 for better plotting - NOTE: VERY VERY SLOW!!!!
                allData['Timestamp'] = pd.to_datetime(allData['Timestamp'])
                allData.index = allData['Timestamp']
                # Back or forward fill if incomplete day
#                if len(allData) < 864000:
#                    allData = framePad(allData)

            print "...complete."
    
            # Printout length of input dta file, if debugging
            if G_DEBUG:
                print "INFORMATION: Input file %d is %d elements long" % (fItem, len(allData))
    
#%% - Create output text files, for both minor & major intervals
            #Open txt file for output
            minorOutputFile = FILE_NAME[fItem] + "_10sec.txt"
            majorOutputFile = FILE_NAME[fItem] + "_10min.txt"
            fMinor = open(os.path.join(DIRECTORY_NAME[fItem], minorOutputFile),'w')
            fMajor = open(os.path.join(DIRECTORY_NAME[fItem], majorOutputFile),'w')
            
            ## Create file/column headers
            writeMinorHeader(fMinor) # function to write column headers for minor output data
            writeMajorHeader(fMajor) # function to write column headers for major output data
    
#%% - Check that 10 min of data are available and, if not, warn user
            majorIntervals = len(allData)//CHUNK_SIZE
            if majorIntervals >= 1:
            #if majorIntervals >= 0:
                
                # Create array to store majorIntervals results
                AMmajorInterval = np.zeros(majorIntervals)    
                # Calculate number of minorIntervals per majorInterval
                minorIntervals = CHUNK_SIZE//BLOCK_SIZE
                if minorIntervals >= 1:
                            
                    # Determine number of points required for time reference within minorIntervals
                    t = np.linspace(0, MINOR_INTERVAL-SAMPLE_INTERVAL, BLOCK_SIZE) # time array
            
                    ## Step through entire text file in MAJOR_INTERVAL chunks
                    #PS_10sec   = []
                    #Freq_10sec = []
                    for majorInterval in range(majorIntervals): #Step through data in CHUNK_SIZE chunks
                    
                        # Create array to store minorIntervals results
                        AMminorInterval = np.zeros(minorIntervals)       # Array for storing level of AM, i.e. scalar
                        HZminorInterval = np.zeros_like(AMminorInterval) # Array for storing frequency of AM, i.e. scalar
                                            
                        # Grab one CHUNK_SIZE chunk (e.g. 10 min)at a time
                        startChunk = majorInterval * CHUNK_SIZE
                        stopChunk  =    startChunk + CHUNK_SIZE
                        majorData  = allData[startChunk:stopChunk] # this just takes 6000 points, i.e. 10 minutes
            
                        for minorInterval in range(minorIntervals):  #Step through data in BLOCK_SIZE chunks
                            
                            # grab one BLOCK_SIZE chunk (e.g. 10 sec) at a time
                            startBlock = minorInterval * BLOCK_SIZE
                            stopBlock  =    startBlock + BLOCK_SIZE
                            minorData  = majorData[startBlock:stopBlock] # this just takes 100 points, i.e. 10 seconds
            
                            # Do minorInterval (e.g. 10 sec) processing / charting - determine level of AM & fundamental
                            if G_METHOD == 0:                        
                                AMminorInterval[minorInterval], HZminorInterval[minorInterval] = minorAM(minorData['LAeq'], G_DEBUG, G_DETREND)
                            elif G_METHOD == 1:
                                AMminorInterval[minorInterval], HZminorInterval[minorInterval] = IOAminorAM(minorData['LAeq'], G_DEBUG, G_DETREND)                            
                            #AMminorInterval[minorInterval], HZminorInterval[minorInterval], dummA, dummB = minorAM(minorData['LAeq'], G_DEBUG, G_DETREND)
                            #PS_10sec.append(dummA)
                            #Freq_10sec.append(dummB)
                            if G_DEBUG:
                                print "INFORMATION: Run %3d:%2d Pk-Pk AM level = %3.1f dB @ %3.1fHz" % (majorInterval, minorInterval,
                                                                                                        AMminorInterval[minorInterval],
                                                                                                        HZminorInterval[minorInterval])
                            else:
                                #print ".",  # Alert user to progress of analysis
                                pass
                
                        ## Do majorInterval (e.g. 10 min) processing & charting
                        AMmajorInterval[majorInterval], AMavg, AM10, AM50 = majorAM(AMminorInterval)
                        if G_PLOT >= 2:
                            plotMajorAM(AMmajorInterval[majorInterval], AMminorInterval, AMavg, AM10, AM50, G_DEBUG)
                        AllAMminor = np.concatenate((AllAMminor, AMminorInterval), axis = 0) # Computationally efficient
                    
                    # Do Survey processing & charting
                    if G_PLOT >= 1:
                        plotSurveyAM(AMmajorInterval, AllAMminor, G_DEBUG)
                    
                    # Tidy up and exit
                    tidyup(G_DEBUG)
                    print 'Code execution took %10.2f secs' %  (time.time() - profileStartTime)
                    print 'Code execution took %10.2f mins' % ((time.time() - profileStartTime)/60)
                else: # if minorIntervals < 1
                    # Tidy up and exit
                    tidyup(G_DEBUG)    
                    raise Exception('TERMINATING: Insufficent data available for BLOCK!') # Stop execution and exit
            else:     # if majorIntervals < 1
                # Tidy up and exit
                tidyup(G_DEBUG)    
                # Stop execution and exit
                #raise Exception('TERMINATING: Insufficent data available for CHUNK!')
    
    else:   # No files selected, i.e. NO_OF_FILES = 0
        print 'TERMINATING: No files selected!'
else:
    print 'TERMINATING: Ensure that range of modulation frequencies is altered!'
##############################################################################################################################
############## MAIN CODE ENDS HERE ###########################################################################################
##############################################################################################################################