# Create your views here.
import itertools
from django.shortcuts import render_to_response
from django.shortcuts import render
from experiments.models import *
from django.core.context_processors import csrf
from django.template import RequestContext  # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
# models
from projects.models import Project
from data.models import *
from compound.models import *
from groups.models import Attribute
from fileupload.models import Sample, CalibrationSample, Curve
# Add on
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.db.models import Avg

try:
    from django.utils import simplejson
except:
    import json as simplejson
from django.utils.safestring import mark_safe
import datetime
import numpy as np
from rpy2.robjects.packages import importr
from rpy2 import robjects

# Scikitlearn for the PCA
from sklearn.decomposition import PCA

from experiments.forms import *
# import mdp
# import matplotlib.pyplot as plt
# from management.pimpxml_parser.pimpxml_parser import Xmltree

# import sys
# temporary import
import os
# tasks
from experiments import tasks
# debug libraries
import timeit
import pickle
from django.views.decorators.cache import cache_page


def experiment(request, project_id):
    class RequiredComparisonFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredComparisonFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.fields['attribute1'].choices = [(c.id, c) for c in attributes]
                form.fields['attribute1'].choices.append(["Select condition", "Select condition"])
                form.fields['attribute1'].initial = "Select condition"
                form.fields['attribute2'].choices = [(c.id, c) for c in attributes]
                form.fields['name'].widget.attrs['readonly'] = True
                form.empty_permitted = False

    class RequiredParameterFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredParameterFormSet, self).__init__(*args, **kwargs)
            i = 0
            for form in self.forms:
                form.fields['value'].initial = default_parameters[i].value
                form.fields['value'].label = default_parameters[i].name
                form.fields['name'].initial = default_parameters[i].name
                form.fields['state'].required = True
                i += 1

    try:
        project = Project.objects.get(pk=project_id)
        user = request.user
        permission = project.userproject_set.get(user=user).permission
    except Project.DoesNotExist:
        raise Http404

    default_parameters = DefaultParameter.objects.all()
    ParametersFormSet = formset_factory(ParameterForm, extra=len(default_parameters), max_num=20,
                                        formset=RequiredParameterFormSet)

    groups = []
    attributes = []
    files = project.picture_set.all()
    samples = project.sample_set.all()
    # Create a list of all attributes in this project without duplucate
    for sample in samples:
        if sample.attribute_set.all():
            attributeSet = set(attributes).union(set(sample.attribute_set.all()))
            attributes = list(attributeSet)

    # Create a list "groups" of groups in this projects without duplicates
    for attribute in attributes:
        if attribute.group not in groups:
            groups.append(attribute.group)

    ref = []
    for group in groups:
        ref.append([att.id for att in group.attribute_set.all()])

    # Create json object of ref to load in template javascript
    if isinstance(ref, QuerySet):
        truc = mark_safe(serialize('json', ref))
    else:
        truc = mark_safe(simplejson.dumps(ref))

    # calcul of max number of combination
    combination = 0
    for group in ref:
        combination += len(list(itertools.combinations(group, 2)))

    ComparisonFormSet = formset_factory(ComparisonForm, extra=1, max_num=combination, formset=RequiredComparisonFormSet)

    """
    Check if standard exist for this project, if not, the choice will be removed from the form.
    """
    if Attribute.objects.filter(name="standard", calibrationsample__project=project):
        no_standard = False
    else:
        no_standard = True

    print "I am here!"
    if request.method == 'POST':
        experiment_form = ExperimentForm(request.POST)
        parameter_formset = ParametersFormSet(request.POST, request.FILES, prefix='parameters')
        comparison_formset = ComparisonFormSet(request.POST, request.FILES, prefix='attributes')
        database_form = DatabaseForm(request.POST)

        ################### DEBUG ############################################
        # print "something"
        # if experiment_form.is_valid():
        # 	print "experiment form is valid"
        # if parameter_formset.is_valid():
        # 	print "parameter form is valid"
        # if comparison_formset.is_valid():
        # 	print "comparison form is valid"

        # for form in comparison_formset.forms:
        # 	for field in form:
        # 		print field.errors
        print "experiment form"
        print experiment_form.is_valid()
        print "parameter "
        print parameter_formset.is_valid()
        print "comparison"
        print comparison_formset.is_valid()
        print "databases form"
        print database_form.is_valid()

        if experiment_form.is_valid() and parameter_formset.is_valid() and comparison_formset.is_valid() and database_form.is_valid():
            experiment = experiment_form.save()
            params = Params()
            params.save()
            for form in parameter_formset.forms:
                project.modified = datetime.datetime.now()
                project.save()
                dictio = form.cleaned_data
                ################ DEBUG ##################
                # if len(dictio.keys()) == 0 :
                # 	print "HHHHHHHHHHHHHHHH"
                # 	# print form.cleaned_data['value']
                # else :
                # 	print "value = ",form.cleaned_data['value']
                # 	print "state = ",form.cleaned_data['state']
                # 	print "name = ",form.cleaned_data['name']
                ############### END DEBUG ################
                value = form.cleaned_data['value']
                state = form.cleaned_data['state']
                name = form.cleaned_data['name']
                if value == None:
                    defaultValue = default_parameters.get(name=name).value
                    parameter = Parameter(state=state, name=name, value=defaultValue)
                    parameter.save()
                else:
                    parameter = Parameter(value=value, state=state, name=name)
                    parameter.save()
                params.param.add(parameter)



            # checkbox = request.POST.get('state', True)
            # print checkbox
            # print form.fields

            # if form.cleaned_data['value']:
            # print form.cleaned_data['value']
            # if form.cleaned_data['state']:
            # print form.cleaned_data['state']
            # else:
            # 	print "parameter form is NOT valid!"
            # 	print "errors : ",form.errors
            # print
            # print "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
            # print "parameter formset : ",parameter_formset
            # print
            # databases_ids = database_form.cleaned_data['databases']
            # for db_id in databases_ids:
            # 	params.databases.add(db_id)

            print "after databases added"

            params.save()
            user = request.user
            name = user.username
            analysis = Analysis(params=params, experiment=experiment, status="Ready", owner=name)
            analysis.save()
            for form in comparison_formset.forms:
                name = form.cleaned_data['name']
                comparison = Comparison(name=name, experiment=experiment)
                comparison.save()
                "comparison saved"
                print name
                # print name
                id_attribute_1 = form.cleaned_data['attribute1']
                print "attribute id : ", id_attribute_1
                attribute_1 = Attribute.objects.get(id=id_attribute_1)
                print "attribute found : ", attribute_1
                attribute_comp = AttributeComparison(control=False, attribute=attribute_1, comparison=comparison)
                attribute_comp.save()

                id_attribute_2 = form.cleaned_data['attribute2']
                attribute_2 = Attribute.objects.get(id=id_attribute_2)
                attribute_comp = AttributeComparison(control=True, attribute=attribute_2, comparison=comparison)
                attribute_comp.save()
            return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))
    else:
        # This is the GET request
        experiment_form = ExperimentForm()
        database_form = DatabaseForm(no_standards=no_standard)
        comparison_formset = ComparisonFormSet(prefix='attributes')
        parameter_formset = ParametersFormSet(prefix='parameters')

    c = {'experiment_form': experiment_form,
         'default_parameters': default_parameters,
         'comparison_formset': comparison_formset,
         'parameter_formset': parameter_formset,
         'project': project,
         'database_form': database_form,
         'permission': permission,
         'ref': truc,
         }
    c.update(csrf(request))
    return render(request, 'experiment/experimentCreation.html', c)


