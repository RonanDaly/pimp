__author__ = "Scott Greig"

import rpy2.robjects as robjects
from django.conf import settings
from frank.models import Peak, SampleFile, CandidateAnnotation, Compound, AnnotationTool, \
    CompoundAnnotationTool, FragmentationSet, Experiment, AnnotationQuery
from djcelery import celery
from celery import chain
from celery.utils.log import get_task_logger
from decimal import *
from frank.peakFactories import MSNPeakBuilder, GCMSPeakBuilder
from suds.client import WebFault
import os
import sys
import logging
from frank.models import *
import frank.network_sampler as ns
import jsonpickle
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from frank.annotationTools import MassBankQueryTool, NISTQueryTool, SIRIUSQueryTool
from urllib2 import URLError
import datetime
from decimal import *
import pandas as pd
import numpy as np

# PiMP objects
from experiments.models import Analysis as PimpAnalysis
from data.models import Peak as PimpPeak
from data.models import Dataset

from MS2LDA.lda_for_fragments import Ms2Lda
from fileupload.views import findpolarity
import pandas as pd
from rpy2.robjects import pandas2ri

celery_logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)

# Return the correct annotation Tool given it's name slug.
def get_annotation_tool(name):
    annotation_tool = AnnotationTool.objects.get(slug=name)
    return annotation_tool


# Create and return annotation query given the correct parameters
def get_annotation_query(fragSet, name, tool_name, params):
    annotation_query, created = AnnotationQuery.objects.get_or_create(
        name=fragSet.name + name,
        fragmentation_set=fragSet,
        annotation_tool=get_annotation_tool(tool_name),
        annotation_tool_params=jsonpickle.encode(params))

    return annotation_query


# Method to run a set of default annotations and set the preferred annotations to the highest
# confidence level (clean methods) - currently used for PiMP/FrAnK intergration
@celery.task
def run_default_annotations(fragSet, user):

    print "In default annotations"
    # Parameters for nist annotation tool
    default_params_nist = {"search_type": "G",
                           "library": ["nist_msms", "nist_msms2", "massbank_msms"],
                           "max_hits": 10}
    # Create nist_query
    nist_query = get_annotation_query(fragSet, "-NistQ", "nist", default_params_nist)

    # Run the nist search for annotations
    print "running Nist from default"
    nist_batch_search(nist_query.id)

    # Create a precursor mass query using the annotations from the NIST search
    pre_default_params = {"parents": [str(nist_query.id)],
                          "positive_transforms": ["M+H"],
                          "negative_transforms": ["M-H"],
                          "mass_tol": 5}
    precursor_query = get_annotation_query(fragSet, "-preFQ", "precursor-mass-filter", pre_default_params)

    # Run the precursor mass filter to remove any results that differ from the m/z by a certain threshold
    print "running precursor mass query from default"
    precursor_mass_filter(precursor_query.id)

    # Create a relationship between the parent and child annotations
    AnnotationQueryHierarchy.objects.create(
        parent_annotation_query=nist_query,
        subquery_annotation_query=precursor_query)

    # Create a run to remove duplicate annotations for a peak, setting the preferred annotation automatically
    clean_default_params = {}
    clean_default_params['parents'] = [str(precursor_query.id)]
    clean_default_params['preferred_threshold'] = Decimal(50)
    clean_default_params['delete_original'] = False
    clean_default_params['do_preferred'] = True
    clean_default_params['collapse_multiple'] = True

    clean_query = get_annotation_query(fragSet, "-cleanQ", "clean-annotations", clean_default_params)
    clean_filter(clean_query.id, user)

    #Create a relationship between the parent and child annotations
    AnnotationQueryHierarchy.objects.get_or_create(
        parent_annotation_query=precursor_query,
        subquery_annotation_query=clean_query)

    print "end default annotations"


