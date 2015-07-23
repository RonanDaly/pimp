import os,sys

if __name__ == '__main__':
	import django
	# sys.path.append('/Users/simon/git/pimp/django_projects/pimp/pimp')
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings_dev')
	django.setup()
	from frank.models import Experiment,Peak,SampleFile,FragmentationSet


	fragment_set = FragmentationSet.objects.get(slug="simon-test-fragmentation-set-2")
	beerfile = SampleFile.objects.filter(name='Beer_3_T10_POS.mzXML')
	list_of_peaks = Peak.objects.filter(fragmentation_set = fragment_set,msnLevel=1,sourceFile=beerfile)
	for p in list_of_peaks:
		print p.mass
		for a in p.annotations.all():
			print '\t' + a.name + '\t' + a.formula



