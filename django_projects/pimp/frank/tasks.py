import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from pimp.settings_dev import MEDIA_ROOT
import os
from frank.models import Peak, SampleFile, CandidateAnnotation, Compound, Repository,\
    CompoundRepository, FragmentationSet, Experiment, AnnotationQuery
from djcelery import celery
from decimal import *
import urllib2
import urllib
from cookielib import CookieJar
from frank.peakFactories import msnPeakBuilder
from suds.client import Client, WebFault
from django.contrib.auth.models import User
import time
import os
from frank.models import *
from django.db.models import Max
from cStringIO import StringIO
from django.core.exceptions import ValidationError
import frank.network_sampler as ns
import re
from subprocess import call


from celery import shared_task
import subprocess

## Method to run simon's network sampler
@celery.task
def runNetworkSampler(fragmentation_set_slug, sample_file_name, annotation_query_slug):
    import jsonpickle
    # fragmentation set is the fragmentation set we want to run the analysis on (slug)
    # annotation_query is the new annotation query slug
    fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_slug)
    new_annotation_query = AnnotationQuery.objects.get(slug=annotation_query_slug)
    parent_annotation_query = new_annotation_query.parent_annotation_query
    sample_file = SampleFile.objects.filter(name=sample_file_name)
    # check if the new annotation query already has annotations attached and delete them if it does
    # might want to remove this at some point, but it's useful for debugging
    old_annotations = CandidateAnnotation.objects.filter(annotation_query = new_annotation_query)
    if old_annotations:
        print "Deleting old annotations..."
        for annotation in old_annotations:
            annotation.delete()

    new_annotation_query.status = 'Submitted'
    new_annotation_query.save()
    # Extract the peaks
    peaks = Peak.objects.filter(fragmentation_set = fragmentation_set,msn_level=1,source_file=sample_file)
    print "Found " + str(len(peaks)) + " peaks"

    peakset = ns.FragSet()
    peakset.annotations = []


    print "Extracting peaks"
    # for i in range(100):
    for p in peaks:
        # p = peaks[i]
        newmeasurement = ns.Measurement(p.id)
        peakset.measurements.append(newmeasurement)
        # Loop over all candidate annotations for this peak
        all_annotations = CandidateAnnotation.objects.filter(peak=p,annotation_query=parent_annotation_query)
        for annotation in all_annotations:
            # split the name up - THIS WILL BE REMOVED
            split_name = annotation.compound.name.split(';')
            short_name = split_name[0]
            # find this one in the previous ones
            previous_pos = [i for i,n in enumerate(peakset.annotations) if n.name==short_name]
            if len(previous_pos) == 0:
                # ADD A COMPOUND ID
                peakset.annotations.append(ns.Annotation(annotation.compound.formula,short_name,annotation.compound.id,annotation.id))
                newmeasurement.annotations[peakset.annotations[-1]] = float(annotation.confidence)
            else:
                # check if this measurement has had this compound in its annotation before 
                # (to remove duplicates with different collision energies - highest confidence is used)
                this_annotation = peakset.annotations[previous_pos[0]]
                if this_annotation in newmeasurement.annotations:
                    current_confidence = newmeasurement.annotations[this_annotation]
                    if float(annotation.confidence) > current_confidence:
                        newmeasurement.annotations[this_annotation] = float(annotation_confidence)
                        this_annotation.parentid = annotation.id
                else:
                    newmeasurement.annotations[this_annotation] = float(annotation.confidence)

    print "Stored " + str(len(peakset.measurements)) + " peaks and " + str(len(peakset.annotations)) + " unique annotations"


    print "Sampling..."
    sampler = ns.NetworkSampler(peakset)
    sampler.set_parameters(jsonpickle.decode(new_annotation_query.massBank_params))
    sampler.sample()

    new_annotation_query.status = 'Processing'
    new_annotation_query.save()
    print "Storing new annotations..."
    # Store new annotations in the database
    for m in peakset.measurements:
        peak = Peak.objects.get(id=m.id)
        for annotation in m.annotations:
            compound = Compound.objects.get(id = annotation.id)
            parent_annotation = CandidateAnnotation.objects.get(id=annotation.parentid)
            add_info_string = "Prior: {:5.4f}, Edges: {:5.2f}".format(peakset.prior_probability[m][annotation],peakset.posterior_edges[m][annotation])
            an = CandidateAnnotation.objects.create(compound=compound,peak=peak,confidence=peakset.posterior_probability[m][annotation],
                annotation_query=new_annotation_query,difference_from_peak_mass = parent_annotation.difference_from_peak_mass,
                mass_match=parent_annotation.mass_match,additional_information = add_info_string)

    edge_dict = sampler.global_edge_count()
    new_annotation_query.status = 'Completed'
    new_annotation_query.save()
    return edge_dict



