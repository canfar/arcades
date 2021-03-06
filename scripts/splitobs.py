# """This script splits out different observations in a single measurement set based on 
# name of the fields observerd."""

import numpy as np
import glob
from os import path

# This script should be run after running scriptForPI.py to generate calibrated 
# measurement sets.

# Note: that this script can be run with SPACESAVING=2 to reduce the number of intermediate
# files saved.  For later versions of CASA (at least using the pipeline for 4.7.0),
# using SPACESAVING=3 will generate problems, as this leaves only a single concatenated
# measurement set, and it is very difficult to split out individual observations of
# the same source after concatenation.

# Note: This script requires a version of CASA which includes the 'msmd' (measurement set
# metadata) command.  CASA 4.2.2pipe includes msmd, but casa4.0.1 does not (I am still
# testing versions inbetween these).  There is no problem running scriptForPI.py using
# an older version of CASA (say 4.0.1), and then running this script subsequently with
# a later version of CASA (say 4.3)


####################### Start of the script #####################

# Part 1: Identify all of the files which have had measurement sets generated for them
# assume a file name format of [uid...].ms.split.cal
# NB for CADC: the set of calibrated measurement sets generated by scriptForPI may be a 
# smaller list than the total number of raw datasets, if some raw datasets failed QA

# NB: The file name structure should imply that the measurement sets selected 
# have been split after calibration, implying that we wish to keep information
# in the 'data' column for our additional splitting per target
# If we need to include files that instead end in .ms, they might have the calibrated info 
# stored in the 'corrected' column instead.  This subtlety is used for the 'split' command
# used below.


# Read in the list of calibrated measurement sets one-by-one, pull out target names, and create
# the individual split measurement sets


def split_ms(filename):
    """
    split out the CALIBRATE and OBSERVE_TARGET observations from given ALMA measurement set
    """
    print("Split out observations found in {}".format(filename))
    msmd.open(filename)
    ms_name = filename.rstrip("ms.split.cal")

    # 1) Create a list of all target names for science & calibrator sources.
    #   Note that all science fields have the observing intent 'OBSERVE_TARGET'
    #   All calibrator fields have observing intents of 'CALIBRATE*', however,
    #   sometimes the science fields also have these observing intents
    #   included (e.g., CALIBRATE_WVR)	
        
    # Identify science fields
    # Note that sometimes have multiple field numbers for the same field name
    sci_field_names = list(np.unique(msmd.fieldsforintent("OBSERVE_TARGET*",True)))
        
    # Get list of all fields (likely msmd.fields could provide a complete list but
    # here we take the calibrate list and append the science target list)
    field_names = list(np.unique(msmd.fieldsforintent('CALIBRATE*',True)))
    field_names.extend(sci_field_names)
    field_names = np.unique(np.array(field_names))

    # remove the attachment to the msmd object.
    msmd.done()
    
    # Loop through each of these fields and split out measurement set    
    for field_name in field_names:
        # if this is in the science target list call it science, else its a calibrator
        obs_type = field_name in sci_field_names and "SCI" or "CAL"
        split_dir = "{}.{}.{}.ms.split.cal".format(ms_name, obs_type, field_name)
        print("Splitting {} into {}".format(field_name, split_dir))
        # Remove the subdirectory, if it exists
        shutil.rmtree(split_dir, ignore_errors=True)
        # split out the given field by name using casa split command
        split(vis=filename,
              outputvis=split_dir, 
              field=field_name,
              datacolumn='data')
            
if __name__ == "__main__":
    BASE_FILENAME = "*.ms.split.cal" # Types of files to process
    for filename in glob.glob(BASE_FILENAME):
        split_ms(filename)

