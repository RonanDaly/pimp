from djcelery import celery
# from rpy2.robjects.packages import importr
# import rpy2.robjects as robjects
import os
import subprocess
import pandas as pd
from rpy2.robjects import pandas2ri
import re
from fileupload.models import Sample, CalibrationSample
from experiments.models import Comparison, Analysis
from data.models import *
from compound.models import *
from experiments.pimpxml_parser.pimpxml_parser import Xmltree
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import connection;
##### JUST FOR SCOTT ALTERNATIVE CODE
import rpy2.robjects as robjects

from frank.models import PimpProjectFrankExp, FragmentationSet
from frank.models import SampleFile as FrankSampleFile
from frank.views import input_peak_list_to_database


logger = logging.getLogger(__name__)

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
    
    ctx_dict = {'analysis_name': analysis.experiment.title,
                'analysis': analysis,
                'project': project,
                'first_name': user.first_name}
    subject = render_to_string('email_templates/analysis_status_email_subject.txt',
                               ctx_dict)
    subject = ''.join(subject.splitlines())
    from_email, to = settings.DEFAULT_FROM_EMAIL, user.email

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
def start_pimp_pipeline(analysis, project, user, saveFixtures=False):
    """ Starts the pimp R pipeline """
    
    # some old code not sure written by whom to call Pimp.runPipeline from python using rpy2
    # according to yoann, this doesn't work with the mzmatch pipeline because it's too big 
    # and takes too long to run
    
    # print "standards: ",standard_list
    # print "comparisons: ",comparisons
    # print "file list: ",file_list
    # print "groups: ",group_list
    # print "+++++++++++++++++ Loading parameters +++++++++++++++"
    # base = importr('base')
    # base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')
    # posvector = robjects.StrVector(file_list['positive'])
    # negvector = robjects.StrVector(file_list['negative'])
    # files = robjects.ListVector({'positive': posvector, 'negative': negvector})
    # print "----------------- File list loaded ----------------"
    # group_dict = {}
    # for k in group_list.keys():
    # 	group_dict[k] = robjects.StrVector(group_list[k])
    # groups = robjects.ListVector(group_dict)
    # print "----------------- Group list loaded ---------------"
    # standards = robjects.StrVector(standard_list)
    # print "--------------- Standard list loaded --------------"
    # contrasts = robjects.StrVector(comparisons)
    # print "--------------- Contrast list loaded --------------"
    # databases = robjects.StrVector(database_list)
    # print "--------------- Database list loaded --------------"
    # pimp = importr('PiMP')
    # runPipeline = robjects.r['Pimp.runPipeline']
    # runPipeline(files=files, groups=groups, contrasts=contrasts, standards=standards, databases=databases, nSlaves=15)

    # Extra calls for running Frank.

    pimpFrankLink = PimpProjectFrankExp.objects.get(pimp_project=project)
    frank_experiment = pimpFrankLink.frank_expt
    print "Pimp tasks Experiment ", frank_experiment
    fragmentation_set = FragmentationSet.objects.get(experiment=frank_experiment)
    print "Pimp Tasks FragSet ", fragmentation_set
    fragment_files = FrankSampleFile.objects.filter(sample__experimental_condition__experiment=frank_experiment)
    num_fragment_files = len(fragment_files)


    logger.info('There are %s' % num_fragment_files, 'fragment files to be processed and are: %s' % fragment_files)

    r_command_list = [settings.RSCRIPT_PATH, os.path.join(os.path.dirname(settings.BASE_DIR), '..', 'runPiMP.R'),
                      str(analysis.id), str(saveFixtures)]
    r_command = " ".join(r_command_list)
    logger.info('r_command is %s' % r_command)    
    
    analysis.status = 'Processing'
    analysis.save(update_fields=['status'])
    connection.close()

    # Here is the entry point to the R pipeline
    return_code = subprocess.call(r_command, shell=True)

    xml_file_name = ".".join(["_".join(["analysis", str(analysis.id)]), "xml"])
    xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(project.id), xml_file_name)
    logger.info('xml_file_path is %s' % xml_file_path)

    if os.path.exists(xml_file_path):
        populate_database(xml_file_path)

        # Start the R pipeline for Frank passing in the Pimp MS1 peaks.
        if num_fragment_files > 0:

            print "Producing a dataframe from the MS1 peaks"
            #Get the MS1 peaks associated with this analysis
            ms1_peaks = Peak.objects.filter(dataset__analysis=analysis).values_list("mass","rt","polarity")

            #Put the data into a dataFrame format in order to be passed to R.
            #Intensity set to -0.25 until we decide what should be done with it.
            data = []
            for mass, rt, polarity in ms1_peaks:
                value = (float(mass), float(rt), -0.25, polarity)
                data.append(value)
            df = pd.DataFrame(data, columns=['mz', 'rt', 'intensity', 'polarity'])
            pandas2ri.activate()
            ms1_df = pandas2ri.py2ri(df)
            print "The ms1 peak_dataframe is", ms1_df

            # Extract the peaks for the fragmentation files using Frank and the ms1 peaks
            input_peak_list_to_database(frank_experiment.slug, fragmentation_set.slug, ms1_df)
            print "Running the input peak list from Pimp"

            #Get all of the peaks associated with this analysis

        analysis.status = 'Finished'
        analysis.save(update_fields=['status'])
        send_email(analysis, project, user, True)
    else:
        analysis.status = 'Error'
        analysis.save(update_fields=['status'])
        send_email(analysis, project, user, False)

    success = True if return_code == 0 else False
    return success