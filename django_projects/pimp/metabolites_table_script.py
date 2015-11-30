import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pimp.settings")

try:
    from django.utils import simplejson
except:
    import json as simplejson
from django.db.models import Avg
# models
from projects.models import Project
from data.models import *
from compound.models import *
from groups.models import Attribute
from fileupload.models import Sample, CalibrationSample, Curve
import timeit

analysis_id = 1
project_id = 1

analysis = Analysis.objects.get(pk=analysis_id)
project = Project.objects.get(pk=project_id)
dataset = analysis.dataset_set.first()
comparisons = analysis.experiment.comparison_set.all()
samples = Sample.objects.filter(
    attribute=Attribute.objects.filter(comparison__in=comparisons).distinct().order_by('id')).distinct().order_by(
    'attribute__id', 'id')
# efficiency
peakdtsamples = PeakDTSample.objects.filter(peak__dataset=dataset)

data = []

identified_compounds = Compound.objects.filter(identified='True', peak__dataset=dataset).distinct()
id_compound_peakdtsamples = peakdtsamples.filter(sample__in=samples, peak__compound__in=identified_compounds)
ic_secondary_ids = identified_compounds.values_list('secondaryId', flat=True)
print "\n"*5
print "Identified compounds"
print "\n"*5
for secondary_id in ic_secondary_ids:
    c_data = []

    # Select the most intense peak that has been identified by the compound
    # and use this to represent the compound
    p_max_intense_id = id_compound_peakdtsamples.filter(peak__compound__secondaryId=secondary_id).order_by('-intensity').values_list('peak__id', flat=True).first()

    max_compound_id = identified_compounds.filter(peak__id=p_max_intense_id, secondaryId=secondary_id).values_list('id', flat=True)[0]

    best_compound = identified_compounds.get(pk=max_compound_id)

    peak = best_compound.peak

    # compound id
    c_data.append(str(max_compound_id))
    # peak id
    c_data.append(str(peak.id))
    # compound name
    c_data.append(best_compound.repositorycompound_set.filter(db_name='stds_db').values_list('compound_name',flat=True).first())
    # compound formula
    c_data.append(str(best_compound.formula))

    # Get pathways
    pathway_ids = CompoundPathway.objects.filter(compound=best_compound).values_list('pathway__pathway__id', flat=True).distinct()
    if pathway_ids.exists():
        superpathways = DataSourceSuperPathway.objects.filter(pathway__id__in=pathway_ids).values_list('super_pathway__name', flat=True)
        if None not in superpathways or superpathways.count() > 0:
            try:
                joined_sp = " ".join(superpathways)
            except:
                joined_sp = "None"
            c_data.append(joined_sp) # superpathways
        else:
            c_data.append("None")
        c_data.append(" ".join(Pathway.objects.filter(id=pathway_ids).values_list('name', flat=True))) # pathways
    else:
        c_data.append("None") # no superpathways
        c_data.append("None") # no pathways

    # Intensities of the peak across samples
    peak_intensities_by_samples = id_compound_peakdtsamples.filter(peak=peak).order_by('sample__attribute__id', 'sample__id')

    for intensity in peak_intensities_by_samples.values_list('intensity', flat=True):
        c_data.append(str(intensity))  # individual sample intensities

    # Average intensity of the peak across attributes
    attribute_ids = set(samples.values_list('sampleattribute__attribute__id', flat=True))
    averages_by_group = []
    for attribute_id in attribute_ids:
        averages_by_group.append(peak_intensities_by_samples.filter(sample__sampleattribute__attribute__id=attribute_id).aggregate(Avg('intensity'))['intensity__avg'])

    c_data += averages_by_group # average intensities over groups
    c_data.append('identified')
    # Add the compound information to data
    print c_data

print "\n"*5
print "Annotated"
print "\n"*5

annotated_compounds = Compound.objects.filter(identified='False', peak__dataset=dataset).exclude(
        secondaryId=identified_compounds.values_list("secondaryId", flat=True)).distinct()
ac_secondary_ids = annotated_compounds.values_list('secondaryId', flat=True)
ac_compound_peakdtsamples = peakdtsamples.filter(sample=samples, peak__compound__in=annotated_compounds)
start = timeit.default_timer()
for secondary_id in ac_secondary_ids:
    c_data = []

    p_max_intense_id = peakdtsamples.filter(sample=samples, peak__compound__in=annotated_compounds, peak__compound__secondaryId=secondary_id).order_by('-intensity').values_list('peak__id', flat=True).first()
    # p_max_intense_id = ac_compound_peakdtsamples.filter(peak__compound__secondaryId=secondary_id).order_by('-intensity').values_list('peak__id', flat=True).first()
    print p_max_intense_id

    max_compound_id = annotated_compounds.filter(peak__id=p_max_intense_id, secondaryId=secondary_id).values_list('id', flat=True).first()
    # print max_compound_id, p_max_intense_id

    best_compound = annotated_compounds.get(pk=max_compound_id)

    peak = best_compound.peak

    c_data.append(max_compound_id)
    c_data.append(peak.id)
    dbs = ['kegg', 'hmdb', 'lipidmaps']
    for db in dbs:
        c_name = best_compound.repositorycompound_set.filter(db_name=db)
        if len(c_name) != 0:
            c_data.append(c_name.first().compound_name)
            break

    c_data.append(best_compound.formula)

    # Get pathways
    pathway_ids = CompoundPathway.objects.filter(compound=best_compound).values_list('pathway__pathway__id', flat=True).distinct()
    if pathway_ids.exists():
        superpathways = DataSourceSuperPathway.objects.filter(pathway__id__in=pathway_ids).values_list('super_pathway__name', flat=True)
        if None not in superpathways or superpathways.count() > 0: #
            print superpathways
            try:
                joined_sp = " ".join(superpathways)
            except:
                joined_sp = "None"
            c_data.append(joined_sp) # superpathways
        else:
            c_data.append("None")
        c_data.append(" ".join(Pathway.objects.filter(id__in=pathway_ids).values_list('name', flat=True))) # pathways
    else:
        c_data.append("None") # no superpathways
        c_data.append("None") # no pathways

    peak_intensities_by_samples = peakdtsamples.filter(peak=peak, sample=samples).order_by('sample__attribute__id', 'sample__id').distinct()
    print peak

    for intensity in peak_intensities_by_samples.values_list('intensity', flat=True):
        c_data.append(str(intensity))  # individual sample intensities

    attribute_ids = set(samples.values_list('sampleattribute__attribute__id', flat=True))
    averages_by_group = []
    for attribute_id in attribute_ids:
        averages_by_group.append(peak_intensities_by_samples.filter(sample__sampleattribute__attribute__id=attribute_id).aggregate(Avg('intensity'))['intensity__avg'])

    c_data += averages_by_group
    c_data.append('annotated')
    print c_data

stop = timeit.default_timer()
print "metabolite table processing time: ", str(stop - start)
"""
response = simplejson.dumps({'aaData': data})

stop = timeit.default_timer()
print "metabolite table processing time: ", str(stop - start)
return HttpResponse(response, content_type='application/json')
"""