@celery.task
def runNetworkSampler(annotation_query_id):
    # def runNetworkSampler(fragmentation_set_slug, sample_file_name, annotation_query_slug):
    """
    Method to run the Network Sampler developed by Simon Rogers
    :author Simon Rogers
    :param fragmentation_set_slug: A string containing the unique slug for the fragmentation set
    :param sample_file_name: A string for the sample file name
    :param annotation_query_slug: A string containing the unique slug for the annotation query
    :return: edge_dict:
    """
    new_annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    parameters = jsonpickle.decode(new_annotation_query.annotation_tool_params)
    fragmentation_set = new_annotation_query.fragmentation_set
    # fragmentation set is the fragmentation set we want to run the analysis on (slug)
    # annotation_query is the new annotation query slug
    # fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_slug)
    parent_annotation_query = AnnotationQuery.objects.filter(slug__in=parameters['parents'])[0]
    # parent_annotation_query = new_annotation_query.parent_annotation_query
    # sample_file = SampleFile.objects.filter(name=sample_file_name)
    # check if the new annotation query already has annotations attached and delete them if it does
    # might want to remove this at some point, but it's useful for debugging
    old_annotations = CandidateAnnotation.objects.filter(annotation_query=new_annotation_query)
    if old_annotations:
        print "Deleting old annotations..."
        for annotation in old_annotations:
            annotation.delete()

    new_annotation_query.status = 'Submitted'
    new_annotation_query.save()
    # Extract the peaks
    # peaks = Peak.objects.filter(fragmentation_set=fragmentation_set, msn_level=1, source_file=sample_file)
    peaks = Peak.objects.filter(fragmentation_set=fragmentation_set, msn_level=1)
    print "Found " + str(len(peaks)) + " peaks"

    peakset = ns.FragSet()
    peakset.compounds = []

    print "Extracting peaks"
    # for i in range(100):
    for p in peaks:
        # p = peaks[i]
        newmeasurement = ns.Measurement(p.id)
        peakset.measurements.append(newmeasurement)
        # Loop over all candidate annotations for this peak
        all_annotations = CandidateAnnotation.objects.filter(peak=p, annotation_query=parent_annotation_query)
        for annotation in all_annotations:
            # split the name up - THIS WILL BE REMOVED
            split_name = annotation.compound.name.split(';')
            short_name = split_name[0]
            # find this one in the previous ones
            previous_compound = [n for n in peakset.compounds if n.name == short_name]
            if len(previous_compound) == 0:
                peakset.compounds.append(ns.Compound(annotation.compound.id, annotation.compound.formula, short_name))
                newmeasurement.annotations[ns.Annotation(peakset.compounds[-1], annotation.id)] = float(
                    annotation.confidence)
            else:
                this_compound = previous_compound[0]
                # Have we seen this compound in this measurement at all?
                previous_annotation_local = [n for n in newmeasurement.annotations if n.compound == this_compound]
                if len(previous_annotation_local) > 0:
                    this_annotation = previous_annotation_local[0]
                    this_annotation.parentid = annotation.id
                    newmeasurement.annotations[this_annotation] = float(annotation.confidence)
                else:
                    newmeasurement.annotations[ns.Annotation(this_compound, annotation.id)] = float(
                        annotation.confidence)


                    # previous_annotations = [n for n in newmeasurement.annotations if n.name==short_name]
                    # if len(previous_annotations) == 0:
                    #     # ADD A COMPOUND ID
                    #     peakset.annotations.append(ns.Annotation(annotation.compound.formula,short_name,annotation.compound.id,annotation.id))
                    #     newmeasurement.annotations[peakset.annotations[-1]] = float(annotation.confidence)
                    # else:
                    #     # check if this measurement has had this compound in its annotation before
                    #     # (to remove duplicates with different collision energies - highest confidence is used)
                    #     this_annotation = previous_annotations[0]
                    #     current_confidence = newmeasurement.annotations[this_annotation]
                    #     if float(annotation.confidence) > current_confidence:
                    #         newmeasurement.annotations[this_annotation] = float(annotation.confidence)
                    #         this_annotation.parentid = annotation.id

    print "Stored " + str(len(peakset.measurements)) + " peaks and " + str(len(peakset.compounds)) + " unique compounds"

    print "Sampling..."
    sampler = ns.NetworkSampler(peakset)
    sampler.set_parameters(parameters)
    sampler.sample()

    new_annotation_query.status = 'Processing'
    new_annotation_query.save()
    print "Storing new annotations..."
    # Store new annotations in the database
    for m in peakset.measurements:
        peak = Peak.objects.get(id=m.id)
        for annotation in m.annotations:
            compound = Compound.objects.get(id=annotation.compound.id)
            parent_annotation = CandidateAnnotation.objects.get(id=annotation.parentid)
            add_info_string = "Prior: {:5.4f}, Edges: {:5.2f}".format(peakset.prior_probability[m][annotation],
                                                                      peakset.posterior_edges[m][annotation])
            an = CandidateAnnotation.objects.create(compound=compound, peak=peak,
                                                    confidence=peakset.posterior_probability[m][annotation],
                                                    annotation_query=new_annotation_query,
                                                    difference_from_peak_mass=parent_annotation.difference_from_peak_mass,
                                                    mass_match=parent_annotation.mass_match,
                                                    additional_information=add_info_string)

    edge_dict = sampler.global_edge_count()
    new_annotation_query.status = 'Completed Successfully'
    new_annotation_query.save()
    return edge_dict