## Method to derive the peaks from the mzXML file for LCMS-MSN data sets
@celery.task
def msnGeneratePeakList(experiment_slug, fragmentation_set_id):
    # Determine the directory of the experiment
    experiment_object = Experiment.objects.get(slug = experiment_slug)
    # From the experiment object derive the file directory of the .mzXML files
    filepath = os.path.join(MEDIA_ROOT,
                            'frank',
                            experiment_object.created_by.username,
                            experiment_object.slug,
                            )
    fragmentation_set_object = FragmentationSet.objects.get(id=fragmentation_set_id)
    r_source = robjects.r['source']
    r_source('~/Git/MScProjectRepo/pimp/django_projects/pimp/frank/frankMSnPeakMatrix.R')
    r_frankMSnPeakMatrix = robjects.globalenv['frankMSnPeakMatrix']
    fragmentation_set_object.status = 'Processing'
    fragmentation_set_object.save()
    output = r_frankMSnPeakMatrix(source_directory = filepath)
    peak_generator = msnPeakBuilder(output, fragmentation_set_object.id)
    peak_generator.populate_database_peaks()
    fragmentation_set_object.status = 'Completed'
    fragmentation_set_object.save()
    return 'Done'

# Method to batch query the mass bank annotation tool using SOAP
@celery.task
def massBank_batch_search(fragmentation_set_id, annotation_query_id):
    fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
    sample_peak_qset = Peak.objects.filter(fragmentation_set=fragmentation_set)
    query_spectra = get_massBank_query_spectra(sample_peak_qset)
    # Now the query is structured, send it to mass Bank
    positive_spectra = query_spectra['positive_spectra']
    negative_spectra = query_spectra['negative_spectra']
    positive_spectra_query_status = query_mass_bank(positive_spectra, 'Positive', annotation_query_id)
    negative_spectra_query_status = query_mass_bank(negative_spectra, 'Negative', annotation_query_id)
    return 'Done'

# Method to format a query set of peaks for batch query of the mass bank annotation tool
def get_massBank_query_spectra(sample_peak_query_set):
    print 'Number of Peaks = '+str(len(sample_peak_query_set))
    number_of_msn_levels = sample_peak_query_set.aggregate(Max('msn_level'))
    number_of_msn_levels = number_of_msn_levels['msn_level__max']
    print 'Number of MSN Levels = '+str(number_of_msn_levels)
    positive_samples_query = []
    negative_samples_query = []
    for level in range(1, (number_of_msn_levels)):
        peaks_in_msn_level = sample_peak_query_set.filter(msn_level=level)
        print 'Number of peaks in level = '+str(len(peaks_in_msn_level))
        for peak in peaks_in_msn_level:
            polarity = peak.source_file.polarity
            peak_name = peak.slug
            fragmented_peaks = sample_peak_query_set.filter(parent_peak=peak)
            spectrum_query_string = list('Name:'+peak_name+';')
            for fragment in fragmented_peaks:
                spectrum_query_string.append(''+str(fragment.mass)+','+str(fragment.intensity)+';')
            if polarity == 'Positive':
                positive_samples_query.append(''.join(spectrum_query_string))
            else:
                negative_samples_query.append(''.join(spectrum_query_string))
    query_spectra = {
        'positive_spectra':positive_samples_query,
        'negative_spectra':negative_samples_query,
    }
    return query_spectra

