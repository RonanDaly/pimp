import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from pimp.settings_dev import MEDIA_ROOT
import os
from frank.models import Peak, SampleFile
from djcelery import celery
from decimal import *
import urllib2
import urllib
from cookielib import CookieJar
from frank.helperObjects import msnPeakBuilder
from suds.client import Client, WebFault
from django.contrib.auth.models import User
import time


from celery import shared_task
import subprocess

## Method to derive the peaks from the mzXML file
@celery.task
def msnGeneratePeakList(experiment):

#     ### Scarey Script ######
    r_source = robjects.r['source']
    r_source('~/Git/MScProjectRepo/pimp/django_projects/pimp/frank/frankMSnPeakMatrix.R')
    r_frankMSnPeakMatrix = robjects.globalenv['frankMSnPeakMatrix']
    output = r_frankMSnPeakMatrix(source_directory = '~/Git/MScProjectRepo/pimp/django_projects/pimp_data/justin-sample-dataset-1')
#    ### Debug Script ######
#     r_source = robjects.r['source']
#     r_source('~/R/MyScripts/testScript.R')
#     r_testScript = robjects.globalenv['testscript']
#     output = r_testScript('~/Git/MScProjectRepo/pimp/django_projects/pimp_data/beer-versus-urine-1')
#  #######################
    peak_generator = msnPeakBuilder(output)
    peak_generator.populate_database_peaks()


@celery.task
def massBank_batch_search(experiment):
    #currentUser = User.objects.get_by_natural_key(username=username)
    ## Remember to change this to the current users email address
    mailAddress = 'scottgreig27@gmail.com'
    query = [
        'Name:Sample1; 59.300,653466.0;112.300,19802.0;',
        'Name:Sample2; 30.000,34653.5;80.100,430693.5;',
        'Name:Sample3; 80.100,430693.5;55.900,89109.0;60.100,391089.5',
    ]
    inst = [
        "all",
    ]
    ion = "Positive"
    type = "1"
    params = [
        type,
        mailAddress,
        query,
        inst,
        ion,
    ]
    client = Client('http://www.massbank.jp/api/services/MassBankAPI?wsdl')
    print client
    try:
        response = client.service.execBatchJob(
            type,
            mailAddress,
            query,
            inst,
            ion,
        )
    except WebFault, e:
        print e.message
    job_id = response
    print 'JOB ID = '+job_id
    job_list = [job_id]
    for seconds in range(0, 60):
        time.sleep(60)
        try:
            response2 = client.service.getJobStatus(job_list)
            print response2
        except WebFault, e:
            print e.message
        if response2['status'] == 'Completed':
            break
    try:
        response3 = client.service.getJobResult(job_list)
    except WebFault, e:
        print e.message
    results = response3
    for result in results:
        print result


# def magma_mass_tree():
#     sample = SampleFile.objects.get(name = 'Urine_37_Top10_NEG.mzXML')
#     ms1_peaks = Peak.objects.filter(sourceFile = sample, msnLevel = 1)
#     testFile = open('magma_mass_tree.txt', 'w')
#     for peak in ms1_peaks:
#         testFile.write(str(peak.mass)+': '+str(peak.intensity))
#         ms2_children = Peak.objects.filter(msnLevel = 2, parentPeak = peak)
#         if len(ms2_children) == 0:
#             testFile.write(',\n')
#         else:
#             testFile.write('(\n')
#             for child_peak in ms2_children:
#                 testFile.write('\t'+str(child_peak.mass)+': '+str(child_peak.intensity)+',\n')
#             testFile.write(')\n')
#     print('test file written')
#
# def MAGMa_api():
#     # cj = CookieJar()
#     # #test_tree =
#     form_values = dict(ms_data_format='mass_tree',
#                        ms_data = ''
#                    structure_database='pubchem',
#                    max_mz='1200',
#                    min_refscore='1',
#                    excl_halo='on',
#                    structure_format='smiles',
#                    scenario='[{"type":"phase1","steps":"2"},{"type":"phase2","steps":"1"}]',
#                    ionisation_mode='-1',
#                    max_broken_bonds='3',
#                    max_water_losses='1',
#                    mz_precision='5',
#                    mz_precision_abs='0.001',
#     )
#     # form_values = {}
#     # data = urllib.urlencode(form_values)
#     # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#     # req = urllib2.Request('http://www.emetabolomics.org/magma/start', data)
#     # page = opener.open(req)
#     # print page.read()
#     cookie_jar = CookieJar()
#     opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
#     urllib2.install_opener(opener)
#
#     ## acquire cookie
#     url_1 = 'http://www.emetabolomics.org/magma'
#     req = urllib2.Request(url_1)
#     rsp = urllib2.urlopen(req)
#
#     # do POST
#     url_2 = 'http://www.emetabolomics.org/magma/start'
#     values = dict()
#     data = urllib.urlencode(form_values)
#     req = urllib2.Request(url_2, data)
#     rsp = urllib2.urlopen(req)
#     content = rsp.read()
#
#     print content


if __name__ == '__main__':
    msnGeneratePeakList()
