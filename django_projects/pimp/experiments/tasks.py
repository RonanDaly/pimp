from djcelery import celery
from celery.result import AsyncResult
from celery import chain
#from celery.utils.log import get_task_logger

import os
import subprocess
import sys
import pandas as pd
from rpy2.robjects import pandas2ri
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import connection
from djcelery import celery

from compound.models import logging, Compound, RepositoryCompound, DataSourceSuperPathway, CompoundPathway
from data.models import Analysis, Dataset, Peak, Comparison, PeakDtComparison, Sample, PeakDTSample, CalibrationSample, PeakQCSample
from experiments.pimpxml_parser.pimpxml_parser import Xmltree
from experiments.pipelines.pipeline_rpy2 import Rpy2Pipeline


from frank.models import PimpAnalysisFrankFs, AnnotationQuery
from frank.views import input_peak_list_to_database_signature
from frank.tasks import run_default_annotations
logger = logging.getLogger(__name__)
#logger = get_task_logger(__name__)


@celery.task
def error_handler(task_id, analysis, project, user, success):
    result = AsyncResult(task_id)
    print "We are in the celery error handler routine and running end of pipeline as failed"
    print "The traceback result: %s", result.traceback
    end_pimp_pipeline(analysis, project, user, success)

#@celery.task
def run_frags(pimp_analysis, frank_expt, fragmentation_set):

    #Get dataframe of ms1 peaks
    df = get_ms1_df(pimp_analysis)

    print "The dataframe is", df

    populate_tasks = []

    # Get the polarities for the MS1 peaks and for each polarity add the peak processing to the chain.
    polarities = df.polarity.unique()
    for p in polarities:
        df_pol = df[df.polarity == p]
        pandas2ri.activate()
        ms1_df_pol = pandas2ri.py2ri(df_pol)

        # Append to the celery_tasks peaks extraction for the fragmentation files using Frank and the ms1 peaks
        populate_tasks.append(input_peak_list_to_database_signature(frank_expt.slug, fragmentation_set.slug, ms1_df_pol))

    return chain(populate_tasks)

