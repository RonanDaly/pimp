__author__ = "Scott Greig"

import rpy2.robjects as robjects
from pimp.settings_dev import MEDIA_ROOT
from frank.models import Peak, SampleFile, CandidateAnnotation, Compound, AnnotationTool,\
    CompoundAnnotationTool, FragmentationSet, Experiment, AnnotationQuery
from djcelery import celery
from decimal import *
from frank.peakFactories import MSNPeakBuilder, GCMSPeakBuilder
from suds.client import WebFault
import os
from frank.models import *
import frank.network_sampler as ns
from pimp.settings_dev import BASE_DIR
import jsonpickle
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from frank.annotationTools import MassBankQueryTool, NISTQueryTool
from urllib2 import URLError
import datetime


@celery.task
def runNetworkSampler(fragmentation_set_slug, sample_file_name, annotation_query_slug):
    """
    Method to run the Network Sampler developed by Simon Rogers
    :author Simon Rogers
    :param fragmentation_set_slug: A string containing the unique slug for the fragmentation set
    :param sample_file_name: A string for the sample file name
    :param annotation_query_slug: A string containing the unique slug for the annotation query
    :return: edge_dict:
    """

    # fragmentation set is the fragmentation set we want to run the analysis on (slug)
    # annotation_query is the new annotation query slug
    fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_slug)
    new_annotation_query = AnnotationQuery.objects.get(slug=annotation_query_slug)
    parent_annotation_query = new_annotation_query.parent_annotation_query
    sample_file = SampleFile.objects.filter(name=sample_file_name)
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
    peaks = Peak.objects.filter(fragmentation_set=fragmentation_set, msn_level=1, source_file=sample_file)
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
            compound = Compound.objects.get(id=annotation.id)
            parent_annotation = CandidateAnnotation.objects.get(id=annotation.parentid)
            add_info_string = "Prior: {:5.4f}, Edges: {:5.2f}".format(peakset.prior_probability[m][annotation],peakset.posterior_edges[m][annotation])
            an = CandidateAnnotation.objects.create(compound=compound, peak=peak, confidence=peakset.posterior_probability[m][annotation],
                annotation_query=new_annotation_query, difference_from_peak_mass=parent_annotation.difference_from_peak_mass,
                mass_match=parent_annotation.mass_match, additional_information=add_info_string)

    edge_dict = sampler.global_edge_count()
    new_annotation_query.status = 'Completed'
    new_annotation_query.save()
    return edge_dict


@celery.task
def msn_generate_peak_list(experiment_slug, fragmentation_set_id):

    """
    Method to extract peak data from a collection of sample files
    :param experiment_slug: Integer id of the experiment from which the files orginate
    :param fragmentation_set_id:    Integer id of the fragmentation set to be populated
    :return: True   Boolean value denoting the completion of the task
    """

    # Determine the directory of the experiment
    experiment_object = Experiment.objects.get(slug=experiment_slug)
    # From the experiment object derive the file directory of the .mzXML files
    filepath = os.path.join(
        MEDIA_ROOT,
        'frank',
        experiment_object.created_by.username,
        experiment_object.slug,
    )
    # Get the fragmentation set object from the database
    fragmentation_set_object = FragmentationSet.objects.get(id=fragmentation_set_id)
    # Store the source function as a variable
    r_source = robjects.r['source']
    # Derive the location of the R script based on the local directory
    location_of_script = os.path.join(BASE_DIR, 'frank', 'Frank_R', 'frankMSnPeakMatrix.R')
    # Source the script in R
    r_source(location_of_script)
    # Store the function of the R script ('frankMSNPeakMatrix') as a variable
    r_frank_msn_peak_matrix = robjects.globalenv['frankMSnPeakMatrix']
    # Update the status of the task for the user
    fragmentation_set_object.status = 'Processing'
    fragmentation_set_object.save()
    # The script can then be run by passing the root directory of the experiment to the R script
    # The script goes through the hierarchy and finds all mxXML files for processing
    output = r_frank_msn_peak_matrix(source_directory=filepath)
    try:
        # The MSNPeakBuilder is a class which takes the output of the R script and populates the peaks
        # into the database.
        peak_generator = MSNPeakBuilder(output, fragmentation_set_object.id)
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


"""
The following are additions by Simon Rogers
"""
# This really should not be here! - Simon's Addition
# In both of the following, the first number is subtracted from the observed mass
# and the second number is divided
# hence the first number is the total mass gain of the adduct (including any reduction in electrons), divided by the charge
# and the second number is the reciprocal of the charge
POSITIVE_TRANSFORMATIONS = {
    "M+2H": [1.00727645199076,0.5,0.0],
    "M+H+NH4": [9.52055100354076,0.5,0.0],
    "M+H+Na": [11.99824876604076,0.5,0.0],
    "M+H+K": [19.98521738604076,0.5,0.0],
    "M+ACN+2H": [21.520551003540763,0.5,0.0],
    "M+2Na": [22.98922108009076,0.5,0.0],
    "M+H": [1.00727645199076,1.0,0.0],
    "M+HC13": [1.00727645199076,1.0,-1.00335],
    "M+H2C13": [1.00727645199076,1.0,-2.00670],
    "M+NH4": [18.03382555509076,1.0,0.0],
    "M+Na": [22.98922108009076,1.0,0.0],
    "M+NaC13": [22.98922108009076,1.0,-1.00335],
    "M+CH3OH+H": [33.033491201890754,1.0,0.0],
    "M+K": [38.963158320090756,1.0,0.0],
    "M+KC13": [38.963158320090756,1.0,-1.00335],
    "M+ACN+H": [42.03382555509076,1.0,0.0],
    "M+2Na-H": [44.97116570819076,1.0,0.0],
    "M+IsoProp+H": [61.06479132949075,1.0,0.0],
    "M+ACN+Na": [64.01577018319077,1.0,0.0],
    "M+2K-H": [76.91904018819076,1.0,0.0],
    "M+DMSO+H": [79.02121199569076,1.0,0.0],
    "M+2ACN+H": [83.06037465819077,1.0,0.0],
}
# TODO: add some more of these
NEGATIVE_TRANSFORMATIONS = {
    "M-H": [-1.00727645199076,1.0,0.0],
    "M-2H": [-1.00727645199076,0.5,0.0],
}

