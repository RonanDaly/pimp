import os,sys

if __name__ == '__main__':
	import django
	# sys.path.append('/Users/simon/git/pimp/django_projects/pimp/pimp')
	sys.path.append('/Users/simon/git/metabolomics_tools/fragments')
	import peak_objects
	import frag_set
	import network_sampler

	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings_dev')
	django.setup()
	from frank.models import Experiment,Peak,SampleFile,FragmentationSet,AnnotationQuery,CandidateAnnotation


	fragment_set = FragmentationSet.objects.get(slug="simon-test-fragmentation-set-2")
	beerfile = SampleFile.objects.filter(name='Beer_3_T10_POS.mzXML')
	list_of_peaks = Peak.objects.filter(fragmentation_set = fragment_set,msnLevel=1,sourceFile=beerfile)
	qu = AnnotationQuery.objects.filter(slug='test-annotation-query-1')
	
	peakset = frag_set.FragSet()
	peakset.annotations = []


	#Following needs to be done for each peak
	for p in list_of_peaks:
		print p,p.sourceFile.name
		newmeasurement = peak_objects.Measurement(p.id)
		peakset.measurements.append(newmeasurement)
		# loop over all candidate annotations for this peak
		ca = CandidateAnnotation.objects.filter(peak=p,annotation_query=qu)
		for a in ca:
			# split the name up
			split_name = a.compound.name.split(';')
			simple_name = split_name[0]
			# find this one in the previous ones
			previous_pos = [i for i,n in enumerate(peakset.annotations) if n.name==simple_name]
			if len(previous_pos) == 0:
				peakset.annotations.append(peak_objects.Annotation(a.compound.formula,simple_name))
				newmeasurement.annotations[peakset.annotations[-1]] = float(a.confidence)
			else:
				# check if this measurement has had this annotation before
				this_annotation = peakset.annotations[previous_pos[0]]
				if this_annotation in newmeasurement.annotations:
					current_confidence = newmeasurement.annotations[this_annotation]
					newmeasurement.annotations[this_annotation] = max(float(a.confidence),current_confidence)
				else:
					newmeasurement.annotations[this_annotation] = float(a.confidence)
				
			# print '\t' + a.compound.name + '\t' + a.compound.formula + '\t' + str(a.confidence)
			# Compress similar ones

	print "Stored " + str(len(peakset.measurements)) + " peaks and " + str(len(peakset.annotations)) + " unique annotations"



	n = network_sampler.NetworkSampler(peakset)
	n.initialise_sampler()
	n.multiple_network_sample(1000)
	n.dump_output(open('testoutput.txt','w'))