@celery.task
def msn_generate_peak_list(experiment_slug, fragmentation_set_id, ms1_peaks):
    """
    Method to extract peak data from a collection of sample files
    :param experiment_slug: Integer id of the experiment from which the files orginate
    :param fragmentation_set_id:    Integer id of the fragmentation set to be populated
    :return: True   Boolean value denoting the completion of the task
    Passing the MS1 peaks from Pimp when they are run together.
    """
    print ('In MSN generate peak list')
    # Determine the directory of the experiment
    experiment_object = Experiment.objects.get(slug=experiment_slug)
    # From the experiment object derive the file directory of the .mzXML files
    # If the MS1 peaks don't exist, don't touch this but not sure how it works as Frank seems to store differently.
    if ms1_peaks is None:
        filepath = os.path.join(
            settings.MEDIA_ROOT,
            'frank',
            experiment_object.created_by.username,
            experiment_object.slug,
        )

    else:  # This path needs to be different for passing to method 3
        experimental_condition = ExperimentalCondition.objects.filter(experiment=experiment_object)[0]
        print "EXP " + str(experimental_condition)
        sample = Sample.objects.filter(experimental_condition=experimental_condition)[0]
        print "sample " + str(sample)
        filepath = os.path.join(
            settings.MEDIA_ROOT,
            'frank',
            experiment_object.created_by.username,
            experiment_object.slug,
            experimental_condition.slug,
            sample.slug
        )

    print (filepath)
    # Get the fragmentation set object from the database
    fragmentation_set_object = FragmentationSet.objects.get(id=fragmentation_set_id)
    # Store the source function as a variable
    r_source = robjects.r['source']
    # If no MS1 peaks were passed in, the ms1_peak parameter is set to NULL for rpy2
    if ms1_peaks is None:
        location_of_script = os.path.join(settings.BASE_DIR, 'frank', 'Frank_R', 'frankMSnPeakMatrix.R')
        r_source(location_of_script)
        r_frank_pimp_prepare = robjects.globalenv['frankMSnPeakMatrix']

    # Else there are MS1 peaks
    else:
        location_of_script = os.path.join(settings.BASE_DIR, 'frank', 'Frank_R', 'frankPimpPrepare.R')
        r_source(location_of_script)
        r_frank_pimp_prepare = robjects.globalenv['frankPimpPrepare']

    # Function of an R script if the fragments were passed from Pimp

    # Update the status of the task for the user
    fragmentation_set_object.status = 'Processing'
    fragmentation_set_object.save()

    # The script can then be run by passing the root directory of the experiment to the R script
    # The script goes through the hierarchy and finds all mzXML files for processing
    # The script should also take ms1_peaks and mzMl files when run from Pimp.

    # Find out the polarity of the file and pass in a dataframe to represent the relationship
    # This tells us which files and polarites have been added for the fragments

    file_pol_dict = {}

    polarity_vector = ms1_peaks.rx2('polarity')
    print type(polarity_vector.levels[0])
    p = polarity_vector.levels[0]  # The polarity of the MS1 peaks

    print "the polarity is " + p
    if p == "positive":
        print ("P is positive")
        pol_dir = "Positive"
    elif p == "negative":
        pol_dir = "Negative"
    else:
        print "we have a polarity issue"

    print 'Polarity = ' + str(pol_dir)
    if os.path.join(filepath, pol_dir):
        polarity_fp = os.path.join(filepath, pol_dir)
        print polarity_fp

        for f in os.listdir(polarity_fp):
            if f.endswith(".mzML"):
                path = os.path.join(polarity_fp, f)
                pol = findpolarity(path)
                if pol == "+":
                    polarity = "positive"
                elif pol is "-":
                    polarity = "negative"
                file_pol_dict[path] = polarity
            else:
                print 'no file of mzML type here'
        else:
            print 'no file of polarity' + str(p)

    print "the file polarity mapping is", file_pol_dict

    # Put dictionary into dataframe for passing to R
    df = pd.DataFrame(file_pol_dict.items(), columns=['filename', 'polarity'])
    pandas2ri.activate()
    f_pol_df = pandas2ri.py2ri(df)
    print "The polarity_dataframe is", f_pol_df

    # If no MS1 peaks, generate the peak matrix for Frank
    if ms1_peaks is None:
        output = r_frank_pimp_prepare(filepath)
    # Else there are MS1 peaks and we want to prepare the files for Method 3
    else:
        output = r_frank_pimp_prepare(filepath, ms1_peaks, f_pol_df)

    try:
        # The MSNPeakBuilder is a class which takes the output of the R script and populates the peaks
        # into the database.
        # Pass the experiment name slug in order to grab the experiment.
        peak_generator = MSNPeakBuilder(output, fragmentation_set_object.id, experiment_slug)
        # peak_generator = MSNPeakBuilder(output, fragmentation_set_object.id)
        # Each of sub class of the 'Abstract' PeakBuilder class will have the populate_database_peaks() method
        peak_generator.populate_database_peaks()
        # Upon completion the status of the fragmentation set is updated, to inform the user of completion
        fragmentation_set_object.status = 'Completed Successfully'
    # Should the addition of the peaks to the database fail, the exceptions are passed back up
    # and the status is updated.
    except ValueError as value_error:
        print value_error.message
        fragmentation_set_object.status = 'Completed with Errors'
    except TypeError as type_error:
        print type_error.message
        fragmentation_set_object.status = 'Completed with Errors'
    except ValidationError as validation_error:
        print validation_error.message
        fragmentation_set_object.status = 'Completed with Errors'
    except MultipleObjectsReturned as multiple_error:
        print multiple_error.message
        fragmentation_set_object.status = 'Completed with Errors'
    except ObjectDoesNotExist as object_error:
        print object_error.message
        fragmentation_set_object.status = 'Completed with Errors'
    fragmentation_set_object.save()
    return True