# def create_dataset(request, project_id, experiment_id):
# 	if request.method == 'GET':
# 		experiment = Experiment.objects.get(pk=experiment_id)
# 		print experiment.dataset_set.all()
# 		project = Project.objects.get(pk=project_id)
# 		print "PROUTi prouta"
# 		sourceFile = '/Users/yoanngloaguen/Documents/ideomWebSite/static/temp.xlsx'
# 		book = xlrd.open_workbook(sourceFile)
# 		print "sheet number : ",book.nsheets
# 		rawData = book.sheet_by_index(0)
# 		sampleNb = rawData.ncols-23
# 		dtSamples = []
# 		for i in range(3,3+sampleNb):
# 			print rawData.cell_value(rowx=0,colx=i)
# 			dt_sample_name = rawData.cell_value(rowx=0,colx=i)
# 			sample = Sample.objects.filter(project__id=project.id,name=dt_sample_name+str(".mzXML"))[0]
# 			print Sample.objects.filter(project__id=project.id,name=dt_sample_name+str(".mzXML"))[0]
# 		return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))

# def createdataset(request, file_path):
# 	pimpXmlFile = file_path
# 	xmltree = Xmltree(pimpXmlFile)
# 	print len(xmltree.allPeaks())

def start_analysis(request, project_id):
    # base = importr('base')
    # base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')
    # pimp = importr('PiMP')
    if request.is_ajax():
        analysis_id = int(request.GET['id'])
        analysis = Analysis.objects.get(pk=analysis_id)
        project = Project.objects.get(pk=project_id)
        user = request.user
        if analysis.status != "Ready":
            message = "The analysis has already been submitted"
            response = simplejson.dumps(message)
            return HttpResponse(response, content_type='application/json')
        else:
            comparisons = analysis.experiment.comparison_set.all()
            comparison_name = [str(comparison.name) for comparison in comparisons]
            samples = Sample.objects.filter(attribute__comparison__experiment__analysis=analysis).distinct()
            groups = Attribute.objects.filter(comparison__experiment__analysis=analysis).distinct()
            qc = CalibrationSample.objects.filter(project=project).filter(attribute__name="qc")
            blank = CalibrationSample.objects.filter(project=project).filter(attribute__name="blank")
            standard = CalibrationSample.objects.filter(project=project).filter(attribute__name="standard")
            pos_missing_samples = []
            neg_missing_samples = []
            for sample in samples:
                if not sample.samplefile.posdata:
                    pos_missing_samples.append(sample.name.split(".")[0])
                if not sample.samplefile.negdata:
                    neg_missing_samples.append(sample.name.split(".")[0])
            if not neg_missing_samples and not pos_missing_samples:
                pos_list = [str(sample.samplefile.posdata.file.path) for sample in samples]
                neg_list = [str(sample.samplefile.negdata.file.path) for sample in samples]
                # pos_list = [str(sample.samplefile.posdata.file.path) for sample in samples] + [str(sample.standardFile.posdata.file.path) for sample in qc] + [str(sample.standardFile.posdata.file.path) for sample in blank]
                # neg_list = [str(sample.samplefile.negdata.file.path) for sample in samples] + [str(sample.standardFile.negdata.file.path) for sample in qc] + [str(sample.standardFile.negdata.file.path) for sample in blank]
                file_list = {"positive": pos_list, "negative": neg_list}
                group_list = {}
                for group in groups:
                    group_list[str(group.name)] = [str(sample.name.split(".")[0]) for sample in group.sample.all()]
                # group_list["QC"] = [str(sample.name.split(".")[0]) for sample in qc]
                # group_list["Blank"] = [str(sample.name.split(".")[0]) for sample in blank]
                standards = [str(sample.standardFile.data.file.path) for sample in standard]
                databases = ["hmdb", "kegg", "lipidmaps"]
                analysis.status = 'Submitted'
                analysis.save(update_fields=['status'])

                analysis.submited = datetime.datetime.now()
                analysis.save(update_fields=['submited'])

                r = tasks.start_pimp_pipeline.delay(analysis, project, user)
                # r = tasks.start_pimp_pipeline.delay(comparison_name, file_list, group_list, standards, databases)
                # print r.get()
                # message = "The function has been disabled for maintanance"
                message = "Your analysis has been correctly submitted. The status update will be emailed to you."  # +str(r.task_id)
                data = {"status": "success", "message": message}
                response = simplejson.dumps(data)
                return HttpResponse(response, content_type='application/json')
            else:
                message = "Some samples are only present in one polarity, please add the following missing files: "
                data = {"status": "fail", "error": "missing file", "message": message,
                        "missing_neg": neg_missing_samples, "missing_pos": pos_missing_samples}
                response = simplejson.dumps(data)
                return HttpResponse(response, content_type='application/json')