def populate_database(xml_file_path):

    compound_id_map = {}
    print "Database population started!"
    xmltree = Xmltree(xml_file_path)
    anaysis_id = xmltree.getAnalysisId()
    print anaysis_id
    analysis = Analysis.objects.get(id=anaysis_id)
    dataset = Dataset(analysis=analysis)
    dataset.save()

    bp_regex = re.compile('^potential bp$|^bp$')  # Create a regex to match peaks with type base peak (bp) and potential bp

    ############ Create a dataset instance here ##################
    peakSecondaryId = 1
    for peak_element in xmltree.getPeaks():
        ################# Create peak instance here using peakInfo and peakSecondaryId, attach it to the dataset created above #################
        peakInfo = xmltree.getPeakInfoFromElement(peak_element)
        # Select only base peaks (that have a type BP)
        if bp_regex.match(peakInfo['peak_type']):
            peak = Peak(dataset=dataset, secondaryId=peakSecondaryId, mass=peakInfo["mass"],
                    rt=peakInfo["retention_time"], polarity=peakInfo["polarity"], type=peakInfo["peak_type"])
            peak.save()

            # compoundIds = xmltree.getCompoundIds(i)
            compounds = xmltree.getCompoundsFromElement(peak_element)
            if compounds:
                compound_secondary_id_list = set()
                for compound_element in compounds:
                    ################# Create compound instance here using compoundInfo, attach it to the peak created above #################
                    compoundInfo = xmltree.getCompoundInfoFromElement(compound_element)
                    if compoundInfo["id"] not in compound_secondary_id_list:
                        compound_secondary_id_list.add(compoundInfo["id"])
                        compound = Compound(secondaryId=compoundInfo["id"], peak=peak, formula=compoundInfo["formula"],
                                            inchikey=compoundInfo["inchikey"], ppm=compoundInfo["ppm"],
                                            adduct=compoundInfo["adduct"], identified=compoundInfo["identified"])
                        compound.save()
                        try:
                            compound_id_map[compoundInfo["id"]].append(compound.id)
                        except:
                            compound_id_map[compoundInfo["id"]] = [compound.id]
                        dbs = xmltree.getCompoundDbsFromElement(compound_element)
                        if dbs:
                            for db_element in dbs:
                                ################# Create repository_compound (db) instance here using dbInfo, attach it to the compound created above #################
                                dbInfo = xmltree.getDbInfoFromElement(db_element)
                                repository_compound = RepositoryCompound(db_name=dbInfo["db_name"],
                                                                         identifier=dbInfo["identifier"],
                                                                         compound_name=dbInfo["compound_name"].encode(
                                                                             'utf-8'), compound=compound)
                                repository_compound.save()

            comparisons = xmltree.getComparisonsFromElement(peak_element)
            # print "######",comparisons
            if comparisons:
                for comparison_element in comparisons:
                    comparisonInfo = xmltree.getComparisonInfoFromElement(comparison_element)
                    comparison = Comparison.objects.get(id=comparisonInfo["id"])
                    peak_dt_comparison = PeakDtComparison(peak=peak, comparison=comparison,
                                                          logFC=comparisonInfo["logfc"],
                                                          pValue=comparisonInfo["pvalue"],
                                                          adjPvalue=comparisonInfo["adjpvalue"],
                                                          logOdds=comparisonInfo["logodds"])
                    peak_dt_comparison.save()

            sampleReferences = xmltree.getSampleReferencesFromElement(peak_element)
            if sampleReferences:
                for sampleReference_element in sampleReferences:
                    ################## Create PeakDTSample instance here using sampleReferenceId and intensity ###############
                    sampleReferenceId = xmltree.getSampleReferenceId(sampleReference_element)
                    sample = Sample.objects.get(id=sampleReferenceId)
                    # print sample.name
                    sampleReferenceIntensity = xmltree.getSampleReferenceIntensityFromElement(sampleReference_element)
                    peak_dt_sample = PeakDTSample(peak=peak, sample=sample, intensity=sampleReferenceIntensity)
                    peak_dt_sample.save()

            calibrationReferences = xmltree.getCalibrationReferencesFromElement(peak_element)
            if calibrationReferences:
                for calibrationReference_element in calibrationReferences:
                    ################## Create PeakDTSample instance here using sampleReferenceId and intensity ###############
                    calibrationReferenceId = xmltree.getCalibrationReferenceId(calibrationReference_element)
                    calibrationSample = CalibrationSample.objects.get(id=calibrationReferenceId)
                    # print sample.name
                    calibrationReferenceIntensity = xmltree.getCalibrationReferenceIntensityFromElement(
                        calibrationReference_element)
                    peak_qc_sample = PeakQCSample(peak=peak, sample=calibrationSample,
                                                  intensity=calibrationReferenceIntensity)
                    peak_qc_sample.save()

            peakSecondaryId += 1

    for pathway_element in xmltree.getPathways():
        ################# Create pathway instance here using pathwayInfo #################
        pathwayInfo = xmltree.getPathwayInfoFromElement(pathway_element)
        datasource_super_pathway = DataSourceSuperPathway.objects.get(identifier=pathwayInfo["id"].split(":")[1])
        # pathway = Pathway(secondaryId=pathwayInfo["id"].split(":")[1], name=pathwayInfo["name"], compoundNumber=pathwayInfo["compoundNumber"])
        # pathway.save()

        compoundsInPathway = xmltree.getCompoundsInPathwayFromElement(pathway_element)
        if compoundsInPathway:
            for compoundInPathway_element in compoundsInPathway:
                compound_in_pathway_id = xmltree.getCompoundInPathwayIdFromElement(compoundInPathway_element)
                # print compound_in_pathway_id
                if compound_in_pathway_id in compound_id_map:
                    for compound_id in compound_id_map[compound_in_pathway_id]:
                        compound = Compound.objects.get(id=compound_id)
                        CompoundPathway.objects.create(compound=compound, pathway=datasource_super_pathway)