@celery.task
def massbank_batch_search(annotation_query_id):
    """
    Method to query the MassBank spectral reference library
    :param annotation_query_id: Integer id of the annotation query to be performed
    :return: True   Boolean denoting the completion of the query
    """

    # Get the annotation query object and update the status to update the user
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    # Derive the associated fragmentation set from the annotation query
    fragmentation_set = annotation_query.fragmentation_set
    try:
        # The MassBank query tool performs the formatting, sending of the query and population of the database
        mass_bank_query_tool = MassBankQueryTool(annotation_query_id, fragmentation_set.id)
        mass_bank_query_tool.get_mass_bank_annotations()
        annotation_query.status = 'Completed Successfully'
    # In order to inform the user of any errors, exceptions are raised and the status is reflected
    # to reflect the end of the process
    except WebFault as web_fault:
        print web_fault.message
        annotation_query.status = 'Completed with Errors'
    except URLError as url_error:
        print url_error.message
        annotation_query.status = 'Completed with Errors'
    except AttributeError as attribute_error:
        print attribute_error.message
        annotation_query.status = 'Completed with Errors'
    except MultipleObjectsReturned as multiple_error:
        print multiple_error.message
        annotation_query.status = 'Completed with Errors'
    except ObjectDoesNotExist as object_error:
        print object_error.message
        annotation_query.status = 'Completed with Errors'
    except ValidationError as validation_error:
        print validation_error.message
        annotation_query.status = 'Completed with Errors'
    except InvalidOperation as invalid_op:
        print invalid_op.message
        annotation_query.status = 'Completed with Errors'
    annotation_query.save()
    return True


@celery.task
def nist_batch_search(annotation_query_id):
    """
    Method to retrieve candidate annotations from the NIST spectral reference library
    :param annotation_query_id: Integer id of the annotation query to be performed
    :return: True:  Boolean indicating the completion of the task
    """

    # Get the annotation object to be performed and update the process status for the user
    print "In the Nist batch search"
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    try:
        # A NIST query tool, is used to write the query files to a temporary file, which
        # NIST uses to generate candidate annotations which are written to a temporary file
        # The NIST query tool updates the database from the NIST output file.
        nist_annotation_tool = NISTQueryTool(annotation_query_id)
        nist_annotation_tool.get_nist_annotations()
        annotation_query.status = 'Completed Successfully'
        # As before, to prevent to maintain the celery workers, any errors which cannot be resolved
        # by the NISTQueryTool are raised and the status of the task is updated.
    except IOError as io_error:
        print io_error
        annotation_query.status = 'Completed with Errors'
    except OSError as os_error:
        print os_error.message
        annotation_query.status = 'Completed with Errors'
    except ValueError as value_error:
        print value_error.message
        annotation_query.status = 'Completed with Errors'
    except MultipleObjectsReturned as multiple_error:
        print multiple_error.message
        annotation_query.status = 'Completed with Errors'
    except ObjectDoesNotExist as object_err:
        print object_err.message
        annotation_query.status = 'Completed with Errors'
    except Warning as warning:
        print warning.message
        annotation_query.status = 'Completed with Errors'
    annotation_query.save()
    print "Completed the NIST batch serach"


"""
SIRIUS details added by Karen
"""


@celery.task
def sirius_batch_search(annotation_query_id):
    print 'In batch search'

    """
    Method to retrieve candidate annotations from the NIST spectral reference library
    :param annotation_query_id: Integer id of the annotation query to be performed
    :return: True:  Boolean indicating the completion of the task
    """

    # Get the annotation object to be performed and update the process status for the user
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    # Derive the associated fragmentation set from the annotation query
    fragmentation_set = annotation_query.fragmentation_set

    try:
        print ('Print anything in tasks')
        # A SIRIUS query tool, is used to write the query files to a temporary file, which
        # SIRIUS uses to generate candidate annotations which are written to a temporary file
        # The SIRIUS query tool updates the database from the SIRIUS output file.
        sirius_annotation_tool = SIRIUSQueryTool(annotation_query_id, fragmentation_set.id)
        sirius_annotation_tool.get_sirius_annotations
        annotation_query.status = 'Completed Successfully'
        # As before, to prevent to maintain the celery workers, any errors which cannot be resolved
        # by the SIRIUSQueryTool are raised and the status of the task is updated.
    except IOError as io_error:
        print io_error
        annotation_query.status = 'Completed with Errors'
    except OSError as os_error:
        print os_error.message
        annotation_query.status = 'Completed with Errors'
    except ValueError as value_error:
        print value_error.message
        annotation_query.status = 'Completed with Errors'
    except MultipleObjectsReturned as multiple_error:
        print multiple_error.message
        annotation_query.status = 'Completed with Errors'
    except ObjectDoesNotExist as object_err:
        print object_err.message
        annotation_query.status = 'Completed with Errors'
    except Warning as warning:
        print warning.message
        annotation_query.status = 'Completed with Errors'
    annotation_query.save()
    return True


