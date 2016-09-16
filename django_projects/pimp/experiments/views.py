# Create your views here.
import itertools
import logging
from collections import OrderedDict

from django.shortcuts import render_to_response
from django.shortcuts import render
from experiments.models import *
from django.core.context_processors import csrf
from django.template import RequestContext  # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.db.models import Count
# models
from projects.models import Project
from data.models import *
from compound.models import *
from groups.models import Attribute
from fileupload.models import Sample, CalibrationSample, Curve
from frank.models import PimpFrankPeakLink
from frank.models import Peak as FrankPeak
# Add on
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.db.models import Avg, Max, Q
from __builtin__ import True
from Carbon.Aliases import true

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
# from pimp.profiler import profile
logger = logging.getLogger(__name__)

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

    logger.info("I am here!")
    if request.method == 'POST':
        experiment_form = ExperimentForm(request.POST)
        parameter_formset = ParametersFormSet(request.POST, request.FILES, prefix='parameters')
        comparison_formset = ComparisonFormSet(request.POST, request.FILES, prefix='attributes')
        database_form = DatabaseForm(request.POST)

        ################### DEBUG ############################################
        # print "something"
        # if experiment_form.is_valid():
        #     print "experiment form is valid"
        # if parameter_formset.is_valid():
        #     print "parameter form is valid"
        # if comparison_formset.is_valid():
        #     print "comparison form is valid"

        # for form in comparison_formset.forms:
        #     for field in form:
        #         print field.errors
        logger.info("experiment form")
        logger.info(experiment_form.is_valid())
        logger.info("parameter ")
        logger.info(parameter_formset.is_valid())
        logger.info("comparison")
        logger.info(comparison_formset.is_valid())
        logger.info("databases form")
        logger.info(database_form.is_valid())

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
                #     print "HHHHHHHHHHHHHHHH"
                #     # print form.cleaned_data['value']
                # else :
                #     print "value = ",form.cleaned_data['value']
                #     print "state = ",form.cleaned_data['state']
                #     print "name = ",form.cleaned_data['name']
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
            #     print "parameter form is NOT valid!"
            #     print "errors : ",form.errors
            # print
            # print "IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII"
            # print "parameter formset : ",parameter_formset
            # print
            databases_ids = database_form.cleaned_data['databases']
            for db_id in databases_ids:
                params.databases.add(db_id)

            logger.info("after databases added")

            params.save()
            user = request.user
            name = user.username
            analysis = Analysis(params=params, experiment=experiment, status="Ready", owner=name)
            analysis.save()
            for form in comparison_formset.forms:
                name = form.cleaned_data['name']
                comparison = Comparison(name=name, experiment=experiment)
                comparison.save()
                logger.info(name)
                # print name
                id_attribute_1 = form.cleaned_data['attribute1']
                logger.info("attribute id : %s", id_attribute_1)
                attribute_1 = Attribute.objects.get(id=id_attribute_1)
                logger.info("attribute found : %s", attribute_1)
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
#     if request.method == 'GET':
#         experiment = Experiment.objects.get(pk=experiment_id)
#         print experiment.dataset_set.all()
#         project = Project.objects.get(pk=project_id)
#         print "PROUTi prouta"
#         sourceFile = '/Users/yoanngloaguen/Documents/ideomWebSite/static/temp.xlsx'
#         book = xlrd.open_workbook(sourceFile)
#         print "sheet number : ",book.nsheets
#         rawData = book.sheet_by_index(0)
#         sampleNb = rawData.ncols-23
#         dtSamples = []
#         for i in range(3,3+sampleNb):
#             print rawData.cell_value(rowx=0,colx=i)
#             dt_sample_name = rawData.cell_value(rowx=0,colx=i)
#             sample = Sample.objects.filter(project__id=project.id,name=dt_sample_name+str(".mzXML"))[0]
#             print Sample.objects.filter(project__id=project.id,name=dt_sample_name+str(".mzXML"))[0]
#         return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))

# def createdataset(request, file_path):
#     pimpXmlFile = file_path
#     xmltree = Xmltree(pimpXmlFile)
#     print len(xmltree.allPeaks())

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