def get_identification_table(request, project_id, analysis_id):
    if request.is_ajax():
        print "Metabolites table requested"
        start = timeit.default_timer()
        # project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        dataset = analysis.dataset_set.first()
        comparisons = analysis.experiment.comparison_set.all()
        num_comparisons = comparisons.count()
        samples = Sample.objects.filter(attribute=Attribute.objects.filter(comparison__in=comparisons).distinct().order_by('id')).distinct().order_by('attribute__id', 'id')

        data = []

        identified_compounds = Compound.objects.filter(identified='True', peak__dataset=dataset)
        ic_secondary_ids = identified_compounds.values_list('secondaryId', flat=True).distinct()

        for secondary_id in ic_secondary_ids:
            c_data = []

            # Select the most intense peak that has been identified by the compound
            # and use the logFC of this peak to represent the logfc with
            peaks_by_intensities = PeakDTSample.objects.filter(peak__dataset=dataset, sample__in=samples, peak__compound__secondaryId=secondary_id, peak__compound__in=identified_compounds).distinct().values_list('peak__id', flat=True)
            peaks_with_logfc = PeakDtComparison.objects.filter(peak__id__in=peaks_by_intensities).order_by('-peak__peakdtsample__intensity')

            if peaks_with_logfc.exists():
                best_peak_dtcomparison = peaks_with_logfc.first()
                best_peak_id = best_peak_dtcomparison.peak.id
                best_peak_logfcs = PeakDtComparison.objects.filter(peak__id=best_peak_id).order_by('comparison').values_list('logFC', flat=True)
            else:
                # print "No logFC for peak"
                best_peak_id = peaks_by_intensities.first()
                best_peak_logfcs = ["NA" for i in range(num_comparisons)]

            # print "Peak ID", best_peak_id
            # print "compound secondary ID", secondary_id
            max_compound_id = identified_compounds.filter(peak__id=best_peak_id, secondaryId=secondary_id).values_list('id', flat=True).first()

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
                    c_data.append(joined_sp)  # superpathways
                else:
                    c_data.append("None")
                c_data.append(" ".join(Pathway.objects.filter(id=pathway_ids).values_list('name', flat=True)))  # pathways
            else:
                c_data.append("None") # no superpathways
                c_data.append("None") # no pathways

            # Intensities of the peak across samples
            peak_intensities_by_samples = PeakDTSample.objects.filter(peak=peak).order_by('sample__attribute__id', 'sample__id').distinct()

            for intensity in peak_intensities_by_samples.values_list('intensity', flat=True):
                c_data.append(round(intensity, 2))  # individual sample intensities

            # # Average intensity of the peak across attributes
            # attribute_ids = set(samples.values_list('sampleattribute__attribute__id', flat=True))
            # averages_by_group = []
            # for attribute_id in attribute_ids:
            #     averages_by_group.append(peak_intensities_by_samples.filter(sample__sampleattribute__attribute__id=attribute_id).aggregate(Avg('intensity'))['intensity__avg'])
            #
            # for group_average in averages_by_group:
            #     c_data.append(round(group_average, 2))

            # print best_peak_logfcs

            for logfc in best_peak_logfcs:
                if logfc == "NA":
                    c_data.append(logfc)
                else:
                    c_data.append(round(logfc, 2))

            c_data.append('identified')
            # Add the compound information to data
            data.append(c_data)

        annotated_compounds = Compound.objects.filter(identified='False', peak__dataset=dataset).exclude(secondaryId__in=identified_compounds.values_list("secondaryId", flat=True))
        ac_secondary_ids = annotated_compounds.values_list('secondaryId', flat=True).distinct()

        # i = 0
        for secondary_id in ac_secondary_ids:
            # i += 1
            # if i == 10:
            #     break
            c_data = []

            # Select the most intense peak that has been identified by the compound
            # and use this to represent the compound
            peaks_by_intensities = PeakDTSample.objects.filter(peak__dataset=dataset, sample__in=samples, peak__compound__secondaryId=secondary_id, peak__compound__in=annotated_compounds).distinct().values_list('peak__id', flat=True)
            peaks_with_logfc = PeakDtComparison.objects.filter(peak__id__in=peaks_by_intensities).order_by('-peak__peakdtsample__intensity')

            if peaks_with_logfc.exists():
                # print "peak with logfc"
                best_peak_dtcomparison = peaks_with_logfc.first()
                best_peak_id = best_peak_dtcomparison.peak.id
                best_peak_logfcs = PeakDtComparison.objects.filter(peak__id=best_peak_id).order_by('comparison').values_list('logFC', flat=True)
            else:
                # print "No peak with logfc"
                best_peak_id = peaks_by_intensities.first()
                best_peak_logfcs = ["NA" for i in range(num_comparisons)]

            # print "peak id", best_peak_id
            # print "compound id", secondary_id
            max_compound_id = annotated_compounds.filter(peak__id=best_peak_id, secondaryId=secondary_id).values_list('id', flat=True).first()

            best_compound = annotated_compounds.get(pk=max_compound_id)

            peak = best_compound.peak

            # compound id
            c_data.append(str(max_compound_id))
            # peak id
            c_data.append(str(peak.id))
            # compound name
            dbs = ['kegg', 'hmdb', 'lipidmaps']
            for db in dbs:
                c_name = best_compound.repositorycompound_set.filter(db_name=db)
                if len(c_name) != 0:
                    c_data.append(c_name.first().compound_name)
                    break
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
                    c_data.append(joined_sp)  # superpathways
                else:
                    c_data.append("None")
                c_data.append(" ".join(Pathway.objects.filter(id=pathway_ids).values_list('name', flat=True)))  # pathways
            else:
                c_data.append("None") # no superpathways
                c_data.append("None") # no pathways

            # Intensities of the peak across samples
            peak_intensities_by_samples = PeakDTSample.objects.filter(peak=peak).order_by('sample__attribute__id', 'sample__id').distinct()

            for intensity in peak_intensities_by_samples.values_list('intensity', flat=True):
                c_data.append(round(intensity, 2))  # individual sample intensities

            # Average intensity of the peak across attributes
            # attribute_ids = set(samples.values_list('sampleattribute__attribute__id', flat=True))
            # averages_by_group = []
            # for attribute_id in attribute_ids:
            #     averages_by_group.append(peak_intensities_by_samples.filter(sample__sampleattribute__attribute__id=attribute_id).aggregate(Avg('intensity'))['intensity__avg'])
            #
            # for group_average in averages_by_group:
            #     c_data.append(round(group_average, 2))

            for logfc in best_peak_logfcs:
                if logfc == "NA":
                    c_data.append(logfc)
                else:
                    c_data.append(round(logfc, 2))

            c_data.append('annotated')
            # Add the compound information to data
            data.append(c_data)

        response = simplejson.dumps({'aaData': data})

        stop = timeit.default_timer()
        print "metabolite table processing time: ", str(stop - start)
        return HttpResponse(response, content_type='application/json')

    else:
        # return Http404
        pass

def get_metabolite_info(request, project_id, analysis_id):
    """
    AJAX view to return information on a metabolite.

    :param request: as well as the function parameters above, contains compound_id
    :param project_id:
    :param analysis_id:
    :return: HttpResponse containing JSON-formatted data; the mass, rt, intensities the peaks annotated or identified
    by the metabolite
    """
    if request.is_ajax():
        analysis = Analysis.objects.get(pk=analysis_id)
        dataset = analysis.dataset_set.first()
        comparisons = analysis.experiment.comparison_set.all()
        samples = Sample.objects.filter(
            attribute=Attribute.objects.filter(comparison__in=comparisons).distinct().order_by('id')).distinct().order_by(
            'attribute__id', 'id')
        peakdtsamples = PeakDTSample.objects.filter(peak__dataset=dataset)
        compound_id = int(request.GET['compound_id'])
        compound_secondary_id = Compound.objects.get(pk=compound_id).secondaryId

        peaks = Peak.objects.filter(dataset=dataset, compound__secondaryId=compound_secondary_id).order_by('secondaryId')

        attribute_ids = set(samples.values_list('sampleattribute__attribute__id', flat=True))
        peaks_data = []

        for peak in peaks:
            peaks_data.append([peak.id, str(round(peak.rt, 2)), str(round(peak.mass, 4)), str(peak.polarity), str(peak.type)])

            # peak_intensities_by_samples = peakdtsamples.filter(peak=peak).order_by('sample__attribute__id', 'sample__id').distinct()
            #
            # averages_by_group = []
            # for attribute_id in attribute_ids:
            #     averages_by_group.append(peak_intensities_by_samples.filter(sample__sampleattribute__attribute__id=attribute_id).aggregate(Avg('intensity'))['intensity__avg'])
            #
            # peak_data += averages_by_group
            # peaks_data.append(peak_data)

        print peaks_data
        response = simplejson.dumps({'aaData': peaks_data})
        return HttpResponse(response, content_type='application/json')