"""
The following are additions by Simon Rogers
"""
# This really should not be here! - Simon's Addition
# In both of the following, the first number is subtracted from the observed mass
# and the second number is divided
# hence the first number is the total mass gain of the adduct (including any reduction in electrons), divided by the charge
# and the second number is the reciprocal of the charge
POSITIVE_TRANSFORMATIONS = {
    "M+2H": [1.00727645199076, 0.5, 0.0],
    "M+H+NH4": [9.52055100354076, 0.5, 0.0],
    "M+H+Na": [11.99824876604076, 0.5, 0.0],
    "M+H+K": [19.98521738604076, 0.5, 0.0],
    "M+ACN+2H": [21.520551003540763, 0.5, 0.0],
    "M+2Na": [22.98922108009076, 0.5, 0.0],
    "M+H": [1.00727645199076, 1.0, 0.0],
    "M+HC13": [1.00727645199076, 1.0, -1.00335],
    "M+H2C13": [1.00727645199076, 1.0, -2.00670],
    "M+NH4": [18.03382555509076, 1.0, 0.0],
    "M+Na": [22.98922108009076, 1.0, 0.0],
    "M+NaC13": [22.98922108009076, 1.0, -1.00335],
    "M+CH3OH+H": [33.033491201890754, 1.0, 0.0],
    "M+K": [38.963158320090756, 1.0, 0.0],
    "M+KC13": [38.963158320090756, 1.0, -1.00335],
    "M+ACN+H": [42.03382555509076, 1.0, 0.0],
    "M+2Na-H": [44.97116570819076, 1.0, 0.0],
    "M+IsoProp+H": [61.06479132949075, 1.0, 0.0],
    "M+ACN+Na": [64.01577018319077, 1.0, 0.0],
    "M+2K-H": [76.91904018819076, 1.0, 0.0],
    "M+DMSO+H": [79.02121199569076, 1.0, 0.0],
    "M+2ACN+H": [83.06037465819077, 1.0, 0.0],
}
# TODO: add some more of these
NEGATIVE_TRANSFORMATIONS = {
    "M-H": [-1.00727645199076, 1.0, 0.0],
    "M-2H": [-1.00727645199076, 0.5, 0.0],
}


@celery.task
def precursor_mass_filter(annotation_query_id):
    # Runs a filter on the annotations
    import math
    print 'In the precursor mass-filter tool'
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()

    parameters = jsonpickle.decode(annotation_query.annotation_tool_params)
    parent_annotation_queries = AnnotationQuery.objects.filter(slug__in=parameters['parents'])
    positive_transforms_to_use = parameters['positive_transforms']
    negative_transforms_to_use = parameters['negative_transforms']
    mass_tol = parameters['mass_tol']

    fragmentation_set = annotation_query.fragmentation_set
    peaks = Peak.objects.filter(fragmentation_set=fragmentation_set,
                                msn_level=1, source_file__polarity='Positive')
    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak, annotation_query__in=parent_annotation_queries)
        for a in peak_annotations:
            for t in positive_transforms_to_use:
                transformed_mass = (float(peak.mass) - POSITIVE_TRANSFORMATIONS[t][0]) / POSITIVE_TRANSFORMATIONS[t][
                    1] + POSITIVE_TRANSFORMATIONS[t][2]
                mass_error = 1e6 * math.fabs(transformed_mass - float(a.compound.exact_mass)) / transformed_mass
                if mass_error < mass_tol:
                    new_annotation = CandidateAnnotation(peak=peak,
                                                         annotation_query=annotation_query, compound=a.compound,
                                                         mass_match=True, confidence=a.confidence,
                                                         difference_from_peak_mass=peak.mass - a.compound.exact_mass,
                                                         adduct=t,
                                                         instrument_type=a.instrument_type,
                                                         collision_energy=a.collision_energy,
                                                         additional_information=a.additional_information)
                    new_annotation.save()

    peaks = Peak.objects.filter(fragmentation_set=fragmentation_set,
                                msn_level=1, source_file__polarity='Negative')
    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak, annotation_query__in=parent_annotation_queries)
        for a in peak_annotations:
            for t in negative_transforms_to_use:
                transformed_mass = (float(peak.mass) - NEGATIVE_TRANSFORMATIONS[t][0]) / NEGATIVE_TRANSFORMATIONS[t][
                    1] + NEGATIVE_TRANSFORMATIONS[t][2]
                mass_error = 1e6 * math.fabs(transformed_mass - float(a.compound.exact_mass)) / transformed_mass
                if mass_error < mass_tol:
                    new_annotation = CandidateAnnotation(peak=peak,
                                                         annotation_query=annotation_query, compound=a.compound,
                                                         mass_match=True, confidence=a.confidence,
                                                         difference_from_peak_mass=peak.mass - a.compound.exact_mass,
                                                         adduct=t,
                                                         instrument_type=a.instrument_type,
                                                         collision_energy=a.collision_energy,
                                                         additional_information=a.additional_information)
                    new_annotation.save()

    annotation_query.status = "Completed Successfully"
    annotation_query.save()
    print "At the end of the Precursor tool, saved,"


"""
End of additions by Simon Rogers
"""