def get_metabolites_table(request, project_id, analysis_id):
    if request.is_ajax():
        logger.info("Metabolites table requested")
        start = timeit.default_timer()
        # project = Project.objects.get(pk=project_id)
        analysis = Analysis.objects.get(pk=analysis_id)
        dataset = analysis.dataset_set.first()
        comparisons = analysis.experiment.comparison_set.all()
        num_comparisons = comparisons.count()
        samples = Sample.objects.filter(attribute=Attribute.objects.filter(comparison__in=list(comparisons)).distinct().order_by('id')).distinct().order_by('attribute__id', 'id')

        data = []
        c_data = []

        identified_compounds = Compound.objects.filter(identified='True', peak__dataset=dataset)
        # list(identified_compounds)
        ic_secondary_ids = identified_compounds.values_list('secondaryId', flat=True).distinct()

        sample_map = [sample.id for sample in samples]
        new_test_start = timeit.default_timer()

        test = PeakDtComparison.objects.filter(peak__compound__in=list(identified_compounds)).order_by('peak__compound__secondaryId','-peak__peakdtsample__intensity','comparison').values_list('peak__compound__secondaryId','peak__id','comparison__id', 'peak__peakdtsample__sample__id','peak__compound__id','peak__secondaryId','peak__compound__formula','peak__peakdtsample__intensity','logFC','peak__peakdtsample__id').distinct()
        identified_compound_pathway_list = identified_compounds.order_by("secondaryId").values_list("secondaryId", "compoundpathway__pathway__pathway__name").distinct()
        pathway_super_pathway_list = Pathway.objects.all().values_list("name","datasourcesuperpathway__super_pathway__name")

        superpathway_dict = {}

        for pathway_name in pathway_super_pathway_list:
            if pathway_name[0] in superpathway_dict:
                if pathway_name[1] not in superpathway_dict[pathway_name[0]]:
                    superpathway_dict[pathway_name[0]] = " ".join([superpathway_dict[pathway_name[0]], pathway_name[1]])
            else:
                if pathway_name[1] == None:
                    superpathway_dict[pathway_name[0]] = "None"
                else:
                    superpathway_dict[pathway_name[0]] = pathway_name[1]

        pathway_name_dict = {}
        # Create dictionnary with pathway names for each compound
        for pathway_name in identified_compound_pathway_list:
            #
            if pathway_name[0] in pathway_name_dict:
                if pathway_name[1] not in pathway_name_dict[pathway_name[0]][0]:
                    pathway_name_dict[pathway_name[0]][0] = " ".join([pathway_name_dict[pathway_name[0]][0], pathway_name[1]])
                    pathway_name_dict[pathway_name[0]][1] = " ".join([pathway_name_dict[pathway_name[0]][1], superpathway_dict[pathway_name[1]]])
            else:
                if pathway_name[1] == None:
                    pathway_name_dict[pathway_name[0]] = ["None","None"]
                else:
                    pathway_name_dict[pathway_name[0]] = [pathway_name[1],  superpathway_dict[pathway_name[1]]]

        # print pathway_name_dict

        list(test)
        current_compound = None
        current_peak = None
        comparison_id_list = None
        sample_id_list = None
        first = True

        for i in range(len(test)):
            if test[i][0] != current_compound:
                if not first:
                    id_status = 'identified+fragment' if has_frank_annotation(current_peak) else 'identified'
                    c_data = [compound_id,peak_secondary_id,compound_name,formula,super_pathway_names,pathway_names] + intensity_list + logfc_list + [id_status]
                    data.append(c_data)
                else:
                    first = False
                current_compound = test[i][0]
                current_peak = test[i][1]
                comparison_id_list = [test[i][2]]
                sample_id_list = [test[i][3]]
                compound_id = test[i][4]
                peak_secondary_id = test[i][5]
                formula = test[i][6]
                logfc_list = [round(test[i][8], 2)]
                intensity_list = [None] * len(sample_map)
                intensity_list[sample_map.index(test[i][3])] = round(test[i][7], 2)
                # Get the compound name
                compound_name = identified_compounds.get(pk=compound_id).repositorycompound_set.filter(db_name='stds_db').values_list('compound_name',flat=True).first()
                pathway_names = pathway_name_dict[current_compound][0]
                super_pathway_names = pathway_name_dict[current_compound][1]
            else:
                if current_peak == test[i][1]:
                    if test[i][2] not in comparison_id_list:
                        logfc_list.append(round(test[i][8], 2))
                        comparison_id_list.append(test[i][2])
                    if test[i][3] not in sample_id_list:
                        intensity_list[sample_map.index(test[i][3])] = round(test[i][7], 2)
                        sample_id_list.append(test[i][3])

        if not first:
            id_status = 'identified+fragment' if has_frank_annotation(current_peak) else 'identified'
            c_data = [compound_id,peak_secondary_id,compound_name,formula,super_pathway_names,pathway_names] + intensity_list + logfc_list + [id_status]
            data.append(c_data)

        new_test_stop = timeit.default_timer()

        logger.info("Identified metabolites processing time: %s", str(new_test_stop - new_test_start))
        logger.info("--------------------------------------------------------")

        ac_start = timeit.default_timer()

        logger.info('Creating a list of the compound objects that are annotated removing all identified')
        annotated_compounds = Compound.objects.filter(Q(adduct="M+H") | Q(adduct="M-H"),identified='False', peak__dataset=dataset).exclude(secondaryId__in=list(ic_secondary_ids))
        logger.info('Getting the list of secondary Ids of compounds that are annotated only')

        new_test_ac_start = timeit.default_timer()
        logger.info('Getting comparisons')
        test = PeakDtComparison.objects.filter(peak__compound__in=list(annotated_compounds)).order_by('peak__compound__secondaryId','-peak__peakdtsample__intensity','comparison').values_list('peak__compound__secondaryId','peak__id','comparison__id', 'peak__peakdtsample__sample__id','peak__compound__id','peak__secondaryId','peak__compound__formula','peak__peakdtsample__intensity','logFC','peak__peakdtsample__id').distinct()
        logger.info('Getting annotated compound name list')
        annotated_compound_name_list = annotated_compounds.order_by("secondaryId").values_list("id","repositorycompound__db_name","repositorycompound__compound_name").distinct()
        logger.info('Getting annotated compound pathway list')
        annotated_compound_pathway_list = annotated_compounds.order_by("secondaryId").values_list("secondaryId", "compoundpathway__pathway__pathway__name").distinct()
        logger.info('Getting super-pathway list')
        pathway_super_pathway_list = Pathway.objects.all().values_list("name","datasourcesuperpathway__super_pathway__name")

        superpathway_dict = {}

        for pathway_name in pathway_super_pathway_list:
            if pathway_name[0] in superpathway_dict:
                if pathway_name[1] not in superpathway_dict[pathway_name[0]]:
                    superpathway_dict[pathway_name[0]] = " ".join([superpathway_dict[pathway_name[0]], pathway_name[1]])
            else:
                if pathway_name[1] == None:
                    superpathway_dict[pathway_name[0]] = "None"
                else:
                    superpathway_dict[pathway_name[0]] = pathway_name[1]

        pathway_name_dict = {}
        # Create dictionnary with pathway names for each compound
        for pathway_name in annotated_compound_pathway_list:
            if pathway_name[0] in pathway_name_dict:
                if pathway_name[1] not in pathway_name_dict[pathway_name[0]][0]:
                    pathway_name_dict[pathway_name[0]][0] = " ".join([pathway_name_dict[pathway_name[0]][0], pathway_name[1]])
                    pathway_name_dict[pathway_name[0]][1] = " ".join([pathway_name_dict[pathway_name[0]][1], superpathway_dict[pathway_name[1]]])
            else:
                if pathway_name[1] == None:
                    pathway_name_dict[pathway_name[0]] = ["None","None"]
                else:
                    pathway_name_dict[pathway_name[0]] = [pathway_name[1],  superpathway_dict[pathway_name[1]]]

        compound_name_dict = {}
        for compound_name in annotated_compound_name_list:
            compound_name_dict[compound_name[0]] = compound_name[2]

        list(test)
        current_compound = None
        current_peak = None
        comparison_id_list = None
        sample_id_list = None
        first = True
        for i in range(len(test)):
            if test[i][0] != current_compound:
                if not first:
                    id_status = 'annotated+fragment' if has_frank_annotation(current_peak) else 'annotated'
                    c_data = [compound_id,peak_secondary_id,compound_name,formula,super_pathway_names,pathway_names] + intensity_list + logfc_list + [id_status]
                    data.append(c_data)
                else:
                    first = False
                current_compound = test[i][0]
                current_peak = test[i][1]
                comparison_id_list = [test[i][2]]
                sample_id_list = [test[i][3]]
                compound_id = test[i][4]
                peak_secondary_id = test[i][5]
                formula = test[i][6]
                logfc_list = [round(test[i][8], 2)]
                intensity_list = [None] * len(sample_map)
                intensity_list[sample_map.index(test[i][3])] = round(test[i][7], 2)
                # Get the compound name
                compound_name = compound_name_dict[compound_id]
                pathway_names = pathway_name_dict[current_compound][0]
                super_pathway_names = pathway_name_dict[current_compound][1]

            else:
                if current_peak == test[i][1]:
                    if test[i][2] not in comparison_id_list:
                        logfc_list.append(round(test[i][8], 2))
                        comparison_id_list.append(test[i][2])
                    if test[i][3] not in sample_id_list:
                        intensity_list[sample_map.index(test[i][3])] = round(test[i][7], 2)
                        sample_id_list.append(test[i][3])
        if not first:
            id_status = 'annotated+fragment' if has_frank_annotation(current_peak) else 'annotated'
            c_data = [compound_id,peak_secondary_id,compound_name,formula,super_pathway_names,pathway_names] + intensity_list + logfc_list + [id_status]
            data.append(c_data)

        new_test_ac_stop = timeit.default_timer()

        logger.info("Annotated metabolites processing time: %s", str(new_test_ac_stop - new_test_ac_start))

        response = simplejson.dumps({'aaData': data})

        stop = timeit.default_timer()
        logger.info("metabolite table processing time: %s", str(stop - start))
        return HttpResponse(response, content_type='application/json')

    else:
        # return Http404
        pass