def get_peak_table(request, project_id, analysis_id):
    if request.is_ajax():
        print "peak table requested"
        start = timeit.default_timer()
        analysis = Analysis.objects.get(pk=analysis_id)
        project = Project.objects.get(pk=project_id)
        dataset = analysis.dataset_set.all()[0]
        comparisons = analysis.experiment.comparison_set.all()
        s = Sample.objects.filter(
            attribute=Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')).distinct().order_by(
            'attribute__id', 'id')
        p = list(PeakDTSample.objects.filter(sample=s, peak__dataset=dataset).distinct().order_by('peak__id',
                                                                                                  'sample__attribute__id',
                                                                                                  'sample__id'))
        pp = map(list, zip(*[iter(p)] * s.count()))
        data = [
            [str(peakgroup[0].peak.secondaryId), round(peakgroup[0].peak.mass, 4), round(peakgroup[0].peak.rt, 2)] + [
                round(peakdtsample.intensity, 2) if peakdtsample.intensity != 0 else 'NA' for peakdtsample in
                peakgroup] + [str(peakgroup[0].peak.polarity)] for peakgroup in pp]

        response = simplejson.dumps({"aaData": data})

        stop = timeit.default_timer()
        print "peak table processing time: ", str(stop - start)
        return HttpResponse(response, content_type='application/json')