@celery.task
def precursor_mass_filter(annotation_query_id):
    # Runs a filter on the annotations 
    import math
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()

    parameters = jsonpickle.decode(annotation_query.annotation_tool_params)
    parent_annotation_queries = AnnotationQuery.objects.filter(slug__in=parameters['parents'])
    positive_transforms_to_use = parameters['positive_transforms']
    negative_transforms_to_use = parameters['negative_transforms']
    mass_tol = parameters['mass_tol']

    fragmentation_set = annotation_query.fragmentation_set
    peaks = Peak.objects.filter(fragmentation_set = fragmentation_set,
        msn_level = 1, source_file__polarity='Positive')
    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak,annotation_query__in=parent_annotation_queries)
        for a in peak_annotations:
            for t in positive_transforms_to_use:
                transformed_mass = (float(peak.mass) - POSITIVE_TRANSFORMATIONS[t][0])/POSITIVE_TRANSFORMATIONS[t][1] + POSITIVE_TRANSFORMATIONS[t][2]
                mass_error = 1e6*math.fabs(transformed_mass - float(a.compound.exact_mass))/transformed_mass
                if mass_error < mass_tol:
                    new_annotation = CandidateAnnotation(peak = peak,
                        annotation_query = annotation_query,compound = a.compound,
                        mass_match = True, confidence = a.confidence, 
                        difference_from_peak_mass = peak.mass - a.compound.exact_mass , adduct = t,
                        instrument_type = a.instrument_type, collision_energy = a.collision_energy)
                    new_annotation.save()

    peaks = Peak.objects.filter(fragmentation_set = fragmentation_set,
        msn_level = 1, source_file__polarity='Negative')
    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak,annotation_query__in=parent_annotation_queries)
        for a in peak_annotations:
            for t in negative_transforms_to_use:
                transformed_mass = (float(peak.mass) - NEGATIVE_TRANSFORMATIONS[t][0])/NEGATIVE_TRANSFORMATIONS[t][1] + NEGATIVE_TRANSFORMATIONS[t][2]
                mass_error = 1e6*math.fabs(transformed_mass - float(a.compound.exact_mass))/transformed_mass
                if mass_error < mass_tol:
                    new_annotation = CandidateAnnotation(peak = peak,
                        annotation_query = annotation_query,compound = a.compound,
                        mass_match = True, confidence = a.confidence, 
                        difference_from_peak_mass = peak.mass - a.compound.exact_mass , adduct = t,
                        instrument_type = a.instrument_type, collision_energy = a.collision_energy)
                    new_annotation.save()

    annotation_query.status="Completed Successfully"
    annotation_query.save()

"""
End of additions by Simon Rogers
"""


@celery.task
def clean_filter(annotation_query_id,user):
    # This cleans a set of annotations by only keeping one annotation for each compound for each peak
    # and only keeping annotations above a threshold
    # the highest confidence annotation (abover the threshold) is set as the preferred annotation)
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    parameters = jsonpickle.decode(annotation_query.annotation_tool_params)
    parent_annotation_queries = AnnotationQuery.objects.filter(slug__in=parameters['parents'])
    preferred_threshold = parameters['preferred_threshold']

    # Following does nothing yet
    delete_original = parameters['delete_original']

    fragmentation_set = annotation_query.fragmentation_set
    peaks = Peak.objects.filter(fragmentation_set = fragmentation_set,
        msn_level = 1)

    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak,annotation_query__in=parent_annotation_queries)
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
                    if this_annotation.confidence > best_annotation.confidence:
                        best_annotation = this_annotation

            else:
                if annotation.confidence > preferred_threshold:
                    new_annotation = CandidateAnnotation(peak = peak,
                        annotation_query = annotation_query,compound = annotation.compound,
                        mass_match = annotation.mass_match , confidence = annotation.confidence, 
                        difference_from_peak_mass = peak.mass - annotation.compound.exact_mass , adduct = annotation.adduct,
                        instrument_type = annotation.instrument_type, collision_energy = annotation.collision_energy)
                    new_annotation.save()
                    found_compounds[annotation.compound] = new_annotation
                    if best_annotation == None:
                        best_annotation = new_annotation
                    else:
                        if new_annotation.confidence > best_annotation.confidence:
                            best_annotation = new_annotation
        peak.preferred_candidate_annotation = best_annotation
        peak.preferred_candidate_description = "Added automatically with annotation query {} with threshold of {}".format(annotation_query.name,preferred_threshold)
        peak.preferred_candidate_user_selector = user
        peak.preferred_candidate_updated_date = datetime.datetime.now()
        peak.save()

        annotation_query.status = 'Completed Successfully'
        annotation_query.save()



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
        MEDIA_ROOT,
        'frank',
        experiment_object.created_by.username,
        experiment_object.slug,
    )
    # Store the source function
    r_source = robjects.r['source']
    # Derive the source of the GCMS R script from the local install
    location_of_script = os.path.join(BASE_DIR, 'frank', 'Frank_R', 'gcmsGeneratePeakList.R')
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