# Method to send the query spectra to mass bank and populate the database
def query_mass_bank(query_spectra, polarity, annotation_query_id):
    # Check to ensure there are spectra to send to mass bank, if not, simply return
    if len(query_spectra) == 0:
        return 'Done'
    annotation_query_object = AnnotationQuery.objects.get(id=annotation_query_id)
    mass_bank_parameters = annotation_query_object.massBank_params
    # Obtain the parameters of the search from the database
    mass_bank_parameters = re.findall('<(.*?)>', mass_bank_parameters, re.DOTALL)
    mail_address = str(mass_bank_parameters[0])
    number_of_instrument_types = len(mass_bank_parameters)
    instruments = []
    if number_of_instrument_types > 0:
        for instrument_index in range(1,number_of_instrument_types):
            instruments.append(str(mass_bank_parameters[instrument_index]))
    ion = polarity
    type = "1"
    client = Client('http://www.massbank.jp/api/services/MassBankAPI?wsdl')
    try:
        response = client.service.execBatchJob(
            type,
            mail_address,
            query_spectra,
            instruments,
            ion,
        )
    except WebFault, e:
        print e.message
    job_id = response
    print 'JOB ID = '+job_id
    job_list = [job_id]
    for seconds in range(0, 144):
        time.sleep(600)
        try:
            response2 = client.service.getJobStatus(job_list)
            print response2
        except WebFault, e:
            print e.message
            # May also need to handle URLError here for if the connection fails
        if response2['status'] == 'Completed':
            break
    try:
        response3 = client.service.getJobResult(job_list)
    except WebFault, e:
        print e.message
    results = response3
    ## results is a list
    print 'The length of the list is...'+str(len(results))
    annotation_query_object = AnnotationQuery.objects.get(id=annotation_query_id)
    for result_set_list in results:
        print 'Processing...'+result_set_list['queryName']
        peak_identifier_slug = result_set_list['queryName']
        annotations = ()
        number_of_annotations = 0
        try:
            annotations = result_set_list['results']
            number_of_annotations = result_set_list['numResults']
        except AttributeError, ae:
            print 'No Result Set Was Found'
        massBank = Repository.objects.get(name = 'MassBank')
        peak_object = Peak.objects.get(slug=peak_identifier_slug)
        for index in range(0, number_of_annotations):
            each_annotation = annotations[index]
            elements_of_title = re.split('; ', each_annotation['title'])
            try:
                compound_object = Compound.objects.get_or_create(
                    formula = each_annotation['formula'],
                    exact_mass = each_annotation['exactMass'],
                    name=elements_of_title[0],
                )[0]
                compound_repository = CompoundRepository.objects.get_or_create(
                    compound = compound_object,
                    repository = massBank,
                    repository_identifier = each_annotation['id'],
                )
                annotation_mass = Decimal(each_annotation['exactMass'])
                difference_in_mass = peak_object.mass-annotation_mass
                ## Justin's suggestion - I am maybe doing this wrong
                ppm = 1000000*abs(difference_in_mass)/annotation_mass
                mass_match = False
                if ppm < 3.0:
                    mass_match = True
                ## Try and obtain the adduct and collision energy from the description
                adduct_label = None
                collision_energy = None
                for element in elements_of_title:
                    if element.startswith('[M'):
                        adduct_label = element
                    if element.startswith('CE'):
                        collision_energy = element
                CandidateAnnotation.objects.create(
                    compound = compound_object,
                    peak = peak_object,
                    confidence = each_annotation['score'],
                    annotation_query = annotation_query_object,
                    difference_from_peak_mass = difference_in_mass,
                    mass_match = mass_match,
                    adduct = adduct_label,
                    instrument_type = elements_of_title[1],
                    collision_energy = collision_energy,
                    additional_information = each_annotation['title']
                )
            except ValidationError, e:
                print '****WARNING INCORRECTLY FORMATED RESPONSE*****\n *****ANNOTATION IGNORED*****'
    return 'Done'


def gcmsGeneratePeakList(experiment_name_slug, fragmentation_set_id):
    return 'Done'


@celery.task
def nist_batch_search(fragmentation_set_id, annotation_query_id):
    ### NEED CODE HERE TO MAKE MSP FILE #####
    print 'nist_batch_search called!'
    call(["wine",
          "C:\\2013_06_04_MSPepSearch_x32\\MSPepSearch.exe",
          "M",
          "/HITS",
          "3",
          "/PATH",
          "C:\\NIST14\\MSSEARCH",
          "/MAIN",
          "mainlib",
          "/INP",
          "Z:\\home\\scottiedog27\\Git\\MScProjectRepo\\pimp\\django_projects\\pimp\\frank\\NISTQueryFiles\\output.msp",
          "/OUT",
          "Z:\\home\\scottiedog27\\Git\\MScProjectRepo\\pimp\\django_projects\\pimp\\frank\\NISTQueryFiles\\nist_out.txt",
          "/COL",
          "pz,cf"])
    ### NEED CODE HERE TO READ NIST OUPUT FILE ###
    ### NEED CODE HERE TO POPULATE ANNOTATIONS ###
    return 'Done'

def nist_make_msp_file(fragmentation_set_id, annotation_query_id):
    pass
    #### MSP file format seems to be as follows
    #   NAME: name_of_query
    #   DB#: name_of_query
    #   Comments: nothing
    #   Num Peaks: number_of_peaks_in_spectra
    #   mass    intensity   ### For each of the peaks in the spectra

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