# @cache_page(60 * 60 * 24 * 100)
@login_required
def analysis_result(request, project_id, analysis_id):
    if request.method == 'GET':
        try:
            project = Project.objects.get(pk=project_id)
            analysis = Analysis.objects.get(pk=analysis_id)
            user = request.user
            permission = project.userproject_set.get(user=user).permission
        except Project.DoesNotExist:
            raise Http404
        start = timeit.default_timer()
        comparisons = analysis.experiment.comparison_set.all()
        # print comparisons
        dataset = analysis.dataset_set.all()[0]
        compounds = Compound.objects.filter(peak__dataset=dataset)
        print dataset
        ######## Old query for members ########
        # member_set = set()
        # for comparison in comparisons:
        # 	member_set = member_set.union(set(comparison.attribute.all()))
        # member_list = list(member_set)
        ######## New query for members ########
        print "before SSSSSSSSS"
        s = Sample.objects.filter(
            attribute=Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')).distinct().order_by(
            'attribute__id', 'id')
        print "After SSSSSS before PPPPPPPP"
        # p = list(PeakDTSample.objects.filter(sample=s, peak__dataset=dataset).distinct().order_by('peak__id', 'sample__attribute__id', 'sample__id'))
        # print "len p:"
        # print len(p) #154368
        # print "After PPPPPPPP"
        member_list = list(Attribute.objects.filter(comparison=comparisons).distinct().order_by('id'))

        print "member list: ", member_list
        sample_member_hash = {}
        sample_list = []
        for member in member_list:
            sample_list.append(list(member.sample.all().order_by('id')))
            for sample in member.sample.all():
                sample_member_hash[sample] = member_list.index(member)
        print "sample member hash: ", sample_member_hash
        print "sample list: ", sample_list

        # print "Before PPPP2222222"
        # pp = map(list, zip(*[iter(p)]*s.count()))
        # print "After PPPPP222222"
        # peak_set = dataset.peak_set.all()
        # peak_table = {}
        # databases = []
        # pca_table = []
        # for peak in peak_set:
        # 	intensity_list = [[None]*len(samples) for samples in sample_list]#len(member_list)
        # 	for peak_dt_sample in peak.peakdtsample_set.all():
        # 		i = sample_member_hash[peak_dt_sample.sample]
        # 		print i
        # 		# print sample_list[i]
        # 		# print type(sample_list[i])
        # 		j = sample_list[i].index(peak_dt_sample.sample)
        # 		intensity_list[i][j] = peak_dt_sample
        # 	peak_table[peak] = intensity_list
        # 	pca_table.append([item.intensity for sublist in intensity_list for item in sublist])
        # if peak.secondaryId == 100:
        # 	break


        databases = RepositoryCompound.objects.filter(compound__peak__dataset=dataset).values_list('db_name',
                                                                                                   flat=True).distinct()

        print ("hah avant pca")

        ############################################################################
        ############################# PCA calculation ##############################
        ############################################################################
        pca_start = timeit.default_timer()
        pca_table = []
        for sample in s:
            pca_table.append(
                PeakDTSample.objects.filter(sample=sample, peak__dataset__analysis=analysis).distinct().order_by(
                    'peak__id').values_list('intensity', flat=True))

        pca_matrix = np.array(pca_table)
        # pca_table = np.array(pca_table)
        # pca_matrix = pca_table.T
        # print "pca_table :",pca_matrix
        index_of_zero = np.where(pca_matrix == 0)[1]
        # print "len pca matrix 1 :", len(pca_matrix[0])
        # print "index_of_zero : ",index_of_zero
        pca_matrix = np.delete(pca_matrix, index_of_zero, 1)
        # print "after delete : ",np.where(pca_matrix == 0)[1]
        log_pca_matrix = np.log2(pca_matrix)


        pca_obj = PCA(n_components=2,whiten=False)
        pca_obj.fit(log_pca_matrix)
        projected_data = pca_obj.transform(log_pca_matrix)
        explained_variance = []
        for i in range(2):
            explained_variance.append(100*pca_obj.explained_variance_ratio_[i])

        # print "len pca matrix 1 :", pca_matrix[0][0]
        # print "len log pca matrix 1 :", log_pca_matrix[0][0]
        # for yty in log_pca_matrix[0]:
        # 	print yty
        # pcan = mdp.nodes.PCANode(output_dim=3, svd=True)
        # pcar = pcan.execute(log_pca_matrix)


        # print "pcar ",pcar
        # print "pcan ",pcan.d[0],"  ",pcan.d[1]
        # print "pcan again",pcan.d
        # print "explained variance : ",pcan.explained_variance
        # nr, nc = log_pca_matrix.shape
        # xvec = robjects.FloatVector(log_pca_matrix.transpose().reshape((log_pca_matrix.size)))
        # xr = robjects.r.matrix(xvec, nrow=nr, ncol=nc)
        # stats = importr('stats', robject_translations={'format_perc': '_format_perc'})
        # pca = stats.prcomp(xr)

        # first_dim = list(pca.rx2['x'].rx(True, 1))
        # second_dim = list(pca.rx2['x'].rx(True, 2))

        # pca_info = [pcan.d[0],pcan.d[1]]
        pca_info = [None, None]
        pca_data_point = []
        i = 0
        j = 0


        for member in sample_list:
            pca_serie = [member_list[j].name]
            for sample in member:
                dic = []
                dic.append(sample.name)
                # dic.append(pcar[i][0])
                # dic.append(first_dim[i])
                # dic.append(second_dim[i])
                # dic.append(pca_obj.components_[0,i])
                # dic.append(pca_obj.components_[1,i])
                dic.append(projected_data[i,0])
                dic.append(projected_data[i,1])
                # dic.append(pcar[i][1])
                pca_serie.append(dic)
                i += 1
            pca_data_point.append(pca_serie)
            j += 1
        pca_info.append(pca_data_point)

        print "after pca"
        pca_stop = timeit.default_timer()

        print "pca_series: ",pca_data_point
        ############################################################################
        ########################## End PCA calculation #############################
        ############################################################################

        ############################################################################
        ########################## Best hits comparison ############################
        ############################################################################
        comp_start = timeit.default_timer()
        comparison_hits_list = {}
        for c in comparisons:
            identified_peak = Peak.objects.filter(dataset__analysis=analysis, compound__identified='True').distinct()
            annotated_peak = Peak.objects.filter(dataset__analysis=analysis).exclude(
                compound__identified='True').distinct()

            identified_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05).filter(
                peak__in=identified_peak).extra(select={"absLogFC": "abs(logFC)"}).order_by("-absLogFC")
            annotated_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05).filter(
                peak__in=annotated_peak).extra(select={"absLogFC": "abs(logFC)"}).order_by("-absLogFC")

            identified_info_list = []
            for identified_compound in identified_peakdtcomparisonList:
                compound_name = list(set(
                    RepositoryCompound.objects.filter(compound__peak__peakdtcomparison=identified_compound,
                                                      compound__identified="True").values_list('compound_name',
                                                                                               flat=True)))
                intensities = get_intensities_values(identified_compound)
                identified_info_list.append([identified_compound, compound_name, intensities])

            annotated_info_list = []
            for annotated_compound in annotated_peakdtcomparisonList:
                intensities = get_intensities_values(annotated_compound)
                annotated_info_list.append([annotated_compound, intensities])

            comparison_hits = [identified_info_list, annotated_info_list]
            comparison_hits_list[c] = comparison_hits
        # print "comparison hits: ",comparison_hits_list

        comp_stop = timeit.default_timer()

        ############################################################################
        ######################## End Best hits comparison ##########################
        ############################################################################


        # databases.sort()
        databases = map(str, databases)
        # print "databases: ",databases
        pathway_start = timeit.default_timer()

        pathways = Pathway.objects.filter(datasourcesuperpathway__data_source__name="kegg",
                                          datasourcesuperpathway__compoundpathway__compound__peak__dataset=dataset).distinct()
        print "pathway : ", len(pathways)
        pathway_list = []

        for pathway in pathways:
            identified = pathway.get_pathway_compounds(dataset_id=dataset.id, id_type="identified")
            annotated = pathway.get_pathway_compounds(dataset_id=dataset.id, id_type="annotated")
            info = [pathway, len(identified), len(annotated),
                    round(((len(identified) + len(annotated)) / float(DataSourceSuperPathway.objects.filter(pathway=pathway, data_source__name='kegg').first().compound_number)) * 100, 2),
                    [identified.keys(), annotated.keys()]]

            # secId = pathway.compound.filter(identified=True).values_list('secondaryId', flat=True).distinct()
            # secIdannot = pathway.compound.filter(identified=False).exclude(secondaryId__in=secId).values_list('secondaryId', flat=True).distinct()
            # da = pathway.compound.filter(identified=True, repositorycompound__db_name='kegg').values_list('repositorycompound__identifier',flat=True).distinct()
            # d = pathway.compound.filter(identified=False, repositorycompound__db_name='kegg').exclude(secondaryId__in=secId).values_list('repositorycompound__identifier',flat=True).distinct()
            # info = [pathway, len(da), len(secIdannot), round(((len(secId)+len(secIdannot))*100)/float(pathway.compoundNumber),2),[da,d]]
            pathway_list.append(info)

        # for pathway in pathways[:100]:
        # 	all_compounds = pathway.compound.all()
        # 	identified = 0
        # 	annotated = 0
        # 	identified_kegg_id = []
        # 	annotated_kegg_id = []
        # 	distinct_compound = set([c.secondaryId for c in all_compounds])
        # 	for secondary_compound_id in distinct_compound:
        # 		if "True" in pathway.compound.filter(secondaryId=secondary_compound_id).values_list('identified', flat=True):
        # 			identified += 1
        # 			compounds_list = pathway.compound.filter(secondaryId=secondary_compound_id)
        # 			tmp_id_list = RepositoryCompound.objects.filter(compound=compounds_list).filter(db_name='kegg').values_list('identifier',flat=True)
        # 			identified_kegg_id = identified_kegg_id + list(tmp_id_list)
        # 		else:
        # 			annotated += 1
        # 			compounds_list = pathway.compound.filter(secondaryId=secondary_compound_id)
        # 			tmp_id_list = RepositoryCompound.objects.filter(compound=compounds_list).filter(db_name='kegg').values_list('identifier',flat=True)
        # 			annotated_kegg_id = annotated_kegg_id + list(tmp_id_list)
        # 	coverage = round(((annotated+identified)*100)/float(pathway.compoundNumber),2)
        # 	info = [pathway,identified,annotated,coverage,[list(set(identified_kegg_id)),list(set(annotated_kegg_id))]]
        # 	pathway_list.append(info)
        # print "pathway len ",len(pathway_list)
        pathway_stop = timeit.default_timer()
        # print "pathway list ",pathway_list[0]
        # print "compound number ",pathway_list[0][0].compoundNumber

        peak_comparison_list = Peak.objects.filter(peakdtcomparison__comparison__in=comparisons,
                                                   dataset__analysis=analysis).distinct()

        ##potetial hits that can't do statistics on.
        potential_hits = []
        # peaks = Peak.objects.filter(dataset__analysis=analysis)
        # for peak in peaks:
        #  	peak_comparisons = peak.peakdtcomparison_set.all()
        #  	if len(peak_comparisons) < len(comparisons): ##number of comparisons
        #  		missing_comparisons = comparisons.exclude(id__in=peak.peakdtcomparison_set.values_list("comparison_id"))
        #  		for comparison in missing_comparisons:
        #  			groups = comparison.attribute.all()
        #  			if peak._minimum_intensities_present(groups[0].sample.all()) or peak._minimum_intensities_present(groups[1].sample.all()):
        # 				potential_hits.append([peak.id, peak.mass, peak.rt, groups[0].name + " / " + groups[1].name])

        print "apres comparison peak machin chose"
        stop = timeit.default_timer()

        print "processing time : ", str(stop - start)
        print "pca generation : ", str(pca_stop - pca_start)
        print "comp time: ", str(comp_stop - comp_start)
        print "pathway time", str(pathway_stop - pathway_start)
        # print intensity_list
        # print intensity_list[0]

        # Get the TICs
        tics = {}
        for attribute in member_list:
            tics[attribute] = create_member_tic(attribute.id)

        c = {'member_list': member_list,
             'sample_list': sample_list,
             'pathway_list': pathway_list,
             'databases': databases,
             'dataset': dataset,
             # 'peak_table': pp,
             # 'compounds': compounds,
             'project': project,
             'analysis': analysis,
             'peak_comparison_list': peak_comparison_list,
             'comparisons': comparisons,
             'pca_data_point': pca_info,
             'comparison_hits_list': comparison_hits_list,
             'potential_hits': potential_hits,
			'tics':tics,
			'explained_variance':explained_variance,
             }
        # print len(peak_set)
        return render(request, 'base_result3.html', c)