def send_email(analysis, project, user, success):

    print "In the send email function"

    ctx_dict = {'analysis_name': analysis.experiment.title,
                'analysis': analysis,
                'project': project,
                'first_name': user.first_name}
    subject = render_to_string('email_templates/analysis_status_email_subject.txt',
                               ctx_dict)
    subject = ''.join(subject.splitlines())
    from_email, to = settings.DEFAULT_FROM_EMAIL, user.email

    print "The user's email is, ", user.email

    if success: # analysis has run successfully
        text_content = render_to_string('email_templates/analysis_status_success_email.txt', ctx_dict)
        html_content = render_to_string('email_templates/analysis_status_success_email.html', ctx_dict)
    else: # analysis failed
        text_content = render_to_string('email_templates/analysis_status_error_email.txt', ctx_dict)
        html_content = render_to_string('email_templates/analysis_status_error_email.html', ctx_dict)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@celery.task
def create_run_frank_chain(num_fragment_files, analysis, project, frank_experiment, fragmentation_set, user):
    celery_tasks=[]
    if num_fragment_files > 0:
        populate_tasks = run_frags(analysis, frank_experiment, fragmentation_set)
        celery_tasks.append(populate_tasks)
        celery_tasks.append(run_default_annotations.si(fragmentation_set, user))
    celery_tasks.append(end_pimp_pipeline.si(analysis, project, user, True))
    chain(celery_tasks, link_error=error_handler.s(analysis, project, user, False))()


@celery.task
def start_pimp_pipeline(analysis, project, saveFixtures=False):

    """ Starts the pimp R pipeline
    :type analysis: object
    """
    analysis.status = 'Processing'

    pipeline = Rpy2Pipeline(analysis, project, saveFixtures)
    xml_file_path = pipeline.run_pipeline()
    logger.info('xml_file_path is %s' % xml_file_path)

    if os.path.exists(xml_file_path):
        logger.info('Populating database')
        populate_database(xml_file_path)
    else:
        logger.info('XML file does not exist')

    connection.close()


@celery.task
def end_pimp_pipeline(analysis, project, user, successful):

    print "In the end of the pimp pipeline"

    # when pimp R analysis with or without fragments has finished
    if successful and frank_success(analysis):
        analysis.status = 'Finished'
        analysis_succeeded = True
    else:
        analysis.status = 'Error'
        analysis_succeeded = False

    analysis.save(update_fields=['status'])
    print 'the status of the analysis is', analysis.status

    try:
        print 'analysis succeeded is', analysis_succeeded
        send_email(analysis, project, user, analysis_succeeded)
        print 'An email should have been sent'

    except Exception as e:
        logger.info('Sending email failed: %s', e)
        print 'email failed'


#Check that the Frank run associated with this analysis was successful
def frank_success(analysis):

    success = True
    analysis_frag_link = PimpAnalysisFrankFs.objects.get(pimp_analysis=analysis)
    frag_set = analysis_frag_link.frank_fs
    print "Frag set status is:", frag_set.status
    annot_queries = AnnotationQuery.objects.filter(fragmentation_set=frag_set)

    for a_query in annot_queries:
        if a_query.status is "Completed with Errors":
            success = False

    if frag_set.status is "Completed with Errors":
        print "In frag set staus"
        success = False

    print "The success of the FrAnK run is", success

    return success


def get_ms1_df(analysis):

    #Get the MS1 peaks associated with this analysis
    print "Getting the MS1 dataframe"
    ms1_peaks = Peak.objects.filter(dataset__analysis=analysis).values_list("id", "mass", "rt", "polarity")
    # Put the data into a dataFrame format in order to be passed to R.
    # Intensity set to -0.25 until we decide what should be done with it.
    data = []
    for id, mass, rt, polarity in ms1_peaks:
        value = (id, float(mass), float(rt), -0.25, polarity)
        data.append(value)
    df = pd.DataFrame(data, columns=['pimp_id', 'mz', 'rt', 'intensity', 'polarity'])

    return df
