# from django.core.management.base import NoArgsCommand
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

		print "this is working"
		xmltree = Xmltree(args[0])
		anaysis_id = xmltree.getAnalysisId()
		analysis = Analysis.objects.get(id=anaysis_id)
		print "analysis ",analysis.submited
		# print analysis.peak_set.all()
		print "number of peaks :"
		print len(xmltree.allPeaks())
		print len(xmltree.getPeaks())
		############ Create a dataset instance here ##################
		peakSecondaryId = 1
		for i in xmltree.getPeakIds():
			################# Create peak instance here using peakInfo and peakSecondaryId, attach it to the dataset created above #################
			peakInfo = xmltree.getPeakInfo(i)
			######## Debug ########
			if peakSecondaryId == 1:
				print "peak id: ",peakSecondaryId
				print "rt: ",peakInfo["retention_time"]
				print "mass: ",peakInfo["mass"]
				print "polarity: ",peakInfo["polarity"]
			######## End debug #######
			compoundIds = xmltree.getCompoundIds(i)
			if compoundIds:
				for compoundId in compoundIds:
					################# Create compound instance here using compoundInfo and j as compoundSecondaryId, attach it to the peak created above #################
					compoundInfo = xmltree.getCompoundInfo(compoundId)
					######## Debug ########
					if compoundId == 1:
						print "peak id attached: ",peakSecondaryId
						print "compound id: ",compoundId
						print "name: ",compoundInfo["name"]
						print "formula: ",compoundInfo["formula"]
						print "ppm: ",compoundInfo["ppm"]
						print "db: ",compoundInfo["db"]
						print "dbId: ",compoundInfo["dbId"]
						print "adduct: ",compoundInfo["adduct"]
						print "identified: ",compoundInfo["identified"]
					######## End debug #######
			# if xmltree.getComparisonIds(i):
			# 	# print "comparison in this peak: ",xmltree.getComparisonIds(i)
			# 	for comparisonId in xmltree.getComparisonIds(i):
			# 		print comparisonId
			# 		print i
			# 		comparisonInfo = xmltree.getComparisonInfo(i,comparisonId)
			# 		print comparisonInfo
			sampleIds = xmltree.getSampleReferenceIds(i)
			if sampleIds:
				for sampleReferenceId in sampleIds:
					################## Create PeakDTSample instance here using sampleReferenceId
					sample = Sample.objects.get(id=sampleReferenceId)
					# print sample.name
					sampleIntensity = xmltree.getSampleReferenceIntensity(i, sampleReferenceId)
					# print "sample ",sampleReferenceId
					# print "intensity ",sampleIntensity
			print peakSecondaryId
			peakSecondaryId += 1
			break
		print peakSecondaryId