def get_pathway_url(request, project_id, analysis_id):
    if request.is_ajax():
        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        dataset_id = analysis.dataset_set.first().id
        pathway_id = int(request.GET['id'])
        pathway = Pathway.objects.get(pk=pathway_id)

        try:
            requested_comparison_id = int(request.GET['comparison'])
        # print "comparison ",requested_comparison
        except:
            requested_comparison_id = None
            print "no comparison specified"

        pathway_map = pathway.get_pathway_url(dataset_id, requested_comparison_id)

        print pathway_map

        response = simplejson.dumps({'pathway_map': pathway_map})

        return HttpResponse(response, content_type='application/json')


def get_intensities_values(peakdtcomparison):
    peak = peakdtcomparison.peak
    comparison = peakdtcomparison.comparison

    member_set = set()
    member_set = member_set.union(set(comparison.attribute.all()))

    member_list = list(member_set)
    member_hash = {}
    for member in member_list:
        intensity_list = []
        for sample in member.sample.all():
            peak_intensity = sample.peakdtsample_set.get(peak=peak)
            intensity_list.append(peak_intensity.intensity)

        # print sample.name
        # print peak_intensity.intensity
        member_hash[member.name] = intensity_list
    data = []
    for member in member_hash.iterkeys():
        intensities = filter(lambda a: a != 0, member_hash[member])
        if len(intensities) > 1:
            array = np.array(intensities)
            mean = np.mean(array)
            std = np.std(array, axis=0)
            memberInfo = [str(member), mean, std]
            data.append(memberInfo)
        elif len(intensities) == 1:
            memberInfo = [str(member), intensities[0], None]
            data.append(memberInfo)
    # print "data : ",data
    return data


def get_metexplore_info(request, project_id, analysis_id):
    if request.is_ajax():
        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        identified_peak = Peak.objects.filter(dataset__analysis=analysis_id, compound__identified='True')

        comparisons = analysis.experiment.comparison_set.all()

        member_set = set()
        for comparison in comparisons:
            member_set = member_set.union(set(comparison.attribute.all()))
        member_list = list(member_set)
        # print member_list

        compound_data_list = []
        testdata = []
        nameIn = []

        for peak in identified_peak:
            compounds_identified = RepositoryCompound.objects.filter(compound__peak=peak, compound__identified='True',
                                                                     db_name='stds_db')

            if str(compounds_identified[0].compound_name) not in nameIn:
                print compounds_identified[:1]
                for compound in compounds_identified[:1]:
                    member_hash = {}
                    for member in member_list:
                        intensity_list = []
                        for sample in member.sample.all():
                            peak_intensity = sample.peakdtsample_set.get(peak=peak)
                            intensity_list.append(peak_intensity.intensity)

                        # print sample.name
                        # print peak_intensity.intensity
                        member_hash[member.name] = intensity_list
                    # print member_hash
                    hash_data = {}
                    data = []
                    for member in member_hash.iterkeys():
                        intensities = filter(lambda a: a != 0, member_hash[member])
                        if len(intensities) > 1:
                            array = np.array(intensities)
                            mean = np.mean(array)
                            hash_data[str(member)] = int(mean)
                            data.append(int(mean))
                        elif len(intensities) == 1:
                            hash_data[str(member)] = int(intensities[0])
                            data.append(int(intensities[0]))
                        elif len(intensities) == 0:
                            hash_data[str(member)] = 0
                            data.append(0)
                    # print data
                    nameIn.append(str(compound.compound_name))
                    compound_data_list.append({"name": str(compound.compound_name), "conditions": data})
                    testdata.append({compound.compound_name: hash_data})

        # print "COMPOUND DATA"
        # print compound_data_list
        # print testdata
        message = "got somthing on the server!!!"
        response = simplejson.dumps(compound_data_list)

        return HttpResponse(response, content_type='application/json')

    # identified_peakdtcomparisonList = c.peakdtcomparison_set.filter(peak__in=identified_peak)


def peak_info(request, project_id, analysis_id):
    if request.is_ajax():
        compound_id = int(request.GET['id'])
        compound = Compound.objects.get(pk=compound_id)
        peak = compound.peak

        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        comparisons = analysis.experiment.comparison_set.all()

        member_set = set()
        for comparison in comparisons:
            member_set = member_set.union(set(comparison.attribute.all()))
        member_list = list(member_set)
        print member_list
        member_hash = {}
        for member in member_list:
            intensity_list = []
            sample_list = []
            for sample in member.sample.all():
                peak_intensity = sample.peakdtsample_set.get(peak=peak)
                intensity_list.append(peak_intensity.intensity)
                sample_list.append(str(sample.name).split(".")[0])
            # print sample.name
            # print peak_intensity.intensity
            member_hash[member.name] = [intensity_list, sample_list]
        print member_hash
        data = []
        for member in member_hash.iterkeys():
            intensities = filter(lambda a: a != 0, member_hash[member][0])
            print "intensities :"
            print intensities
            if len(intensities) > 1:
                array = np.array(intensities)
                mean = np.mean(array)
                std = np.std(array, axis=0)
                memberInfo = [str(member), mean, std, member_hash[member]]
                data.append(memberInfo)
            elif len(intensities) == 1:
                memberInfo = [str(member), intensities[0], None, member_hash[member]]
                data.append(memberInfo)
        print "BBBbbbbbBBBBBBBBBBBBBBBBBBB"
        print data
        # PeakQCSample objects for blank samples only
        peakblanksamples = PeakQCSample.objects.filter(peak=peak, sample__attribute__name="blank")
        if peakblanksamples:
            print "here peak blank samples:"
            print peakblanksamples
            blank_intensity_list = []
            blank_list = []
            for blank_sample in peakblanksamples:
                blank_intensity_list.append(blank_sample.intensity)
                blank_list.append(str(blank_sample.sample.name).split(".")[0])
            blank_info = [blank_intensity_list, blank_list]

            blank_intensities = filter(lambda a: a != 0, blank_info[0])
            print "blank intensities :"
            print blank_intensities
            blankInfo = []
            if len(blank_intensities) > 1:
                array = np.array(blank_intensities)
                mean = np.mean(array)
                std = np.std(array, axis=0)
                blankInfo = ["blank", mean, std, blank_info]
            elif len(blank_intensities) == 1:
                blankInfo = ["blank", blank_intensities[0], None, blank_info]
            else:
                blankInfo = ["blank", 0, None, blank_info]
        else:
            blankInfo = None

        print blankInfo
        data_hash = {"samples": data, "blanks": blankInfo}
        print data_hash

        message = "got somthing on the server!!!"
        response = simplejson.dumps(data_hash)

        # message = "got somthing on the server!!!"
        # response = simplejson.dumps(data)

        return HttpResponse(response, content_type='application/json')