def get_frank_annotations(peak_ids):

    p2fs = PimpFrankPeakLink.objects.filter(pimp_peak__id__in = peak_ids).select_related(
                                'pimp_peak', 'frank_peak',
                                'frank_peak__fragmentation_set',
                                'frank_peak__preferred_candidate_annotation')
    frank_annotations = {}
    for p2f in p2fs:
        fset = p2f.frank_peak.fragmentation_set.slug

        # super slow
        # ms2_peaks_count = FrankPeak.objects.filter(fragmentation_set=p2f.frank_peak.fragmentation_set, msn_level=2).count()

        pslug = p2f.frank_peak.slug
        if p2f.frank_peak.preferred_candidate_annotation is not None:
            ac = p2f.frank_peak.preferred_candidate_annotation
            # TODO: shouldn't write the link inside here !!
            annot_string = '<a href="/frank/my_fragmentation_sets/{}/{}" target=new>'.format(fset,pslug) + ac.compound.name + " (" + ac.compound.formula + ")" + " Prob = {}".format(ac.confidence) + '</a>'
        # elif ms2_peaks_count > 0:
        else:
            annot_string = '<a href="/frank/my_fragmentation_sets/{}/{}" target=new>'.format(fset,pslug) + 'Annotate in FrAnK' + '</a>'

        peak = p2f.pimp_peak
        frank_annotations[peak.id] = annot_string

    return frank_annotations

def has_frank_annotation(peak_id):
    p2fs = PimpFrankPeakLink.objects.filter(pimp_peak__id = peak_id).select_related(
                                'frank_peak__preferred_candidate_annotation')
    found = False
    for p2f in p2fs:
        if p2f.frank_peak.preferred_candidate_annotation:
            found = True
            break
    return found

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
            attribute=Attribute.objects.filter(comparison__in=list(comparisons)).distinct().order_by('id')).distinct().order_by(
            'attribute__id', 'id')
        peakdtsamples = PeakDTSample.objects.filter(peak__dataset=dataset)
        compound_id = int(request.GET['compound_id'])
        compound_secondary_id = Compound.objects.get(pk=compound_id).secondaryId

        # added for frank annotation stuff
        peaks = Peak.objects.filter(dataset=dataset, compound__secondaryId=compound_secondary_id).order_by('secondaryId')
        peak_ids = [peak.id for peak in peaks]

        logger.info("Before getting Frank annotation")
        frank_annotations = get_frank_annotations(peak_ids)
        attribute_ids = set(samples.values_list('sampleattribute__attribute__id', flat=True))
        peaks_data = []

        logger.info("Before setting peak info")
        for peak in peaks:
            comp = peak.compound_set.get(secondaryId=compound_secondary_id)
            annotated_comp_num = peak.compound_set.exclude(secondaryId=compound_secondary_id).count()
            print "annotated compound number: ",annotated_comp_num
            print comp.identified
            if comp.identified == "True":
                standard_peak = True
            else:
                standard_peak = False
            # print comp.adduct," ",comp.ppm

            frank_annot = frank_annotations[peak.id] if peak.id in frank_annotations else 'None'
            peaks_data.append([peak.secondaryId, str(round(peak.rt, 2)),
                               str(round(peak.mass, 4)), str(peak.polarity),
                               str(peak.type), str(comp.adduct),
                               str(round(comp.ppm, 4)), standard_peak,annotated_comp_num, frank_annot])


            # peak_intensities_by_samples = peakdtsamples.filter(peak=peak).order_by('sample__attribute__id', 'sample__id').distinct()
            #
            # averages_by_group = []
            # for attribute_id in attribute_ids:
            #     averages_by_group.append(peak_intensities_by_samples.filter(sample__sampleattribute__attribute__id=attribute_id).aggregate(Avg('intensity'))['intensity__avg'])
            #
            # peak_data += averages_by_group
            # peaks_data.append(peak_data)

        # print peaks_data
        response = simplejson.dumps({'aaData': peaks_data})
        return HttpResponse(response, content_type='application/json')

