import rpy2.robjects as robjects
from pimp.settings_dev import MEDIA_ROOT
from frank.models import Peak, SampleFile, CandidateAnnotation, Compound, AnnotationTool,\
    CompoundAnnotationTool, FragmentationSet, Experiment, AnnotationQuery
from djcelery import celery
from decimal import *
from frank.peakFactories import MSNPeakBuilder, GCMSPeakBuilder
from suds.client import Client, WebFault
import os
from frank.models import *
import frank.network_sampler as ns
from pimp.settings_dev import BASE_DIR
import jsonpickle
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from frank.annotationTools import MassBankQueryTool, NISTQueryTool


from celery import shared_task
import subprocess

## Method to run simon's network sampler
@celery.task
def runNetworkSampler(fragmentation_set_slug, sample_file_name, annotation_query_slug):
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
    location_of_script = os.path.join(BASE_DIR, 'frank', 'Frank_R', 'frankMSnPeakMatrix.R')
    r_source(location_of_script)
    r_frankMSnPeakMatrix = robjects.globalenv['frankMSnPeakMatrix']
    fragmentation_set_object.status = 'Processing'
    fragmentation_set_object.save()
    output = r_frankMSnPeakMatrix(source_directory = filepath)
    peak_generator = None
    try:
        peak_generator = MSNPeakBuilder(output, fragmentation_set_object.id)
        peak_generator.populate_database_peaks()
        fragmentation_set_object.status = 'Completed Successfully'
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


# Method to batch query the mass bank annotation tool using SOAP
@celery.task
def massBank_batch_search(annotation_query_id):
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    fragmentation_set = annotation_query.fragmentation_set
    try:
        mass_bank_query_tool = MassBankQueryTool(annotation_query_id, fragmentation_set.id)
        mass_bank_query_tool.get_mass_bank_annotations()
        annotation_query.status = 'Completed Successfully'
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
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()
    try:
        nist_annotation_tool = NISTQueryTool(annotation_query_id)
        nist_annotation_tool.get_nist_annotations()
        annotation_query.status = 'Completed Successfully'
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

# This really should not be here!
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

@celery.task
def precursor_mass_filter(annotation_query_id):
    import math
    annotation_query = AnnotationQuery.objects.get(id=annotation_query_id)
    annotation_query.status = 'Processing'
    annotation_query.save()

    parameters = jsonpickle.decode(annotation_query.annotation_tool_params)
    parent_annotation_queries = AnnotationQuery.objects.filter(slug__in=parameters['parents'])
    print parent_annotation_queries
    transforms_to_use = parameters['positive_transforms']
    mass_tol = parameters['mass_tol']

    print "Running precursor mass filter with adducts: ",transforms_to_use

    fragmentation_set = annotation_query.fragmentation_set
    peaks = Peak.objects.filter(fragmentation_set = fragmentation_set,
        msn_level = 1, source_file__polarity='Positive')
    for peak in peaks:
        peak_annotations = CandidateAnnotation.objects.filter(peak=peak,annotation_query__in=parent_annotation_queries)
        for a in peak_annotations:
            for t in transforms_to_use:
                transformed_mass = (float(peak.mass) - POSITIVE_TRANSFORMATIONS[t][0])/POSITIVE_TRANSFORMATIONS[t][1] + POSITIVE_TRANSFORMATIONS[t][2]
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
            



@celery.task
def gcmsGeneratePeakList(experiment_name_slug, fragmentation_set_id):
    fragmentation_set = FragmentationSet.objects.get(id = fragmentation_set_id)
    fragmentation_set.status = 'Processing'
    fragmentation_set.save()
    experiment_object = Experiment.objects.get(slug = experiment_name_slug)
    # From the experiment object derive the file directory of the .mzXML files
    filepath = os.path.join(MEDIA_ROOT,
                            'frank',
                            experiment_object.created_by.username,
                            experiment_object.slug,
                            )
    r_source = robjects.r['source']
    location_of_script = os.path.join(BASE_DIR, 'frank', 'Frank_R', 'gcmsGeneratePeakList.R')
    r_source(location_of_script)
    r_generateGCMSPeakMatrix = robjects.globalenv['generateGCMSPeakMatrix']
    output = r_generateGCMSPeakMatrix(input_directory = filepath)
    try:
        peak_generator = GCMSPeakBuilder(output, fragmentation_set.id)
        peak_generator.populate_database_peaks()
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
    return