@celery.task
def clean_filter(annotation_query_id, user):
    # This cleans a set of annotations by only keeping one annotation for each compound for each peak
    # and only keeping annotations above a threshold
    # the highest confidence annotation (abover the threshold) is set as the preferred annotation)
    print ("In the clean filter tool")
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    parameters = jsonpickle.decode(annotation_query.annotation_tool_params)
    parent_annotation_queries = AnnotationQuery.objects.filter(slug__in=parameters['parents'])
    preferred_threshold = parameters['preferred_threshold']

    # Following does nothing yet
    delete_original = parameters['delete_original']

    # Following is true if the user wants the preferred annotations set
    do_preferred = parameters['do_preferred']

    # Following is true if we should collapse multiple instances of the same compound
    collapse_multiple = parameters['collapse_multiple']

    fragmentation_set = annotation_query.fragmentation_set
    peaks = Peak.objects.filter(fragmentation_set=fragmentation_set,
                                msn_level=1)

    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak, annotation_query__in=parent_annotation_queries)
        found_compounds = {}
        best_annotation = None
        for annotation in peak_annotations:
            if annotation.compound in found_compounds:
                this_annotation = found_compounds[annotation.compound]
                if annotation.confidence > this_annotation.confidence:
                    this_annotation.confidence = annotation.confidence
                    this_annotation.instrument_type = annotation.instrument_type
                    this_annotation.collision_energy = annotation.collision_energy
                    this_annotation.save()
                    print "Saving preferred annotation"
                    if this_annotation.confidence > best_annotation.confidence:
                        best_annotation = this_annotation

            else:
                if annotation.confidence > preferred_threshold:
                    new_annotation = CandidateAnnotation(peak=peak,
                                                         annotation_query=annotation_query,
                                                         compound=annotation.compound,
                                                         mass_match=annotation.mass_match,
                                                         confidence=annotation.confidence,
                                                         difference_from_peak_mass=peak.mass - annotation.compound.exact_mass,
                                                         adduct=annotation.adduct,
                                                         instrument_type=annotation.instrument_type,
                                                         collision_energy=annotation.collision_energy)
                    new_annotation.save()
                    if collapse_multiple:
                        found_compounds[annotation.compound] = new_annotation
                    if best_annotation == None:
                        best_annotation = new_annotation
                    else:
                        if new_annotation.confidence > best_annotation.confidence:
                            best_annotation = new_annotation
        if do_preferred:
            peak.preferred_candidate_annotation = best_annotation
            peak.preferred_candidate_description = "Added automatically with annotation query {} with threshold of {}".format(
                annotation_query.name, preferred_threshold)
            peak.preferred_candidate_user_selector = user
            peak.preferred_candidate_updated_date = datetime.datetime.now()
            peak.save()

    annotation_query.status = 'Completed Successfully'
    annotation_query.save()
    print ("At the end of the clean filter tool")


@celery.task
def gcms_generate_peak_list(experiment_name_slug, fragmentation_set_id):
    """
    Method to derive peak data from GCMS peak data from a collection of source files
    :param experiment_name_slug: Integer id for the experiment
    :param fragmentation_set_id:    Integer id for the fragmentation set
    :return:True    Boolean indicating the completion of the task
    """

    # Get the fragmentation set object corresponding to the id
    fragmentation_set = FragmentationSet.objects.get(id=fragmentation_set_id)
    # Update the status of the set
    fragmentation_set.status = 'Processing'
    fragmentation_set.save()
    # Obtain the experiment corresponding to the id
    experiment_object = Experiment.objects.get(slug=experiment_name_slug)
    # From the experiment object derive the file directory of the .mzXML files
    filepath = os.path.join(
        settings.MEDIA_ROOT,
        'frank',
        experiment_object.created_by.username,
        experiment_object.slug,
    )
    # Store the source function
    r_source = robjects.r['source']
    # Derive the source of the GCMS R script from the local install
    location_of_script = os.path.join(settings.BASE_DIR, 'frank', 'Frank_R', 'gcmsGeneratePeakList.R')
    # The script is then sourced in R
    r_source(location_of_script)
    # Then store the function for extracting the peak data
    r_generate_gcms_peak_matrix = robjects.globalenv['generateGCMSPeakMatrix']
    output = r_generate_gcms_peak_matrix(input_directory=filepath)
    try:
        # The peak generator takes the R dataframe output of the R script and populates the database
        # from the peak list
        peak_generator = GCMSPeakBuilder(output, fragmentation_set.id)
        peak_generator.populate_database_peaks()
        # Finally, update the status of the process for display to the user
        fragmentation_set.status = 'Completed Successfully'
    except IOError as io_error:
        print io_error.message
        fragmentation_set.status = 'Completed with Errors'
    except TypeError as type_error:
        print type_error.message
        fragmentation_set.status = 'Completed with Errors'
    except ValueError as value_error:
        print value_error.message
        fragmentation_set.status = 'Completed with Errors'
    except InvalidOperation as invalid_op_error:
        print invalid_op_error.message
        fragmentation_set.status = 'Completed with Errors'
    except ValidationError as validation_error:
        print validation_error.message
        fragmentation_set.status = 'Completed with Errors'
    except MultipleObjectsReturned as multiple_error:
        print multiple_error.message
        fragmentation_set.status = 'Completed with Errors'
    fragmentation_set.save()
    return True