def get_peak_table(request, project_id, analysis_id):
    if request.is_ajax():
        logger.info("peak table requested")
        start = timeit.default_timer()
        analysis = Analysis.objects.get(pk=analysis_id)
        project = Project.objects.get(pk=project_id)
        dataset = analysis.dataset_set.all()[0]
        comparisons = analysis.experiment.comparison_set.all()
        s = Sample.objects.filter(
            attribute=Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')).distinct().order_by(
            'attribute__id', 'id')
        p = list(PeakDTSample.objects.filter(sample=s, peak__dataset=dataset)       \
                                                .select_related('peak', 'sample')   \
                                                .distinct().order_by('peak__id', 'sample__attribute__id', 'sample__id'))
        pp = map(list, zip(*[iter(p)] * s.count()))

        # Simon's addition to fetch frank_annotations if the peak
        # has been linked to a frank peak and the frank_peak has
        # a preferred_candidate_annotation set

#         start2 = timeit.default_timer()
#         print "before slower"
#         frank_annotations = {}
#         for peakgroup in pp:
#             p2f = PimpFrankPeakLink.objects.filter(pimp_peak = peakgroup[0].peak)
#             if p2f:
#                 if p2f[0].frank_peak.preferred_candidate_annotation:
#                     ac = p2f[0].frank_peak.preferred_candidate_annotation
#                     fset = p2f[0].frank_peak.fragmentation_set.slug
#                     pslug = p2f[0].frank_peak.slug
#                     annot_string = '<a href="/frank/my_fragmentation_sets/{}/{}" target=new>'.format(fset,pslug) + ac.compound.name + " (" + ac.compound.formula + ")" + " Prob = {}".format(ac.confidence) + '</a>'
#                     frank_annotations[peakgroup[0].peak] = annot_string
#         stop2 = timeit.default_timer()
#         print "after slower: ", str(stop2 - start2)

        start2 = timeit.default_timer()
        print "before faster"
        first_peaks_ids = []
        for peakgroup in pp:
            peak = peakgroup[0].peak
            first_peaks_ids.append(peak.id)
        frank_annotations = get_frank_annotations(first_peaks_ids)
        stop2 = timeit.default_timer()
        print "after faster: ", str(stop2 - start2)

        data = [
            [str(peakgroup[0].peak.secondaryId), round(peakgroup[0].peak.mass, 4), round(peakgroup[0].peak.rt, 2)] +
            [round(peakdtsample.intensity, 2) if peakdtsample.intensity != 0 else 'NA' for peakdtsample in
                peakgroup] +
            [str(peakgroup[0].peak.polarity)] +
            [str(frank_annotations[peakgroup[0].peak.id]) if peakgroup[0].peak.id in frank_annotations else 'None'] for peakgroup in pp]



        print "SIMON", len(p),len(data),len(pp)

        response = simplejson.dumps({"aaData": data})

        stop = timeit.default_timer()
        logger.info("peak table processing time: %s", str(stop - start))
        return HttpResponse(response, content_type='application/json')


def get_single_comparison_table(request, project_id, analysis_id, comparison_id):

    if request.is_ajax():
        logger.info("single comparison table requested - comparison id: %s",comparison_id)
        start = timeit.default_timer()
        analysis = Analysis.objects.get(pk=analysis_id)
        project = Project.objects.get(pk=project_id)
        comparison = Comparison.objects.get(pk=comparison_id)
        dataset = analysis.dataset_set.all()[0]

        peak_comparison_list = Peak.objects.filter(peakdtcomparison__comparison=comparison,
                                               dataset=dataset).distinct()

        new_query_start = timeit.default_timer()
        peak_comparison_info = PeakDtComparison.objects.filter(peak__dataset=dataset, peak=peak_comparison_list, comparison=comparison).values_list('peak__secondaryId','logFC', 'pValue','adjPvalue', 'logOdds').distinct()
        new_query_stop = timeit.default_timer()


        list(peak_comparison_info)

        data = [list(elem) for elem in peak_comparison_info]
        # s = Sample.objects.filter(
        #     attribute=Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')).distinct().order_by(
        #     'attribute__id', 'id')
        # p = list(PeakDTSample.objects.filter(sample=s, peak__dataset=dataset)       \
        #                                         .select_related('peak', 'sample')   \
        #                                         .distinct().order_by('peak__id', 'sample__attribute__id', 'sample__id'))
        # pp = map(list, zip(*[iter(p)] * s.count()))
        # data = [
        #     [str(peakgroup[0].peak.secondaryId), round(peakgroup[0].peak.mass, 4), round(peakgroup[0].peak.rt, 2)] + [
        #         round(peakdtsample.intensity, 2) if peakdtsample.intensity != 0 else 'NA' for peakdtsample in
        #         peakgroup] + [str(peakgroup[0].peak.polarity)] for peakgroup in pp]

        response = simplejson.dumps({"aaData": data})
        logger.info("new comparison info list : %s", str(new_query_stop - new_query_start))

        return HttpResponse(response, content_type='application/json')


