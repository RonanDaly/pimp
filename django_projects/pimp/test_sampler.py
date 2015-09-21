import os,sys
import numpy as np
class StdMol:
	def __init__(self,mass,name):
		self.mass = mass
		self.name = name

	def could_be_match(self,mass,tol):
		proton = 1.00727645199076
		mass = mass - proton
		if np.abs(self.mass-mass)/self.mass < tol*1e-6:
			return True
		else:
			return False

if __name__ == '__main__':
	import django
	# sys.path.append('/Users/simon/git/pimp/django_projects/pimp/pimp')
	sys.path.append('/Users/simon/git/metabolomics_tools/fragments')
	import peak_objects
	import frag_set
	import network_sampler



	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings_dev')
	django.setup()
	from frank.models import Experiment,Peak,SampleFile,FragmentationSet,AnnotationQuery,CandidateAnnotation,Repository,Compound,CompoundRepository


	# Load the std1 database
	print "loading std1 mols"
	mols = []
	with open('/Users/simon/git/metabolomics_tools/AdductLevels/database/std1_mols.csv') as dbfile:
		for line in dbfile:
			splitline = line.split(',')
			mols.append(StdMol(float(splitline[3]),splitline[1].strip()))
	
	# pull out a std1 annotation
	fragment_set = FragmentationSet.objects.get(slug='standard-1-frag-set-2')
	sfile = SampleFile.objects.filter(name='STD_MIX1_POS_60stepped_1E5_Top5.mzXML')
	list_of_peaks = Peak.objects.filter(fragmentation_set = fragment_set,msn_level=1,source_file=sfile)

	# loop over the peaks and see if it could be a match
	matches = {}
	for p in list_of_peaks:
		matches[p] = None
		for m in mols:
			if m.could_be_match(float(p.mass),5):
				matches[p] = m

	qu = AnnotationQuery.objects.filter(name='standard-1-frag-set-1')
	for k in matches:
		if matches[k]:
			annotations = CandidateAnnotation.objects.filter(peak=k,annotation_query=qu)
			print
			print
			print matches[k].name
			for a in annotations:
				print a
	

	# fragment_set = FragmentationSet.objects.get(slug="simon-test-fragmentation-set-2")
	# beerfile = SampleFile.objects.filter(name='Beer_3_T10_POS.mzXML')
	# list_of_peaks = Peak.objects.filter(fragmentation_set = fragment_set,msnLevel=1,sourceFile=beerfile)
	# qu = AnnotationQuery.objects.filter(slug='test-annotation-query-1')
	
	# peakset = frag_set.FragSet()
	# peakset.annotations = []

	# qu2 = AnnotationQuery.objects.filter(name='posterior')
	# if qu2 != None:
	# 	an2 = CandidateAnnotation.objects.filter(annotation_query=qu2)
	# 	for a in an2:
	# 		a.delete()
	# 	qu2.delete()


	# qu2 = AnnotationQuery.objects.create(name='posterior',fragmentation_set=fragment_set,massBank=False)


	
	# for p in list_of_peaks:
	# 	print p,p.sourceFile.name
	# 	newmeasurement = peak_objects.Measurement(p.id)
	# 	peakset.measurements.append(newmeasurement)
	# 	# loop over all candidate annotations for this peak
	# 	ca = CandidateAnnotation.objects.filter(peak=p,annotation_query=qu)
	# 	for a in ca:
	# 		# split the name up
	# 		split_name = a.compound.name.split(';')
	# 		simple_name = split_name[0]
	# 		# find this one in the previous ones
	# 		previous_pos = [i for i,n in enumerate(peakset.annotations) if n.name==simple_name]
	# 		if len(previous_pos) == 0:
	# 			peakset.annotations.append(peak_objects.Annotation(a.compound.formula,simple_name))
	# 			newmeasurement.annotations[peakset.annotations[-1]] = float(a.confidence)
	# 		else:
	# 			# check if this measurement has had this annotation before
	# 			this_annotation = peakset.annotations[previous_pos[0]]
	# 			if this_annotation in newmeasurement.annotations:
	# 				current_confidence = newmeasurement.annotations[this_annotation]
	# 				newmeasurement.annotations[this_annotation] = max(float(a.confidence),current_confidence)
	# 			else:
	# 				newmeasurement.annotations[this_annotation] = float(a.confidence)
				
	# 		# print '\t' + a.compound.name + '\t' + a.compound.formula + '\t' + str(a.confidence)
	# 		# Compress similar ones

	# print "Stored " + str(len(peakset.measurements)) + " peaks and " + str(len(peakset.annotations)) + " unique annotations"



	# n = network_sampler.NetworkSampler(peakset)
	# n.initialise_sampler()
	# n.multiple_network_sample(1000)
	# n.compute_posteriors()
	# n.dump_output(open('testoutput.txt','w'))

	# repo,created = Repository.objects.get_or_create(name='posterior_annotations')
	# print repo
	# co = Compound.objects.filter(repository=repo)
	# for c in co:
	# 	c.delete()
	# co = CompoundRepository.objects.filter(repository=repo)
	# for c in co:
	# 	c.delete()

	# for m in peakset.measurements:
	# 	p = Peak.objects.get(id=m.id)
	# 	for a in m.annotations:
	# 		c,created = Compound.objects.get_or_create(formula=a.formula.formula,exact_mass=a.formula.compute_exact_mass(),name=a.name)
	# 		c.save()
	# 		if created:
	# 			d = CompoundRepository.objects.create(compound=c,repository=repo)
	# 		an = CandidateAnnotation.objects.create(compound=c,peak=p,confidence=peakset.posterior_probability[m][a],annotation_query=qu2)


