from djcelery import celery
# from rpy2.robjects.packages import importr
# import rpy2.robjects as robjects
import os
import subprocess
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
##### JUST FOR SCOTT ALTERNATIVE CODE
import rpy2.robjects as robjects


@celery.task
def start_pimp_pipeline(analysis, project, user):
    # print "standards: ",standard_list
    # print "comparisons: ",comparisons
    # print "file list: ",file_list
    # print "groups: ",group_list

    # print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
    # print "+++++++++++++++++ Loading parameters +++++++++++++++"
    # print "++++++++++++++++++++++++++++++++++++++++++++++++++++"

    # base = importr('base')
    # base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')
    # posvector = robjects.StrVector(file_list['positive'])
    # negvector = robjects.StrVector(file_list['negative'])
    # files = robjects.ListVector({'positive': posvector, 'negative': negvector})
    # print "---------------------------------------------------"
    # print "----------------- File list loaded ----------------"
    # print "---------------------------------------------------"
    # group_dict = {}
    # for k in group_list.keys():
    # 	group_dict[k] = robjects.StrVector(group_list[k])
    # groups = robjects.ListVector(group_dict)
    # print "---------------------------------------------------"
    # print "----------------- Group list loaded ---------------"
    # print "---------------------------------------------------"
    # standards = robjects.StrVector(standard_list)
    # print "---------------------------------------------------"
    # print "--------------- Standard list loaded --------------"
    # print "---------------------------------------------------"
    # contrasts = robjects.StrVector(comparisons)
    # print "---------------------------------------------------"
    # print "--------------- Contrast list loaded --------------"
    # print "---------------------------------------------------"
    # databases = robjects.StrVector(database_list)
    # print "---------------------------------------------------"
    # print "--------------- Database list loaded --------------"
    # print "---------------------------------------------------"
    # pimp = importr('PiMP')
    # runPipeline = robjects.r['Pimp.runPipeline']
    # runPipeline(files=files, groups=groups, contrasts=contrasts, standards=standards, databases=databases, nSlaves=15)
    analysis.status = 'Processing'
    analysis.save(update_fields=['status'])
    # print "Email sent to the user"
    # user.email_user('Subject here', 'Your analysis has started processing, thank you for using PiMP', settings.DEFAULT_FROM_EMAIL)
    ############## This wouldn't work for me! - Scott
    # r_command_list = ["/usr/local/bin/R-3.0.3/lib64/R/bin/Rscript","/opt/django/scripts/pimp/runPiMP.R",str(analysis.id)]

    r_command_list = [settings.RSCRIPT_PATH, os.path.join(os.path.dirname(settings.BASE_DIR), '..', 'runPiMP.R'),
                      str(analysis.id)]
    r_command = " ".join(r_command_list)
    print r_command
    subprocess.call(r_command, shell=True)
    xml_file_name = ".".join(["_".join(["analysis", str(analysis.id)]), "xml"])
    # xml_file_path = os.path.join('/opt/django/data/pimp_data/projects/',str(project.id), xml_file_name)
    ############## Again Hard coded path incorrect for me
    xml_file_path = os.path.join(settings.MEDIA_ROOT, 'projects', str(project.id),
                                 xml_file_name)

    if os.path.exists(xml_file_path):
        compound_id_map = {}
        print "Database population started!"
        xmltree = Xmltree(xml_file_path)
        anaysis_id = xmltree.getAnalysisId()
        # print anaysis_id
        analysis = Analysis.objects.get(id=anaysis_id)
        # print "analysis ",analysis.submited
        # print analysis.peak_set.all()
        # print "number of peaks :"
        # print len(xmltree.allPeaks())
        # print len(xmltree.getPeaks())
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
                # print peak.id
                ######## Debug ########
                # if peakSecondaryId == 1:
                # 	print "peak id: ",peakSecondaryId
                # 	print "rt: ",peakInfo["retention_time"]
                # 	print "mass: ",peakInfo["mass"]
                # 	print "polarity: ",peakInfo["polarity"]
                ######## End debug #######


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
                            ######### Debug ########
                            # if compoundInfo["id"] == 2:
                            # 	print "####################### COMPOUND #######################"
                            # 	print "peak id attached: ",peakSecondaryId
                            # 	print "compound id: ",compoundInfo["id"]
                            # 	# print "name: ",compoundInfo["name"]
                            # 	print "formula: ",compoundInfo["formula"]
                            # 	print "inchikey: ",compoundInfo["inchikey"]
                            # 	print "ppm: ",compoundInfo["ppm"]
                            # 	# print "db: ",compoundInfo["db"]
                            # 	# print "dbId: ",compoundInfo["dbId"]
                            # 	print "adduct: ",compoundInfo["adduct"]
                            # 	print "identified: ",compoundInfo["identified"]
                            ######## End debug #######
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
                                ######### Debug ########
                                # if compoundInfo["id"] == 2:
                                # 	print "####################### DB #######################"
                                # 	print "db name: ",dbInfo["db_name"]
                                # 	print "db identifier: ",dbInfo["identifier"]
                                # 	print "compound name: ",dbInfo["compound_name"]
                                ######## End debug #######

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
                    # if peakSecondaryId == 1:
                    # 	print "####################### COMPARISON #######################"
                    # 	print "id: ",comparisonInfo["id"]
                    # 	print "logfc: ",comparisonInfo["logfc"]
                    # 	print "pvalue: ",comparisonInfo["pvalue"]
                    # 	print "adjpvalue: ",comparisonInfo["adjpvalue"]
                    # 	print "logodds: ",comparisonInfo["logodds"]
                # if xmltree.getComparisonIds(i):
                # 	# print "comparison in this peak: ",xmltree.getComparisonIds(i)
                # 	for comparisonId in xmltree.getComparisonIds(i):
                # 		print comparisonId
                # 		print i
                # 		comparisonInfo = xmltree.getComparisonInfo(i,comparisonId)
                # 		print comparisonInfo


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

                    # if peakSecondaryId == 1:
                    # 	print "######################## SAMPLE REFERENCE ####################"
                    # 	print "sample reference id: ", sampleReferenceId
                    # 	print "intensity: ",sampleReferenceIntensity
                    # print "sample ",sampleReferenceId
                    # print "intensity ",sampleIntensity

                peakSecondaryId += 1
        # print peakSecondaryId
        # break
        # print peakSecondaryId
        # print len(xmltree.getPathways())
        for pathway_element in xmltree.getPathways():
            ################# Create pathway instance here using pathwayInfo #################
            pathwayInfo = xmltree.getPathwayInfoFromElement(pathway_element)
            datasource_super_pathway = DataSourceSuperPathway.objects.get(identifier=pathwayInfo["id"].split(":")[1])
            # pathway = Pathway(secondaryId=pathwayInfo["id"].split(":")[1], name=pathwayInfo["name"], compoundNumber=pathwayInfo["compoundNumber"])
            # pathway.save()

            compoundsInPathway = xmltree.getCompoundsInPathwayFromElement(pathway_element)
            # print pathwayInfo["id"]
            if compoundsInPathway:
                for compoundInPathway_element in compoundsInPathway:
                    compound_in_pathway_id = xmltree.getCompoundInPathwayIdFromElement(compoundInPathway_element)
                    # print compound_in_pathway_id
                    if compound_in_pathway_id in compound_id_map:
                        for compound_id in compound_id_map[compound_in_pathway_id]:
                            compound = Compound.objects.get(id=compound_id)
                            CompoundPathway.objects.create(compound=compound, pathway=datasource_super_pathway)
                            # if pathwayInfo["id"] == "path:map00052":
                            # print "pathway info"
                            # print pathwayInfo
        analysis.status = 'Finished'
        analysis.save(update_fields=['status'])
        ctx_dict = {'analysis_name': analysis.experiment.title,
                    'analysis': analysis,
                    'project': project,
                    'first_name': user.first_name}
        subject = render_to_string('email_templates/analysis_status_email_subject.txt',
                                   ctx_dict)
        subject = ''.join(subject.splitlines())
        from_email, to = settings.DEFAULT_FROM_EMAIL, user.email
        text_content = render_to_string('email_templates/analysis_status_success_email.txt',
                                        ctx_dict)
        html_content = render_to_string('email_templates/analysis_status_success_email.html',
                                        ctx_dict)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    # user.email_user('Subject here', 'Your analysis is now finished, login to PiMP and start interprete your results now! Thanks for using PiMP', settings.DEFAULT_FROM_EMAIL)
    else:
        analysis.status = 'Error'
        analysis.save(update_fields=['status'])
        ctx_dict = {'analysis_name': analysis.experiment.title,
                    'analysis': analysis,
                    'first_name': user.first_name}
        subject = render_to_string('email_templates/analysis_status_email_subject.txt',
                                   ctx_dict)
        subject = ''.join(subject.splitlines())
        from_email, to = settings.DEFAULT_FROM_EMAIL, user.email
        text_content = render_to_string('email_templates/analysis_status_error_email.txt',
                                        ctx_dict)
        html_content = render_to_string('email_templates/analysis_status_error_email.html',
                                        ctx_dict)
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    # subprocess.call("/usr/local/bin/R-3.0.3/lib64/R/bin/Rscript /home/yoann/run_pimp_pipeline.R", shell=True)
    # subprocess.call("/usr/local/bin/R-3.0.3/lib64/R/bin/Rscript /opt/django/scripts/pimp/runPiMP.R", shell=True)
    # runPipeline(files=files, groups=groups, contrasts=contrasts, standards=standards, databases=databases)
    return "Pipeline run with success! Yeah, celebration time!!!!!"
