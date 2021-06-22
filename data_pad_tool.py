import tkFileDialog
import Tkinter
import numpy as np
import time
import pandas as pd
import os

# G_DEBUG = True         # True-verbose output; False - Minimal output
G_DEBUG = False        # True-verbose output; False - Minimal output

SAMPLE_FREQ = 10          # Sample rate in Hz (10 Hz is 100 ms data)
MINOR_INTERVAL = 10          # Length of data chunks for analysis (in seconds)
MAJOR_INTERVAL = 600          # Length of data chunk for overall analysis (in seconds)
MAJOR_INTERVAL_COUNTS = 30          # Number of valid periods required in major intervals (30 pref)
PROMINENCE_RATIO = 4          # Prominence ratio check value from IOA AM WG
HARMONICS_P2P_LIMIT = 1.5          # Harmonics peak to peak check value from IOA AM WG

BLOCK_SIZE = MINOR_INTERVAL*SAMPLE_FREQ  # No of samples in a minor interval (block)
CHUNK_SIZE = MAJOR_INTERVAL*SAMPLE_FREQ  # No of samples in a major interval (chunk)
SAMPLE_INTERVAL = 1.0/SAMPLE_FREQ             # Time (sec) between samples
FREQ_RESOLUTION = 1.0/MINOR_INTERVAL          # Frequency resolution of PSD (in Hz)
START_DIR = r'C:\Users\bass\Downloads'


def getFile(userMessage, userDir, userFileType, allowMultiple=False, debug=False):  
    root = Tkinter.Tk() # Set the Tkinter root
    root.withdraw() # this stops a small window popping up

    # This line opens the file open dialog
    full_path = tkFileDialog.askopenfilename(parent=root, title=userMessage,
                                             defaultextension=userFileType,
                                             initialdir=userDir,
                                             multiple=allowMultiple,
                                             filetypes=[('CSV files', '*.csv'), ('Text files', '*.txt'), ('All files', '*.*')])
    # If allowMultiple is true response is a tuple, otherwise a string

    if full_path:  # full-path contains at least one filename
        if allowMultiple:
            totalFiles = len(full_path)
            pathName = []
            fileName = []
            fileExtension = []
            for file in range(totalFiles):
                dummy, dummyX = os.path.split(full_path[file])
                pathName.append(dummy)
                dummy, dummyX = os.path.splitext(dummyX)
                fileName.append(dummy)
                fileExtension.append(dummyX[1:])
        else:
            totalFiles = 1
            pathName, fileName = os.path.split(full_path)
            fileName, fileExtension = os.path.splitext(fileName)
            fileExtension = fileExtension[1:]
    else:  # full_path doesn't contain any filenames because cancel pressed
        totalFiles = 0
        pathName = None
        fileName = None
        fileExtension = None

    if debug:  # Prints out list of selected files, for debugging purposes
        print totalFiles
        print pathName
        print fileName
        print fileExtension
        if totalFiles > 0:
            for fItem in range(totalFiles):
                print 'File: %d' % fItem,
                print '%s' % pathName[fItem],
                print '/%s' % fileName[fItem],
                print '.%s' % fileExtension[fItem]

    # Return key information to main programme
    return totalFiles, pathName, fileName, fileExtension


def file_pad(infile, outfile):
    for line in infile:
        outfile.write(line)
    infile.close()
    line = line.replace('59.8', '59.9')
    outfile.write(line)
    outfile.close()
    return

# Ask user what file they want to process
NO_OF_FILES, DIRECTORY_NAME, FILE_NAME, FILE_EXTN = getFile('Select data file',
                                                            START_DIR,
                                                            'csv', True,
                                                            G_DEBUG)
# If there are files to process, then cycle through
if NO_OF_FILES > 0:
    for fItem in range(NO_OF_FILES):
        fName = FILE_NAME[fItem] + '.' + FILE_EXTN[fItem]
        print "File %d of %d: " % (fItem+1, NO_OF_FILES),
        data = pd.read_csv(os.path.join(DIRECTORY_NAME[fItem], fName))
        if len(data) < 864000:
            print "[%d lines long]" % (len(data)),
            original = open(os.path.join(DIRECTORY_NAME[fItem], fName), "r")
            fName = FILE_NAME[fItem] + '_F.' + FILE_EXTN[fItem]
            copy = open(os.path.join(DIRECTORY_NAME[fItem], fName), "w")
            file_pad(original, copy)
            data = pd.read_csv(os.path.join(DIRECTORY_NAME[fItem], fName))
            if len(data) == 864000:
                print " :Fixed!"
            # Tidy up file names
            fName1 = FILE_NAME[fItem] + '.' + FILE_EXTN[fItem]
            fName2 = FILE_NAME[fItem] + '_Orig.' + FILE_EXTN[fItem]
            os.rename(os.path.join(DIRECTORY_NAME[fItem], fName1),
                      os.path.join(DIRECTORY_NAME[fItem], fName2))
            fName1 = FILE_NAME[fItem] + '_F.' + FILE_EXTN[fItem]
            fName2 = FILE_NAME[fItem] + '.' + FILE_EXTN[fItem]
            os.rename(os.path.join(DIRECTORY_NAME[fItem], fName1),
                      os.path.join(DIRECTORY_NAME[fItem], fName2))
else:   # No files selected, i.e. NO_OF_FILES = 0
    print 'TERMINATING: No files selected!'