def peak_info_peak_id(request, project_id, analysis_id):
    if request.is_ajax():
        peak_id = int(request.GET['id'])

        try:
            requested_comparison_id = int(request.GET['comparison'])
            requested_comparison = Comparison.objects.get(pk=requested_comparison_id)
            print "comparison ", requested_comparison
        except:
            requested_comparison = None
            print "no comparison specified"

        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        peak = analysis.dataset_set.all()[0].peak_set.get(secondaryId=peak_id)
        comparisons = analysis.experiment.comparison_set.all()

        member_set = set()
        if requested_comparison:
            member_set = member_set.union(set(requested_comparison.attribute.all()))
        else:
            for comparison in comparisons:
                member_set = member_set.union(set(comparison.attribute.all()))
        member_list = list(member_set)
        print member_list
        member_hash = {}
        for member in member_list:
            intensity_list = []
            sample_list = []
            for sample in member.sample.all():
                peak_intensity = sample.peakdtsample_set.get(peak=peak)
                intensity_list.append(peak_intensity.intensity)
                sample_list.append(str(sample.name).split(".")[0])
            # print sample.name
            # print peak_intensity.intensity
            member_hash[member.name] = [intensity_list, sample_list]
        print member_hash
        data = []
        for member in member_hash.iterkeys():
            intensities = filter(lambda a: a != 0, member_hash[member][0])
            if len(intensities) > 1:
                array = np.array(intensities)
                mean = np.mean(array)
                std = np.std(array, axis=0)
                memberInfo = [str(member), mean, std, member_hash[member]]
                data.append(memberInfo)
            elif len(intensities) == 1:
                memberInfo = [str(member), intensities[0], None, member_hash[member]]
                data.append(memberInfo)
        print data
        # PeakQCSample objects for blank samples only
        peakblanksamples = PeakQCSample.objects.filter(peak=peak, sample__attribute__name="blank")
        if peakblanksamples:
            print "here peak blank samples:"
            print peakblanksamples
            blank_intensity_list = []
            blank_list = []
            for blank_sample in peakblanksamples:
                blank_intensity_list.append(blank_sample.intensity)
                blank_list.append(str(blank_sample.sample.name).split(".")[0])
            blank_info = [blank_intensity_list, blank_list]

            blank_intensities = filter(lambda a: a != 0, blank_info[0])
            print "blank intensities :"
            print blank_intensities
            blankInfo = []
            if len(blank_intensities) > 1:
                array = np.array(blank_intensities)
                mean = np.mean(array)
                std = np.std(array, axis=0)
                blankInfo = ["blank", mean, std, blank_info]
            elif len(blank_intensities) == 1:
                blankInfo = ["blank", blank_intensities[0], None, blank_info]
            else:
                blankInfo = ["blank", 0, None, blank_info]
        else:
            blankInfo = None

        print blankInfo
        data_hash = {"samples": data, "blanks": blankInfo}
        print data_hash

        message = "got somthing on the server!!!"
        response = simplejson.dumps(data_hash)

        # message = "got somthing on the server!!!"
        # response = simplejson.dumps(data)

        return HttpResponse(response, content_type='application/json')


def get_peaks_from_compound(request, project_id, analysis_id):
    if request.is_ajax():
        compound_id = int(request.GET['id'])
        ppm = float(request.GET['ppm'])
        rtWindow = float(request.GET['rtwindow'])

        compound = Compound.objects.get(pk=compound_id)
        peak = compound.peak

        polarity = peak.polarity
        rt = float(peak.rt)
        mass = float(peak.mass)

        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        comparisons = analysis.experiment.comparison_set.all()
        member_set = set()
        for comparison in comparisons:
            member_set = member_set.union(set(comparison.attribute.all()))
        member_list = list(member_set)
        print member_list

        sample_list = []
        for member in member_list:
            sample_list.append(list(member.sample.all()))
        print sample_list

        print "peak id", peak.id
        print polarity
        print rt
        print mass

        massWindow = mass * ppm * 0.000001
        print "after mass window"
        massUp = mass + massWindow
        massLow = mass - massWindow
        rtUp = rt + rtWindow / 2
        rtLow = rt - rtWindow / 2
        print "after rtLow"
        u = robjects.FloatVector([massLow, massUp])
        mzrange = robjects.r['matrix'](u, ncol=2)
        w = robjects.FloatVector([rtLow, rtUp])
        rtrange = robjects.r['matrix'](w, ncol=2)
        xcms = importr("xcms")

        # sample_ids = [560,561,562,563,564,565,566,567,568]
        data = [[polarity, rt, mass]]
        for member in sample_list:
            for sample in member:
                name = sample.name.split(".")[0]
                # print "name: ",name
                if polarity == "negative":
                    mzxmlfile = sample.samplefile.negdata
                else:
                    mzxmlfile = sample.samplefile.posdata
                file = xcms.xcmsRaw(mzxmlfile.file.path)
                # print "file opened"
                # print "mzrange: ",mzrange
                # print "rtrange: ",rtrange
                y = xcms.rawMat(file, mzrange, rtrange)
                # print "Y : ",y
                lineList = []
                try:
                    time = list(y.rx(True, 1))
                    # print "time"
                    intensity = list(y.rx(True, 3))
                    for i in range(len(intensity)):
                        lineList.append([float(time[i]), round(float(intensity[i]), 3)])
                except:
                    lineList = None
                    print "EXCEPTION TRIGGERED!!!!!"
                # print lineList
                data.append([name, lineList])
            # print data
        message = "got somthing on the server for peaks chromatogram!!!"
        response = simplejson.dumps(data)
        return HttpResponse(response, content_type='application/json')


def my_new_view(requet, project_id, analysis_id):
    if request.is_ajax():
        peak_id = int(request.GET['id'])
        ppm = float(request.GET['ppm'])
        rtWindow = float(request.GET['rtwindow'])

        mass = float(peak.mass)
        u = robjects.FloatVector([massLow, massUp])
        mzrange = robjects.r['matrix'](u, ncol=2)
        w = robjects.FloatVector([rtLow, rtUp])
        rtrange = robjects.r['matrix'](w, ncol=2)
        xcms = importr("xcms")


def get_peaks_from_peak_id(request, project_id, analysis_id):
    if request.is_ajax():
        peak_id = int(request.GET['id'])
        ppm = float(request.GET['ppm'])
        rtWindow = float(request.GET['rtwindow'])

        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        peak = analysis.dataset_set.all()[0].peak_set.get(secondaryId=peak_id)

        rt = float(peak.rt)
        mass = float(peak.mass)
        polarity = peak.polarity
        comparisons = analysis.experiment.comparison_set.all()
        member_set = set()
        for comparison in comparisons:
            member_set = member_set.union(set(comparison.attribute.all()))
        member_list = list(member_set)
        print member_list

        sample_list = []
        for member in member_list:
            sample_list.append(list(member.sample.all()))
        print sample_list

        print "peak id", peak.id
        print polarity
        print rt
        print mass

        massWindow = mass * ppm * 0.000001
        print "after mass window"
        massUp = mass + massWindow
        massLow = mass - massWindow
        rtUp = rt + rtWindow / 2
        rtLow = rt - rtWindow / 2
        print "after rtLow"
        u = robjects.FloatVector([massLow, massUp])
        mzrange = robjects.r['matrix'](u, ncol=2)
        w = robjects.FloatVector([rtLow, rtUp])
        rtrange = robjects.r['matrix'](w, ncol=2)
        xcms = importr("xcms")

        # sample_ids = [560,561,562,563,564,565,566,567,568]
        data = [[polarity, rt, mass]]
        for member in sample_list:
            for sample in member:
                name = sample.name.split(".")[0]
                print "name: ", name
                if polarity == "negative":
                    mzxmlfile = sample.samplefile.negdata
                else:
                    mzxmlfile = sample.samplefile.posdata
                file = xcms.xcmsRaw(mzxmlfile.file.path)
                print "file opened"
                print "mzrange: ", mzrange
                print "rtrange: ", rtrange
                y = xcms.rawMat(file, mzrange, rtrange)
                # print "Y : ",y
                lineList = []
                try:
                    time = list(y.rx(True, 1))
                    # print "time"
                    intensity = list(y.rx(True, 3))
                    for i in range(len(intensity)):
                        lineList.append([float(time[i]), round(float(intensity[i]), 3)])
                except:
                    lineList = None
                    print "EXCEPTION TRIGGERED!!!!!"
                # print lineList
                data.append([name, lineList])
                print data
        message = "got somthing on the server for peaks chromatogram!!!"
        response = simplejson.dumps(data)
        return HttpResponse(response, content_type='application/json')