# @cache_page(60 * 60 * 24 * 100)
@login_required
# @profile("analysis_result.prof")
def analysis_result(request, project_id, analysis_id):

    if request.method == 'GET':

        try:
            project = Project.objects.get(pk=project_id)
            analysis = Analysis.objects.get(pk=analysis_id)
        except Project.DoesNotExist:
            raise Http404

        start = timeit.default_timer()

        comparisons = analysis.experiment.comparison_set.all().order_by('id')
        list(comparisons)
        dataset = analysis.dataset_set.all()[0]
        logger.info('dataset id: %d', dataset.id)
        logger.info('dataset %s', dataset)

        ############################# Samples & attributes ##############################
        logger.info("Samples -- START")
        s, member_list, sample_list = get_samples_and_attributes(comparisons)
        logger.info("Samples -- END")

        ############################# PCA calculation ##############################
        logger.info("PCA -- START")
        pca_start = timeit.default_timer()
        pca_info, explained_variance = get_pca(analysis, s, sample_list, member_list)
        pca_stop = timeit.default_timer()
        logger.info("PCA -- END")

        ########################## Best hits comparison ############################
        logger.info("Best hits comparison -- START")
        comp_start = timeit.default_timer()
        comparison_hits_list = get_best_hits_comparison(dataset, comparisons, s)
        comp_stop = timeit.default_timer()
        logger.info("comparison hits", comparison_hits_list)
        logger.info("Best hits comparison -- END")

        ############################# Databases ##############################
        logger.info("Databases -- START")
        databases = RepositoryCompound.objects.filter(compound__peak__dataset=dataset) \
                        .values_list('db_name', flat=True).distinct()
        databases = map(str, databases)
        logger.info("Databases -- END")

        ############################# Pathway ##############################
        logger.info("Pathway -- START")
        pathway_start = timeit.default_timer()
        pathway_list = Pathway.get_pathway_compounds_for_dataset(dataset)
        pathway_stop = timeit.default_timer()
        logger.info("Pathway -- END")

        ############################# Comparison info list ##############################
        logger.info("Comparison info list -- START")
        peak_comparison_list, comparison_info, all_comparison_info = get_comparison_info_list(dataset, comparisons)
        logger.info("Comparison info list -- END")

        ############################# Potential hits ##############################
        logger.info("Potential hits -- START")
        potential_hits = get_potential_hits(analysis, comparisons) # potetial hits that can't do statistics on.
        logger.info("Potential hits -- END")

        ############################# Super Pathway ##############################
        logger.info("Super Pathway -- START")
        super_pathways_list = get_superpathway()
        logger.info("Super Pathway -- END")

        stop = timeit.default_timer()
        logger.info("processing time : %s", str(stop - start))
        logger.info("pca generation : %s", str(pca_stop - pca_start))
        logger.info("comp time: %s", str(comp_stop - comp_start))
        logger.info("pathway time: %s", str(pathway_stop - pathway_start))

        logger.info('Starting TIC creation')
        tic_start = timeit.default_timer()
        tics = create_member_tics(comparisons)
        tic_stop = timeit.default_timer()
        logger.info('TIC creation time: %.2f', tic_stop - tic_start)

        identification_type_list = ['annotated', 'annotated+fragment', 'identified', 'identified+fragment']

        # populate in the request context
        c = {'member_list': member_list,
             'sample_list': sample_list,
             'pathway_list': pathway_list,
             'databases': databases,
             'dataset': dataset,
             'comparison_info': comparison_info,
             'all_comparison_info': all_comparison_info,
             'project': project,
             'analysis': analysis,
             'peak_comparison_list': peak_comparison_list,
             'comparisons': comparisons,
             'pca_data_point': pca_info,
             'comparison_hits_list': comparison_hits_list,
             'potential_hits': potential_hits,
             'tics': tics,
             'super_pathways_list': super_pathways_list,
             'explained_variance':explained_variance,
             'identification_type_list': identification_type_list
            }

        logger.info('Starting render')
        rendering_start = timeit.default_timer()
        rendering = render(request, 'base_result3.html', c)
        rendering_stop = timeit.default_timer()
        logger.info("rendering time: %s", str(rendering_stop - rendering_start))
        return rendering

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
            logger.info("no comparison specified")

        pathway_map = pathway.get_pathway_url(dataset_id, requested_comparison_id)

        logger.info(pathway_map)

        response = simplejson.dumps({'pathway_map': pathway_map})

        return HttpResponse(response, content_type='application/json')

def get_samples_and_attributes(comparisons):

    ######## Old query for members ########
    # member_set = set()
    # for comparison in comparisons:
    #     member_set = member_set.union(set(comparison.attribute.all()))
    # member_list = list(member_set)

    ######## New query for members ########
    s = Sample.objects.filter(
        attribute=Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')).distinct().order_by(
        'attribute__id', 'id')

    member_list = list(Attribute.objects.filter(comparison=comparisons).distinct().order_by('id'))
    logger.info('Member list: %s' % member_list)

    sample_member_hash = {}
    sample_list = []
    for member in member_list:
        sample_list.append(list(member.sample.all().order_by('id')))
        for sample in member.sample.all():
            sample_member_hash[sample] = member_list.index(member)
    logger.debug("sample member hash: %s", sample_member_hash)
    logger.debug("sample list: %s", sample_list)

    return s, member_list, sample_list

def get_pca(analysis, s, sample_list, member_list):

    pca_table = []
    for sample in s:
        pca_table.append(
            PeakDTSample.objects.filter(sample=sample, peak__dataset__analysis=analysis).distinct().order_by(
                'peak__id').values_list('intensity', flat=True))

    pca_matrix = np.array(pca_table)
    index_of_zero = np.where(pca_matrix == 0)[1]
    pca_matrix = np.delete(pca_matrix, index_of_zero, 1)
    log_pca_matrix = np.log2(pca_matrix)

    pca_obj = PCA(n_components=2,whiten=False)
    pca_obj.fit(log_pca_matrix)
    projected_data = pca_obj.transform(log_pca_matrix)
    explained_variance = []
    for i in range(2):
        explained_variance.append(100*pca_obj.explained_variance_ratio_[i])

    pca_info = [None, None]
    pca_data_point = []
    i = 0
    j = 0

    for member in sample_list:
        pca_serie = [member_list[j].name]
        for sample in member:
            dic = []
            dic.append(sample.name)
            dic.append(projected_data[i,0])
            dic.append(projected_data[i,1])
            pca_serie.append(dic)
            i += 1
        pca_data_point.append(pca_serie)
        j += 1
    pca_info.append(pca_data_point)
    logger.debug("pca_series: %s", pca_data_point)

    return pca_info, explained_variance

