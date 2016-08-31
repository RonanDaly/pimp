import os
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from djcelery import celery
from rpy2.robjects.packages import importr

from compound.models import logging, Compound, RepositoryCompound, DataSourceSuperPathway, CompoundPathway
from data.models import Analysis, Dataset, Peak, Comparison, PeakDtComparison, Sample, PeakDTSample, CalibrationSample, PeakQCSample
from experiments.pimpxml_parser.pimpxml_parser import Xmltree
import rpy2.robjects as robjects

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

def get_file_list(analysis, project):
    file_list = {}
    file_list['positive'] = [
        'samples/POS/Beer_4_full1.mzXML', 'samples/POS/Beer_4_full2.mzXML', 'samples/POS/Beer_4_full3.mzXML',
        'samples/POS/Beer_1_full1.mzXML', 'samples/POS/Beer_1_full2.mzXML', 'samples/POS/Beer_1_full3.mzXML',
        'samples/POS/Beer_2_full1.mzXML', 'samples/POS/Beer_2_full2.mzXML', 'samples/POS/Beer_2_full3.mzXML',
        'samples/POS/Beer_3_full1.mzXML', 'samples/POS/Beer_3_full2.mzXML', 'samples/POS/Beer_3_full3.mzXML'
    ]
    file_list['negative'] = [
        'samples/NEG/Beer_4_full1.mzXML', 'samples/NEG/Beer_4_full2.mzXML', 'samples/NEG/Beer_4_full3.mzXML',
        'samples/NEG/Beer_1_full1.mzXML', 'samples/NEG/Beer_1_full2.mzXML', 'samples/NEG/Beer_1_full3.mzXML',
        'samples/NEG/Beer_2_full1.mzXML', 'samples/NEG/Beer_2_full2.mzXML', 'samples/NEG/Beer_2_full3.mzXML',
        'samples/NEG/Beer_3_full1.mzXML', 'samples/NEG/Beer_3_full2.mzXML', 'samples/NEG/Beer_3_full3.mzXML'
    ]
    return file_list

def get_groups(analysis, project):
    groups = {
        'beer_taste' : {
            'delicious' : ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'],
            'not_bad'   : ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3'],
            'bad'       : ['Beer_4_full1'],
            'awful'     : ['Beer_4_full2', 'Beer_4_full3']
        },
        'beer_colour' : {
            'dark'      : ['Beer_1_full1', 'Beer_1_full2', 'Beer_1_full3', 'Beer_2_full1', 'Beer_2_full2', 'Beer_2_full3'],
            'light'     : ['Beer_3_full1', 'Beer_3_full2', 'Beer_3_full3', 'Beer_4_full1', 'Beer_4_full2', 'Beer_4_full3']
        }
    }
    return groups

def convert_to_r(groups):
    ''' Convert groups in python into rpy2 objects'''

    outer_dict = {}
    for key in groups.keys():
        inner_dict = groups[key]
        group_dict = {}
        for k in inner_dict.keys():
            group_dict[k] = robjects.StrVector(inner_dict[k])
        item = robjects.ListVector(group_dict)
        outer_dict[key] = item

    r_thing = robjects.ListVector(outer_dict)
    return r_thing

def get_standard_list():
    standard_list = [
        'calibration_samples/standard/Std1_1_20150422_150810.csv',
        'calibration_samples/standard/Std2_1_20150422_150711.csv',
        'calibration_samples/standard/Std3_1_20150422_150553.csv'
    ]
    return standard_list

def get_comparisons(analysis, project):
    comparisons = ['beer1', 'beer4']
    comparison_names = ['beer_comparison']
    return comparisons, comparison_names

def get_database_list(analysis, project):
    database_list = ['kegg', 'hmdb', 'lipidmaps', 'standard']
    return database_list

class PipelineMetadata(object):
    def __init__(self, files, groups, stds, names, contrasts, databases):
        self.files = files
        self.groups = groups
        self.stds = stds
        self.names = names
        self.contrasts = contrasts
        self.databases = databases
        
def get_pipeline_metadata(analysis, project):
    
    # set up files
    file_list = get_file_list(analysis, project)
    posvector = robjects.StrVector(file_list['positive'])
    negvector = robjects.StrVector(file_list['negative'])
    files = robjects.ListVector({'positive': posvector, 'negative': negvector})

    # set up groups
    groups = get_groups(analysis, project)
    groups = convert_to_r(groups)

    # set up standards
    standard_list = get_standard_list()
    stds = robjects.StrVector(standard_list)

    # TODO: need to set up the comparison correctly
    comparisons, comparison_names = get_comparisons(analysis, project)
    contrasts = robjects.StrVector(comparisons)
    names = robjects.StrVector(comparison_names)

    # set up databases
    database_list = get_database_list(analysis, project)
    databases = robjects.StrVector(database_list)
    
    # collect all the values together
    metadata = PipelineMetadata(files, groups, stds, names, 
                                contrasts, databases)
    
    return metadata

# read and think about this:
# http://stackoverflow.com/questions/5707382/is-multiprocessing-with-rpy-safe
def run_rpy2_pipeline(analysis, project, metadata, saveFixtures):
        
    importr('PiMP')

    # TODO: we should do this in Python ..
    get_pimp_wd = robjects.r['Pimp.getPimpWd']
    working_dir = get_pimp_wd(project.id)

    # TODO: we should do this in Python ??
    validate_input = robjects.r['Pimp.validateInput']
    validate_input(analysis.id, metadata.files, metadata.groups, working_dir)

    # TODO: we should do this in Python !!
    get_analysis_params = robjects.r['Pimp.getAnalysisParams']
    pimp_params = get_analysis_params(analysis.id)

    # dump the input parameters out for R debugging
    dump_input = robjects.r['Pimp.dump_parameters']
    dump_input(metadata.files, metadata.groups, metadata.stds, 
               metadata.names, metadata.contrasts, metadata.databases, 
               analysis.id, project.id, working_dir, pimp_params)

    # call the pipeline
    runPipeline = robjects.r['Pimp.runPipeline']
    runPipeline(metadata.files, metadata.groups, metadata.stds, 
                metadata.names, metadata.contrasts, metadata.databases, 
                saveFixtures, analysis.id, project.id, working_dir,
                pimp_params)
    
    return_code = 0
    return return_code
    
@celery.task
def start_pimp_pipeline(analysis, project, user, saveFixtures=False):
    ''' Starts the pimp R pipeline '''

    base = importr('base')
    base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')

    metadata = get_pipeline_metadata(analysis, project)
    return_code = run_rpy2_pipeline(analysis, project, metadata, saveFixtures)

    xml_file_name = ".".join(["_".join(["analysis", str(analysis.id)]), "xml"])
    xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(project.id), xml_file_name)
    logger.info('xml_file_path is %s' % xml_file_path)

    if os.path.exists(xml_file_path):
        populate_database(xml_file_path)
        analysis.status = 'Finished'
        analysis.save(update_fields=['status'])
        send_email(analysis, project, user, True)
    else:
        analysis.status = 'Error'
        analysis.save(update_fields=['status'])
        # send_email(analysis, project, user, False) REMEMBER TO UNCOMMENT THIS

    success = True if return_code == 0 else False
    return success