def compound_info(request, project_id, analysis_id):
    if request.is_ajax():
        compound_id = int(request.GET['id'])
        compound = Compound.objects.get(pk=compound_id)
        data = [compound.adduct, compound.inchikey]
        for repo in compound.repositorycompound_set.all():
            repoInfo = []
            repoInfo = [repo.db_name, repo.compound_name, repo.identifier]
            data.append(repoInfo)
        message = "got somthing on the server!!!"
        response = simplejson.dumps(data)
        return HttpResponse(response, content_type='application/json')


def get_compounds_from_peak_id(request, project_id, analysis_id):
    if request.is_ajax():
        peak_id = int(request.GET['id'])

        project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        peak = analysis.dataset_set.all()[0].peak_set.get(secondaryId=peak_id)

        compoundsList = []

        # print "peak here",peak

        for compound in peak.compound_set.all():
            # print "blblblblblbl"
            names = compound.repositorycompound_set.all().values_list('compound_name', flat=True).distinct()
            print "names lalalalalalala ", names
            distinct_names = list(set([x.lower() for x in names]))
            compoundsList.append(distinct_names)

        print "compoundList herererererere", compoundsList

        message = "Blaaaaaaa got somthing on the server!!!"
        response = simplejson.dumps(compoundsList)
        return HttpResponse(response, content_type='application/json')


def create_member_tic(attribute_id):
    attribute = Attribute.objects.get(id=attribute_id)
    attribute_name = attribute.name
    sampleList = attribute.sample.all()

    sampleCurveList = {}

    for sample in sampleList:
        sample_name = sample.name
        if not sample.samplefile.posdata:
            posdata = "None"
        else:
            posmzxmlfile = sample.samplefile.posdata
            if not posmzxmlfile.tic:
                print "over here"
                posdata = getIntensity(posmzxmlfile)
                # print "posdata ",[i[0] for i in posdata]
                x_axis = [i[0] for i in posdata]
                y_axis = [i[1] for i in posdata]
                x = pickle.dumps(x_axis)
                y = pickle.dumps(y_axis)
                mean = np.mean(y_axis)
                median = np.median(y_axis)
                print "pos median : ", median
                print "pos mean : ", mean
                posBarTic = [mean, median]

                # print x

                print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"

                curve = Curve.objects.create(x_axis=x, y_axis=y, mean=mean, median=median)
                curve.save()
                posmzxmlfile.tic = curve
                posmzxmlfile.save()

                print posmzxmlfile.tic.x_axis
            # posintensity = posdata[0]
            # postime = posdata[1]
            else:
                print "tic exist"
                # print str(posmzxmlfile.tic.x_axis)
                x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
                y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
                print "pos median : ", posmzxmlfile.tic.median
                print "pos mean : ", posmzxmlfile.tic.mean
                posBarTic = [posmzxmlfile.tic.mean, posmzxmlfile.tic.median]
                posdata = []
                print "after loads"
                for i in range(len(x_axis)):
                    posdata.append([float(x_axis[i]), float(y_axis[i])])
                print "after for"
            # print posdata
        if not sample.samplefile.negdata:
            negdata = "None"
        else:
            negmzxmlfile = sample.samplefile.negdata
            if not negmzxmlfile.tic:
                print "over there :)"
                negdata = getIntensity(negmzxmlfile)
                x_axis = [i[0] for i in negdata]
                y_axis = [i[1] for i in negdata]
                x = pickle.dumps(x_axis)
                y = pickle.dumps(y_axis)
                mean = np.mean(y_axis)
                median = np.median(y_axis)
                print "neg median : ", median
                print "neg mean : ", mean
                negBarTic = [mean, median]

                curve = Curve.objects.create(x_axis=x, y_axis=y, mean=mean, median=median)
                curve.save()
                negmzxmlfile.tic = curve
                negmzxmlfile.save()
            else:
                print "tic exist"
                x_axis = pickle.loads(str(negmzxmlfile.tic.x_axis))
                y_axis = pickle.loads(str(negmzxmlfile.tic.y_axis))
                print "neg median : ", negmzxmlfile.tic.median
                print "neg mean : ", negmzxmlfile.tic.mean
                negBarTic = [negmzxmlfile.tic.mean, negmzxmlfile.tic.median]
                negdata = []
                for i in range(len(x_axis)):
                    negdata.append([float(x_axis[i]), float(y_axis[i])])
        # fileList = [sample_name,posdata,negdata,posBarTic,negBarTic]
        fileList = {'pos': posdata, 'neg': negdata}
        sampleCurveList[sample_name] = fileList

    # print attributeResponse
    # ++++++++++++++++++++++++++++++++++++++ Previous version of group tic creation ++++++++++++++++++++++++++++++++++++++
    # if not Attribute.objects.get(id=attribute_id).ticgroup.postic :
    # 	posticfile = "None"
    # else:
    # 	posticfile = Attribute.objects.get(id=attribute_id).ticgroup.postic.ticplot
    # 	# print posticfile
    # if not Attribute.objects.get(id=attribute_id).ticgroup.negtic :
    # 	negticfile = "None"
    # else:
    # 	negticfile = Attribute.objects.get(id=attribute_id).ticgroup.negtic.ticplot
    # fileList = [attribute_name,posticfile,negticfile]
    # attributeResponse = [attribute_name, sampleCurveList]
    return sampleCurveList


def getIntensity(mzxmlFile):
    xcms = importr("xcms")
    intensity = []
    file = xcms.xcmsRaw(mzxmlFile.file.path)
    print "file opened"
    intensity = [int(i) for i in list(file.do_slot("tic"))]
    time = [str(i) for i in list(file.do_slot("scantime"))]
    print "intensity list created"
    # scan = xcms.getScan(file, 1)
    # print "scan : ",scan
    # print intensity
    # print time
    lineList = []
    for i in range(len(intensity)):
        lineList.append([float(time[i]), intensity[i]])
    # print lineList
    return lineList