def get_best_hits_comparison(dataset, comparisons, s):

    # cache peakdt' intensity values from all samples for use later
    peakdtsample_intensity = {}
    for sample in s:
        pdts = sample.peakdtsample_set.all().values()
        for pdt in pdts:
            key = (pdt['peak_id'], pdt['sample_id'])
            peakdtsample_intensity[key] = pdt['intensity']
    logger.info("len(peakdtsample_intensity): %d", len(peakdtsample_intensity))

    comparison_hits_list = {}

    for c in comparisons:

        identified_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05)    \
                                            .filter(peak__compound__identified='True', peak__dataset=dataset)             \
                                            .extra(select={"absLogFC": "abs(logFC)",
                                                           'compound_name':'compound_repositorycompound.compound_name'},
                                                   tables=['compound_repositorycompound'],
                                                   where=['compound_repositorycompound.compound_id = compound_compound.id'])           \
                                            .order_by("-absLogFC").distinct()
        peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05)     \
                                            .filter(peak__dataset=dataset)              \
                                            .extra(select={"absLogFC": "abs(logFC)"})           \
                                            .order_by("-absLogFC").distinct()

        annotated_peakdtcomparisonList = list(set(peakdtcomparisonList) - set(identified_peakdtcomparisonList))

        peakdtcomparison_compound_name = OrderedDict()
        for pdtc in identified_peakdtcomparisonList:
            if not peakdtcomparison_compound_name.has_key(pdtc):
                peakdtcomparison_compound_name[pdtc] = (pdtc, [pdtc.compound_name])
            else:
                peakdtcomparison_compound_name[pdtc][1].append(pdtc.compound_name)

        # build the comparison table for identified compounds
        identified_info_list = []
        member_list = list(set(c.attribute.all()))
        member_list_map = dict()
        for member in member_list:
            member_list_map[member] = []
            for sample in member.sample.all():
                member_list_map[member].append(sample)

        for value in peakdtcomparison_compound_name.itervalues():
            identified_compound = value[0]
            compound_name = value[1]
            intensities = get_intensities_values(identified_compound, peakdtsample_intensity, member_list_map)
            identified_info_list.append([identified_compound, compound_name, intensities])

        # build the comparison table for annotated compounds
        annotated_info_list = []
        for annotated_compound in annotated_peakdtcomparisonList:
            intensities = get_intensities_values(annotated_compound, peakdtsample_intensity, member_list_map)
            annotated_info_list.append([annotated_compound, intensities])

        comparison_hits = [identified_info_list, annotated_info_list]
        comparison_hits_list[c] = comparison_hits

    return comparison_hits_list

def get_intensities_values(peakdtcomparison, peakdtsample_intensity, member_list_map):
    peak = peakdtcomparison.peak_id
    member_hash = {}

    for member, samples in member_list_map.iteritems():
        intensity_list = []
        for sample in samples:
            key = (peak, sample.id)
            peak_intensity = peakdtsample_intensity[key]
            intensity_list.append(peak_intensity)
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
        else: # len is 0
            memberInfo = [str(member), 0, None]
            data.append(memberInfo)
    # print "data : ",datadata
    return data

def get_comparison_info_list(dataset, comparisons):

    peak_comparison_list = Peak.objects.filter(peakdtcomparison__comparison__in=list(comparisons),
                                               dataset=dataset).distinct()
    new_query_start = timeit.default_timer()
    comparison_info = []
    for comparison in comparisons:
        peak_comparison_info = PeakDtComparison.objects.filter(peak__dataset=dataset, peak=peak_comparison_list, comparison=comparison.id).values_list('peak__secondaryId','logFC','adjPvalue', 'pValue', 'logOdds').distinct()
        logger.info('peak_comparison_info: %d', peak_comparison_info.count())
        logger.debug(peak_comparison_info)
        comparison_info.append([comparison,peak_comparison_info])
    new_query_stop = timeit.default_timer()
    logger.info("new comparison info list : %s", str(new_query_stop - new_query_start))

    new_comp_query_start = timeit.default_timer()
    all_comparison_info_query = PeakDtComparison.objects.filter(peak__dataset=dataset, peak=peak_comparison_list).values_list('peak__secondaryId','logFC','adjPvalue').order_by('peak__secondaryId','comparison__id').distinct()
    all_comparison_info = zip(*[iter(all_comparison_info_query)]*comparisons.count())
    new_comp_query_stop = timeit.default_timer()
    logger.info("all comparison info list : %s", str(new_comp_query_stop - new_comp_query_start))

    return peak_comparison_list, comparison_info, all_comparison_info

def get_potential_hits(analysis, comparisons):

    potential_hits = []
#     peaks = Peak.objects.filter(dataset__analysis=analysis)
#     for peak in peaks:
#          peak_comparisons = peak.peakdtcomparison_set.all()
#          if len(peak_comparisons) < len(comparisons): ##number of comparisons
#              missing_comparisons = comparisons.exclude(id__in=peak.peakdtcomparison_set.values_list("comparison_id"))
#              for comparison in missing_comparisons:
#                  groups = comparison.attribute.all()
#                  if peak._minimum_intensities_present(groups[0].sample.all()) or peak._minimum_intensities_present(groups[1].sample.all()):
#                     potential_hits.append([peak.id, peak.mass, peak.rt, groups[0].name + " / " + groups[1].name])
    return potential_hits

