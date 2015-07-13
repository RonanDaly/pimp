import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from pimp.settings_dev import MEDIA_ROOT
import os
from frank.models import Peak, SampleFile
from djcelery import celery
from decimal import *

from celery import shared_task
import subprocess

## Method to derive the peaks from the mzXML file
@celery.task
def msnAnalysis(experiment):

    ### Scarey Script ######
    #
    r_source = robjects.r['source']
    r_source('~/Git/MScProjectRepo/pimp/django_projects/pimp/frank/frankMSnPeakMatrix.R')
    r_frankMSnPeakMatrix = robjects.globalenv['frankMSnPeakMatrix']
    output = r_frankMSnPeakMatrix(source_directory = '~/Git/MScProjectRepo/pimp/django_projects/pimp_data/justin-sample-dataset-1')
#
#    ########################
#
#    ### Debug Script ######
#     r_source = robjects.r['source']
#     r_source('~/R/MyScripts/testScript.R')
#     r_testScript = robjects.globalenv['testscript']
#     output = r_testScript('~/Git/MScProjectRepo/pimp/django_projects/pimp_data/beer-versus-urine-1')
#    #######################
#
#   The columns of the data frame returned by the R call have to be seperated into vectors
    peakID = output[0]
    parentPeak = output[1]
    msnLevel = output[2]
    retention_time = output[3]
    mz_ratio = output[4]
    intensity = output[5]
    # Remember that sample must be a factor vector for the 'real' dataset
    sample = output[6]
    groupPeakMSn = output[7]
    collisionEnergy = output[8]
    # sampleID contains the 'name' of the source file from which the peak was derived
    sampleID = output[9]
    # Determine the total number of peaks
    number_of_peaks = len(peakID)

    # Create a dictionary, using the arbitrary numerical values assigned to the peaks by Tony Lawson's script
    # with the value of the pair being the peak object (the django representation of the peak)
    peak_dict = {}
    print "Populating peak list ...."
    for peak in range (0,number_of_peaks):
        if peak%100 == 0:
            print 'Processed '+str(peak)+'peaks of '+str(number_of_peaks)+' total peaks'
        # Note the [peak]-1 is due to the indexing of R beginning from 1
        peak_source_file = SampleFile.objects.get(name=sampleID.levels[sampleID[peak]-1])
        peak_mass = mz_ratio[peak]
        peak_retention_time = retention_time[peak]
        peak_intensity = intensity[peak]
        peak_parent_peak = int(parentPeak[peak])
        peak_msn_level = int(msnLevel[peak])
        # Determine whether the peak have a parent ion
        try:
            # If the peak is ms1 and has no parent ion, then no foreign key value should be added.
            if peak_parent_peak == 0 and peak_msn_level == 1:
                parentIon = None
            elif peak_parent_peak in peak_dict:
                parent_peak_id = peak_dict.get(peak_parent_peak)
                parentIon = Peak.objects.get(id = parent_peak_id)
            else:
                raise ValueError('Parent Peak Not Found')
        except ValueError as e:
            print 'Peak relationships not maintained'
        new_peak = Peak.objects.create(
            sourceFile = peak_source_file,
            mass = peak_mass,
            retentionTime = peak_retention_time,
            intensity = peak_intensity,
            parentPeak = parentIon,
            msnLevel = peak_msn_level,
        )
        peak_dict[int(peakID[peak])] = new_peak.id
    print 'Peaks Populated!!'

@celery.task
def queryMagma(experiment):
    

    # Get the peaks and create a
    # jarRetCode = subprocess.call([javaPath, jar, jarPath, fileType, mfPath, outSwitch, outPath])

if __name__ == '__main__':
    msnAnalysis()
