import os
import csv
import numpy as np
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings_dev')

import django
django.setup()

import jsonpickle
from experiments.models import DefaultParameter, Database, Experiment, Analysis
from frank.models import AnnotationTool, ExperimentalProtocol, AnnotationToolProtocol
from compound.models import Pathway, SuperPathway, DataSource, DataSourceSuperPathway
from frank.models import Peak as FrankPeak
from frank.models import PimpFrankPeakLink
from data.models import Peak, Dataset,PeakDTSample
from frank.models import FragmentationSet,SampleFile
from fileupload.models import Sample
from projects.models import Project

def hit(pimp_peak,frank_peak,masstol,rttol):
    pimp_mass = float(pimp_peak.mass)
    frank_mass = float(frank_peak.mass)
    if np.abs(frank_peak.retention_time - pimp_peak.rt) < rttol:
        if 1e6*np.abs(frank_mass - pimp_mass)/frank_mass < masstol:
            return True
        else:
            return False


if __name__=='__main__':


    # Extract the frank ms1 peaks

    fs = FragmentationSet.objects.all()[0]
    posfile = SampleFile.objects.filter(name='Beer_3_T10_POS.mzXML')[0]
    frankpeaks = FrankPeak.objects.filter(source_file = posfile,fragmentation_set = fs,msn_level = 1)
    print posfile,len(frankpeaks)
    # fp = FrankPeak.objects.filter(fragmentation_set = fs,msn_level=1,source_file_polarity = 'POS')

    # for f in fp:
    # 	if f.preferred_candidate_annotation:
    # 		print f.preferred_candidate_annotation.compound.name

    # project = Project.objects.filter(title = 'BeerProject')[0]
    # projectSamples = Sample.objects.filter(project = project,name__startswith = 'Beer_3')
    # stopeaks = PeakDTSample.objects.filter(sample = projectSamples)
    # peaks = []
    # for s in stopeaks:
    # 	if not s.peak in peaks:
    # 		peaks.append(s.peak)

    # print len(peaks)
    experiment = Experiment.objects.filter(title = 'AfterRonanMagic')[0]
    analysis = Analysis.objects.get(experiment = experiment)
    dataset = Dataset.objects.get(analysis = analysis)
    peaks = Peak.objects.filter(dataset = dataset, polarity = 'positive')
    print experiment,len(peaks)

    masstol = 1
    rttol = 5


    # Delete old link objects
    print "Deleting old links"
    links = PimpFrankPeakLink.objects.all()
    for l in links:
        l.delete()


    hit_count = 0
    # for i in range(100):
    for peak in peaks:
        # peak = peaks[i]
        in_range = [fp for fp in frankpeaks if hit(peak,fp,masstol,rttol)]
        if len(in_range)>0:
            if len(in_range) == 1:
                top_hit = in_range[0]
            else:
                # Find the closest
                top_hit = None
                closest_mass_diff = 1e6
                for p in in_range:
                    mass_diff = np.abs(peak.mass-fp.mass)
                    if mass_diff < closest_mass_diff:
                        top_hit = p
                        closest_mass_diff = mass_diff
            hit_count += 1
            print top_hit.mass,peak.mass,top_hit.retention_time,peak.rt
            if top_hit.preferred_candidate_annotation:
                print top_hit.preferred_candidate_annotation.compound.name,top_hit.preferred_candidate_annotation.confidence
            PimpFrankPeakLink.objects.create(frank_peak = top_hit,pimp_peak = peak)
    print hit_count,1.0*hit_count/len(peaks)