@celery.task
def run_ms2lda_analysis(annotation_query_id):
    """
    Method to run a Mass2LDA analysis.
        - read MS1 peaks from database
        - read MS2 peaks from database
        - create MS2 Intensity Matrix
        - save data into ms2lda object
        - run an LDA analysis on the data
        - run thresholding on the data
	- save the project file so that visualisation can be done at a later stage
          for this annotation query
    """

    # get the parameters specified on the mass2lda form (saved in the annotation query object)
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    parameters = jsonpickle.decode(annotation_query.annotation_tool_params)

    minimal_ms1_intensity = parameters['minimal_ms1_intensity']
    minimal_ms2_intensity = parameters['minimal_ms2_intensity']
    min_ms1_retention_time = parameters['min_ms1_retention_time']
    max_ms1_retention_time = parameters['max_ms1_retention_time']
    grouping_tol = parameters['grouping_tol']
    scaling_factor = parameters['scaling_factor']
    polarity = parameters['polarity']
    alpha_model_parameter = parameters['alpha_model_parameter']
    beta_model_parameter = parameters['beta_model_parameter']
    gibbs_sampling_number = parameters['gibbs_sampling_number']
    mass2motif_count = parameters['mass2motif_count']

    ms2lda_dir = os.environ['HOME'] + "/ms2lda_data/"  # directory to hold mass2lda project files

    annotation_query.status = 'Processing'
    annotation_query.save()

    # extract the fragmentation set details (as specified in the annotation query) from the database
    frag_set = annotation_query.fragmentation_set

    # extract the ms1 peak objects
    print "Extracting ms1_peaks and inserting into dataframe ..."
    ms1_peaks = Peak.objects.filter(fragmentation_set=frag_set, msn_level=1, source_file__polarity=polarity)

    # place ms1 data into a dataframe
    col_names = ['peakID', 'MSnParentPeakID', 'msLevel', 'rt', 'mz', 'intensity']
    row_names = []
    ms1_peakdata = []
    for peak in ms1_peaks:
        ms1_peakdata.append({'peakID': peak.id, 'MSnParentPeakID': 0, \
                             'msLevel': peak.msn_level, 'rt': peak.retention_time, \
                             'mz': peak.mass, 'intensity': peak.intensity})
        row_names.append(peak.id)
    ms1_df = pd.DataFrame(ms1_peakdata, index=row_names, columns=col_names, dtype='float')
    print "\tms1_df.shape = ", ms1_df.shape

    # extract the ms2 peak objects
    print "Extracting ms2_peaks and inserting into dataframe ..."
    ms2_peaks = Peak.objects.filter(fragmentation_set=frag_set, msn_level=2)

    # place ms2 data into a dataframe
    col_names = ['peakID', 'MSnParentPeakID', 'msLevel', 'rt', 'mz', 'intensity']
    row_names = []
    ms2_peakdata = []
    for peak in ms2_peaks:
        ms2_peakdata.append({'peakID': peak.id, 'MSnParentPeakID': peak.parent_peak.id, \
                             'msLevel': peak.msn_level, 'rt': peak.retention_time, \
                             'mz': peak.mass, 'intensity': peak.intensity})
        # (Note: MSnParentPeakID is the object of the parent peak)
        row_names.append(peak.id)
    ms2_df = pd.DataFrame(ms2_peakdata, index=row_names, columns=col_names, dtype='float')
    print "\tms2_df.shape = ", ms2_df.shape

    # Now need to generate the MS2 Intensity matrix.
    # Matrix column will be the MS1 peak value (i.e. Documents)
    # Matrix rows will be to MS2 masses/fragments (i.e. Words)

    # first need to order the MS2 dataframe by intensities into descending order
    print "Sorting MS2 data ..."
    sorted_ms2_df = ms2_df.copy(deep=True)
    sorted_ms2_df.sort(['intensity'], ascending=False, inplace=True)

    # calculate MS2 fragment(Word) values
    print "Calculating MS2 fragment values ..."
    unique_masses = []
    mass_id = []
    mass = sorted_ms2_df['mz'].tolist()
    for m in mass:
        # check for previous
        previous_pos = [i for i, a in enumerate(unique_masses) if (abs(m - a) / m) * 1e6 < grouping_tol]
        if len(previous_pos) == 0:
            # it's a new one
            unique_masses.append(m)
            mass_id.append(len(unique_masses) - 1)
        else:
            # it's an old one
            mass_id.append(previous_pos[0])

    # add an extra column to the MS2 peak dataframe - will hold the MS2 fragment(word)
    # that the MS2 peak should be stored in
    n_peaks = len(mass)
    frag_col = []
    for n in range(n_peaks):
        frag_col.append(unique_masses[mass_id[n]])  # held as a float
    sorted_ms2_df['fragment_bin_id'] = frag_col  # add the new column
    sorted_ms2_df['loss_bin_id'] = 0  # add a placeholder for loss column
    # otherwise plot method will fail

    # populate the ms2 intensity matrix
    print "Populating the ms2 intensity matrix ..."
    intensity_dmat = np.zeros((len(unique_masses), len(ms1_df.index)))
    unique_masses.sort()  # sort the fragments into ascending order
    for i, ms1 in enumerate(ms1_df.index.tolist()):
        ms2_rows = sorted_ms2_df.loc[sorted_ms2_df['MSnParentPeakID'] == ms1] \
            # all ms2 children for the ms1
        ms2_intensities = np.array(ms2_rows['intensity'].tolist()) \
            # all ms2 intensities for this ms1
        ms2_fragments = np.array(ms2_rows['fragment_bin_id'].tolist()) \
            # .. and the fragment bins they go in

        # add each ms2 intensity associated with this ms1 to the dmat
        # (normalise and floor first ...)

        word_counts = ms2_intensities / max(ms2_intensities) * scaling_factor
        word_counts = np.floor(word_counts)

        for j, ms2 in enumerate(word_counts):
            intensity_dmat[unique_masses.index(ms2_fragments[j]), i] = ms2

    # create a dataframe holding intensity of ms2 peaks for a given ms1 peak
    # column - ms1 peaks, label=mz_rt_peakID
    # rows - ms2 fragment, label=fragment_<frag>
    print "Creating intensity_df ..."
    row_names = ['fragment_' + str(round(x, 5)) for x in unique_masses]
    col_names = []
    for i, row in ms1_df.iterrows():
        mz = str(round(row['mz'], 5))
        rt = str(row['rt'])
        peak_ID = str(int(row['peakID']))
        col_names.append(mz + '_' + rt + '_' + peak_ID)
    # copy the data into pandas dataframe
    intensity_df = pd.DataFrame(intensity_dmat, index=row_names, columns=col_names)
    intensity_df = intensity_df.transpose()
    print "\tintensity_df.shape = ", intensity_df.shape

    # saving off project data in ms2lda object
    vocab = intensity_df.columns.values
    input_filenames = []
    ms2lda = Ms2Lda(intensity_df, vocab, ms1_df, sorted_ms2_df, input_filenames, mass2motif_count, 2)

    # run lda analysis
    # n_topics = 300		** now uses mass2motif_count parameter
    n_samples = 3
    n_burn = 0
    n_thin = 1
    # alpha = 50.0/n_topics      **now uses parameter entered on the screen**
    # beta = 0.1                 **now uses parameter entered on the screen**
    print "Running LDA anaylysis ..."
    ms2lda.run_lda(mass2motif_count, n_samples, n_burn, n_thin, float(alpha_model_parameter),
                   float(beta_model_parameter))

    print "\nRunning thresholding ..."
    ms2lda.do_thresholding(th_doc_topic=0.05, th_topic_word=0.01)

    # need to convert following columns to str
    ms2lda.ms2['fragment_bin_id'] = ms2lda.ms2['fragment_bin_id'].round(5)
    ms2lda.ms2['fragment_bin_id'] = ms2lda.ms2['fragment_bin_id'].astype(str)  # covert to str
    ms2lda.ms2['loss_bin_id'] = ms2lda.ms2['loss_bin_id'].astype(str)  # covert to str

    # save the project off to the relevant directory so that it can be read from the visualisation
    # first check if relevant directory exists - if not then create it.
    if not os.path.isdir(ms2lda_dir):
        os.makedirs(ms2lda_dir)
    ms2lda.save_project(ms2lda_dir + "ms2lda_" + str(annotation_query_id) + ".project")

    annotation_query.status = 'Completed Successfully'
    annotation_query.save()