def get_superpathway():

    super_pathways = SuperPathway.objects.all().prefetch_related('datasourcesuperpathway_set__pathway')
    super_pathways_list = []
    for i in super_pathways:
        single_super_pathway_list = []
        pathway_name_list = []
        single_super_pathway_list.append(i.name)
        for i2 in i.datasourcesuperpathway_set.all():
            pathway_name_list.append(i2.pathway.name)
        single_super_pathway_list.append(pathway_name_list)
        super_pathways_list.append(single_super_pathway_list)
    pathway_name_list = []
    for i in DataSourceSuperPathway.objects.filter(super_pathway=None).prefetch_related('pathway'):
        pathway_name_list.append(i.pathway.name)
    super_pathways_list.append([None, pathway_name_list])
    return super_pathways_list

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
                logger.debug(compounds_identified[:1])
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
        logger.debug(member_list)
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
        logger.debug(member_hash)
        data = []
        for member in member_hash.iterkeys():
            intensities = filter(lambda a: a != 0, member_hash[member][0])
            logger.debug("intensities :")
            logger.debug(intensities)
            if len(intensities) > 1:
                array = np.array(intensities)
                mean = np.mean(array)
                std = np.std(array, axis=0)
                memberInfo = [str(member), mean, std, member_hash[member]]
                data.append(memberInfo)
            elif len(intensities) == 1:
                memberInfo = [str(member), intensities[0], None, member_hash[member]]
                data.append(memberInfo)
        logger.debug("BBBbbbbbBBBBBBBBBBBBBBBBBBB")
        logger.debug(data)
        # PeakQCSample objects for blank samples only
        peakblanksamples = PeakQCSample.objects.filter(peak=peak, sample__attribute__name="blank")
        if peakblanksamples:
            logger.debug("here peak blank samples:")
            logger.debug(peakblanksamples)
            blank_intensity_list = []
            blank_list = []
            for blank_sample in peakblanksamples:
                blank_intensity_list.append(blank_sample.intensity)
                blank_list.append(str(blank_sample.sample.name).split(".")[0])
            blank_info = [blank_intensity_list, blank_list]

            blank_intensities = filter(lambda a: a != 0, blank_info[0])
            logger.debug("blank intensities :")
            logger.debug(blank_intensities)
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

        logger.info(blankInfo)
        data_hash = {"samples": data, "blanks": blankInfo}
        logger.info(data_hash)

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
            logger.info("comparison %s", requested_comparison)
        except:
            requested_comparison = None
            logger.info("no comparison specified")

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
        logger.info(member_list)
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
        logger.debug(member_hash)
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
            else:
                memberInfo = [str(member), 0, None, member_hash[member]]
                data.append(memberInfo)
        logger.debug(data)
        # PeakQCSample objects for blank samples only
        peakblanksamples = PeakQCSample.objects.filter(peak=peak, sample__attribute__name="blank")
        if peakblanksamples:
            logger.info("here peak blank samples:")
            logger.debug(peakblanksamples)
            blank_intensity_list = []
            blank_list = []
            for blank_sample in peakblanksamples:
                blank_intensity_list.append(blank_sample.intensity)
                blank_list.append(str(blank_sample.sample.name).split(".")[0])
            blank_info = [blank_intensity_list, blank_list]

            blank_intensities = filter(lambda a: a != 0, blank_info[0])
            logger.info("blank intensities :")
            logger.debug(blank_intensities)
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

        logger.debug(blankInfo)
        data_hash = {"samples": data, "blanks": blankInfo}
        logger.debug(data_hash)


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
        logger.info(member_list)

        sample_list = []
        for member in member_list:
            sample_list.append(list(member.sample.all()))
        logger.info(sample_list)

        logger.info("peak id %s", peak.id)
        logger.info(polarity)
        logger.info(rt)
        logger.info(mass)

        massWindow = mass * ppm * 0.000001
        logger.info("after mass window")
        massUp = mass + massWindow
        massLow = mass - massWindow
        rtUp = rt + rtWindow / 2
        rtLow = rt - rtWindow / 2
        logger.info("after rtLow")
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
                    logger.error("EXCEPTION TRIGGERED!!!!!")
                # print lineList
                data.append([name, lineList])
            # print data
        message = "got somthing on the server for peaks chromatogram!!!"
        response = simplejson.dumps(data)
        return HttpResponse(response, content_type='application/json')


#def my_new_view(requet, project_id, analysis_id):
#    if request.is_ajax():
#        peak_id = int(request.GET['id'])
#        ppm = float(request.GET['ppm'])
#        rtWindow = float(request.GET['rtwindow'])
#
#        mass = float(peak.mass)
#        u = robjects.FloatVector([massLow, massUp])
#        mzrange = robjects.r['matrix'](u, ncol=2)
#        w = robjects.FloatVector([rtLow, rtUp])
#        rtrange = robjects.r['matrix'](w, ncol=2)
#        xcms = importr("xcms")


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
        logger.info(member_list)

        sample_list = []
        for member in member_list:
            sample_list.append(list(member.sample.all()))
        logger.info(sample_list)

        logger.info("peak id %s", peak.id)
        logger.info(polarity)
        logger.info(rt)
        logger.info(mass)

        massWindow = mass * ppm * 0.000001
        logger.info("after mass window")
        massUp = mass + massWindow
        massLow = mass - massWindow
        rtUp = rt + rtWindow / 2
        rtLow = rt - rtWindow / 2
        logger.info("after rtLow")
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
                logger.info("name: %s", name)
                if polarity == "negative":
                    mzxmlfile = sample.samplefile.negdata
                else:
                    mzxmlfile = sample.samplefile.posdata
                file = xcms.xcmsRaw(mzxmlfile.file.path)
                logger.info("file opened")
                logger.debug("mzrange: %s", mzrange)
                logger.debug("rtrange: %s", rtrange)
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
                    logger.error("EXCEPTION TRIGGERED!!!!!")
                # print lineList
                data.append([name, lineList])
                logger.debug(data)
        message = "got somthing on the server for peaks chromatogram!!!"


        response = simplejson.dumps(data)
        return HttpResponse(response, content_type='application/json')


def compound_info(request, project_id, analysis_id):
    if request.is_ajax():
        compound_id = int(request.GET['id'])
        compound = Compound.objects.get(pk=compound_id)
        data = [compound.adduct, compound.inchikey]
        pathway_list = [pathway_name.encode("utf8") for pathway_name in compound.compoundpathway_set.all().values_list('pathway__pathway__name', flat=True).distinct()]
        if pathway_list:
            data.append(pathway_list)
        else:
            data.append(None)
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
            logger.debug("names lalalalalalala %s", names)
            distinct_names = list(set([x.lower() for x in names]))
            compoundsList.append(distinct_names)

        logger.debug("compoundList herererererere %s", compoundsList)

        response = simplejson.dumps(compoundsList)
        return HttpResponse(response, content_type='application/json')

