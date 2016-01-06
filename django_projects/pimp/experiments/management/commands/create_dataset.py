# from django.core.management.base import NoArgsCommand
# Command to run in order to create dataset on database, replace the file by "yourFile"
# python manage.py create_dataset "/Users/yoanngloaguen/Documents/ideomWebSite/lydia_for_yoann.xml"
from django.core.management.base import BaseCommand
from fileupload.models import Sample
from experiments.models import Comparison, Analysis
from data.models import *
from compound.models import *
from experiments.pimpxml_parser.pimpxml_parser import Xmltree


class Command(BaseCommand):
    def handle(self, *args, **options):
        # populating database with information from xml file
        # print args
        compound_id_map = {}
        print "this is working"
        xmltree = Xmltree(args[0])
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
        print "Database population done!"