@celery.task
def simple_pimp_frank_linker(pimp_analysis_id, frank_fragmentation_set_id, mass_tolerance, rt_tolerance, link_id):
    print "RUNNING PiMP <-> FrAnK LINKER"
    pimp_analysis = PimpAnalysis.objects.get(id=pimp_analysis_id)
    fragmentation_set = FragmentationSet.objects.get(id=frank_fragmentation_set_id)

    # Get the PiMP peaks
    dataset = Dataset.objects.get(analysis=pimp_analysis)
    peaks = PimpPeak.objects.filter(dataset=dataset)

    # Delete any previous links for these peaks
    for peak in peaks:
        link = PimpFrankPeakLink.objects.filter(pimp_peak=peak)
        for l in link:
            l.delete()

    # Get the frank peaks
    positive_frank_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set, source_file__polarity='Positive')
    negative_frank_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set, source_file__polarity='Negative')

    print "Extracted {} positive and {} negative peaks from Frank".format(len(positive_frank_peaks),
                                                                          len(negative_frank_peaks))

    n_links = 0
    for i, peak in enumerate(peaks):
        if peak.polarity == 'positive':
            in_range = [fp for fp in positive_frank_peaks if hit(peak, fp, mass_tolerance, rt_tolerance)]
        else:
            in_range = [fp for fp in negative_frank_peaks if hit(peak, fp, mass_tolerance, rt_tolerance)]
        if len(in_range) > 0:
            if len(in_range) == 1:
                top_hit = in_range[0]
            else:
                # Find the closest
                top_hit = None
                closest_mass_diff = 1e6
                for p in in_range:
                    mass_diff = abs(peak.mass - fp.mass)
                    if mass_diff < closest_mass_diff:
                        top_hit = p
                        closest_mass_diff = mass_diff
            print "Found link PiMP: {} <--> {} FrAnK ({} of {})".format(peak.mass, top_hit.mass, i, len(peaks))
            n_links += 1
            PimpFrankPeakLink.objects.create(frank_peak=top_hit, pimp_peak=peak)

    print "Finished linking, found {} links".format(n_links)
    link_object = PimpAnalysisFrankFs.objects.get(id=link_id)
    link_object.status = 'Complete'
    link_object.save()


def hit(pimp_peak, frank_peak, masstol, rttol):
    pimp_mass = float(pimp_peak.mass)
    frank_mass = float(frank_peak.mass)
    if abs(frank_peak.retention_time - pimp_peak.rt) < rttol:
        if 1e6 * abs(frank_mass - pimp_mass) / frank_mass < masstol:
            return True
        else:
            return False