def create_member_tics(comparisons):
    tics = {}
    attributes = Attribute.objects.filter(comparison=comparisons).distinct().order_by('id').prefetch_related(
        'sample__samplefile__posdata__tic', 'sample__samplefile__negdata__tic'
    )

    for attribute in attributes:
        sampleList = attribute.sample.all()

        sampleCurveList = {}

        for sample in sampleList:
            sample_name = sample.name
            if not sample.samplefile.posdata:
                posdata = "None"
            else:
                posmzxmlfile = sample.samplefile.posdata
                if not posmzxmlfile.tic:
                    # print "over here"
                    posdata = getIntensity(posmzxmlfile)
                    # print "posdata ",[i[0] for i in posdata]
                    x_axis = [i[0] for i in posdata]
                    y_axis = [i[1] for i in posdata]
                    x = pickle.dumps(x_axis)
                    y = pickle.dumps(y_axis)
                    mean = np.mean(y_axis)
                    median = np.median(y_axis)
                    # print "pos median : ", median
                    # print "pos mean : ", mean
                    posBarTic = [mean, median]

                    # print x

                    # print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"

                    curve = Curve.objects.create(x_axis=x, y_axis=y, mean=mean, median=median)
                    curve.save()
                    posmzxmlfile.tic = curve
                    posmzxmlfile.save()

                    logger.debug('%s', posmzxmlfile.tic.x_axis)
                # posintensity = posdata[0]
                # postime = posdata[1]
                else:
                    # print "tic exist"
                    # print str(posmzxmlfile.tic.x_axis)
                    x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
                    y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
                    # print "pos median : ", posmzxmlfile.tic.median
                    # print "pos mean : ", posmzxmlfile.tic.mean
                    posBarTic = [posmzxmlfile.tic.mean, posmzxmlfile.tic.median]
                    posdata = []
                    # print "after loads"
                    for i in range(len(x_axis)):
                        posdata.append([float(x_axis[i]), float(y_axis[i])])
                    # print "after for"
                # print posdata
            if not sample.samplefile.negdata:
                negdata = "None"
            else:
                negmzxmlfile = sample.samplefile.negdata
                if not negmzxmlfile.tic:
                    # print "over there :)"
                    negdata = getIntensity(negmzxmlfile)
                    x_axis = [i[0] for i in negdata]
                    y_axis = [i[1] for i in negdata]
                    x = pickle.dumps(x_axis)
                    y = pickle.dumps(y_axis)
                    mean = np.mean(y_axis)
                    median = np.median(y_axis)
                    # print "neg median : ", median
                    # print "neg mean : ", mean
                    negBarTic = [mean, median]

                    curve = Curve.objects.create(x_axis=x, y_axis=y, mean=mean, median=median)
                    curve.save()
                    negmzxmlfile.tic = curve
                    negmzxmlfile.save()
                else:
                    # print "tic exist"
                    x_axis = pickle.loads(str(negmzxmlfile.tic.x_axis))
                    y_axis = pickle.loads(str(negmzxmlfile.tic.y_axis))
                    # print "neg median : ", negmzxmlfile.tic.median
                    # print "neg mean : ", negmzxmlfile.tic.mean
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
        #     posticfile = "None"
        # else:
        #     posticfile = Attribute.objects.get(id=attribute_id).ticgroup.postic.ticplot
        #     # print posticfile
        # if not Attribute.objects.get(id=attribute_id).ticgroup.negtic :
        #     negticfile = "None"
        # else:
        #     negticfile = Attribute.objects.get(id=attribute_id).ticgroup.negtic.ticplot
        # fileList = [attribute_name,posticfile,negticfile]
        # attributeResponse = [attribute_name, sampleCurveList]
        tics[attribute] = sampleCurveList
    return tics


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
                # print "over here"
                posdata = getIntensity(posmzxmlfile)
                # print "posdata ",[i[0] for i in posdata]
                x_axis = [i[0] for i in posdata]
                y_axis = [i[1] for i in posdata]
                x = pickle.dumps(x_axis)
                y = pickle.dumps(y_axis)
                mean = np.mean(y_axis)
                median = np.median(y_axis)
                # print "pos median : ", median
                # print "pos mean : ", mean
                posBarTic = [mean, median]

                # print x

                # print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"

                curve = Curve.objects.create(x_axis=x, y_axis=y, mean=mean, median=median)
                curve.save()
                posmzxmlfile.tic = curve
                posmzxmlfile.save()

                logger.debug('%s', posmzxmlfile.tic.x_axis)
            # posintensity = posdata[0]
            # postime = posdata[1]
            else:
                # print "tic exist"
                # print str(posmzxmlfile.tic.x_axis)
                x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
                y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
                # print "pos median : ", posmzxmlfile.tic.median
                # print "pos mean : ", posmzxmlfile.tic.mean
                posBarTic = [posmzxmlfile.tic.mean, posmzxmlfile.tic.median]
                posdata = []
                # print "after loads"
                for i in range(len(x_axis)):
                    posdata.append([float(x_axis[i]), float(y_axis[i])])
                # print "after for"
            # print posdata
        if not sample.samplefile.negdata:
            negdata = "None"
        else:
            negmzxmlfile = sample.samplefile.negdata
            if not negmzxmlfile.tic:
                # print "over there :)"
                negdata = getIntensity(negmzxmlfile)
                x_axis = [i[0] for i in negdata]
                y_axis = [i[1] for i in negdata]
                x = pickle.dumps(x_axis)
                y = pickle.dumps(y_axis)
                mean = np.mean(y_axis)
                median = np.median(y_axis)
                # print "neg median : ", median
                # print "neg mean : ", mean
                negBarTic = [mean, median]

                curve = Curve.objects.create(x_axis=x, y_axis=y, mean=mean, median=median)
                curve.save()
                negmzxmlfile.tic = curve
                negmzxmlfile.save()
            else:
                # print "tic exist"
                x_axis = pickle.loads(str(negmzxmlfile.tic.x_axis))
                y_axis = pickle.loads(str(negmzxmlfile.tic.y_axis))
                # print "neg median : ", negmzxmlfile.tic.median
                # print "neg mean : ", negmzxmlfile.tic.mean
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
    #     posticfile = "None"
    # else:
    #     posticfile = Attribute.objects.get(id=attribute_id).ticgroup.postic.ticplot
    #     # print posticfile
    # if not Attribute.objects.get(id=attribute_id).ticgroup.negtic :
    #     negticfile = "None"
    # else:
    #     negticfile = Attribute.objects.get(id=attribute_id).ticgroup.negtic.ticplot
    # fileList = [attribute_name,posticfile,negticfile]
    # attributeResponse = [attribute_name, sampleCurveList]
    return sampleCurveList


def getIntensity(mzxmlFile):
    xcms = importr("xcms")
    intensity = []
    file = xcms.xcmsRaw(mzxmlFile.file.path)
    logger.info("file opened")
    intensity = [int(i) for i in list(file.do_slot("tic"))]
    time = [str(i) for i in list(file.do_slot("scantime"))]
    logger.info("intensity list created")
    # scan = xcms.getScan(file, 1)
    # print "scan : ",scan
    # print intensity
    # print time
    lineList = []
    for i in range(len(intensity)):
        lineList.append([float(time[i]), intensity[i]])
    # print lineList
    return lineList
