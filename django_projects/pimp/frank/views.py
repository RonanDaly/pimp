from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from frank.models import *
from frank.forms import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from frank import tasks
import numpy as np
from decimal import *
from django.db.models import Max
import re
import datetime
import jsonpickle
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError

##### No longer needed for plotting #######
# import matplotlib
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure

#### Now used to plot the graph ######
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from matplotlib import pylab
from pylab import *
import PIL
import PIL.Image
import StringIO
from django.http import HttpResponse
from django.db import transaction



## Add a method to generate each context_dictionary for each view here
## Aim is to avoid repetition of code

# Context dictionary for the 'my_experiments' page
def get_my_experiments_context_dict(user):
    experiment_list = Experiment.objects.filter(users = user)
    context_dict = {
        'experiment_list': experiment_list,
    }
    return context_dict


# Context dictionary for the 'add_experiments' page
def get_add_experiment_context_dict(form):
    context_dict = {
        'experiment_form': form,
    }
    return context_dict


# Context dictionary for the 'Experiment' page
def get_experiment_summary_context_dict(experiment_name_slug):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experimental_conditions = ExperimentalCondition.objects.filter(experiment = experiment)
    fragmentation_set_list = FragmentationSet.objects.filter(
            experiment = experiment
    )
    can_add_frag_set = False
    sample_files_in_experiment = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)
    if len(sample_files_in_experiment) > 1:
        can_add_frag_set = True
    context_dict = {
        'experiment': experiment,
        'conditions': experimental_conditions,
        'fragmentation_sets': fragmentation_set_list,
        'create_frag_set': can_add_frag_set
    }
    return context_dict

# Context dictionary for the 'Add Experimental Condition' page
def get_add_experimental_condition_context_dict(experiment_name_slug, form):
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    context_dict = {
            'experimental_condition_form': form,
            'experiment_name': experiment.title,
            'experiment_slug': experiment.slug,
    }
    return context_dict


# Context dictionary for the 'Experimental Condition' page
def get_condition_summary_context_dict(experiment_name_slug, condition_name_slug):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experimental_condition = ExperimentalCondition.objects.get(slug = condition_name_slug)
    samples = Sample.objects.filter(experimental_condition = experimental_condition)
    files = SampleFile.objects.filter(sample = samples)
    context_dict = {
        'experiment': experiment,
        'condition': experimental_condition,
        'samples': samples,
        'sample_files': files
    }
    return context_dict


# Context dictionary for the 'Add Experimental Sample' page
def get_add_sample_context_dict(experiment_name_slug, condition_name_slug, sample_form):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    condition = ExperimentalCondition.objects.get(slug=condition_name_slug)
    context_dict = {
        'experiment': experiment,
        'condition': condition,
        'sample_form':sample_form,
    }
    return context_dict


# Context dictionary for the 'Add Sample File' page
def get_add_sample_file_context_dict(experiment_name_slug, condition_name_slug, sample_slug, sample_file_form):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experimental_condition = ExperimentalCondition.objects.get(slug=condition_name_slug)
    sample = Sample.objects.get(slug = sample_slug)
    context_dict = {
            'experiment': experiment,
            'condition': experimental_condition,
            'sample': sample,
            'sampleFileForm': sample_file_form,
    }
    return context_dict


# Context dictionary for the 'Create Fragmentation Set' page
def get_create_fragmentation_set_context_dict(experiment_name_slug, form):
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    context_dict = {
            'frag_set_form': form,
            'experiment': experiment
    }
    return context_dict

def get_fragmentation_set_summary_context_dict(user):
    fragmentation_set_list = []
    user_experiment_list = Experiment.objects.filter(users=user)
    for experiment in user_experiment_list:
        experiment_fragment_sets = FragmentationSet.objects.filter(experiment=experiment)
        fragmentation_set_list.extend(experiment_fragment_sets)
    context_dict = {
        'fragmentation_sets': fragmentation_set_list,
    }
    return context_dict

def get_fragmentation_set_context_dict(fragmentation_set_name_slug, annotation_tool_selection_form):
    fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    ## Display number of msn peaks
    ms1_peaks = Peak.objects.filter(fragmentation_set = fragmentation_set, msn_level=1)
    number_of_ms1_peaks = len(ms1_peaks)
    annotation_queries = AnnotationQuery.objects.filter(fragmentation_set = fragmentation_set)
    sample_file_ids = ms1_peaks.values("source_file").distinct()
    ms1_peaks_by_file = {}
    for file_id in sample_file_ids:
        experimental_file = SampleFile.objects.get(id=file_id.get('source_file'))
        ms1_peaks_by_file[experimental_file] = ms1_peaks.filter(source_file = experimental_file).order_by('mass')
    context_dict = {
        'annotation_tool_form': annotation_tool_selection_form,
        'fragment_set': fragmentation_set,
        'number_of_peaks':number_of_ms1_peaks,
        'annotations': annotation_queries,
        'peaks_by_file': ms1_peaks_by_file,
    }
    return context_dict


def get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug):
    fragmentation_set_object = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    peak = Peak.objects.get(slug=peak_name_slug, fragmentation_set = fragmentation_set_object)
    ## Display number of msn peaks
    fragmentation_spectra = Peak.objects.filter(parent_peak = peak).order_by('mass')
    associated_annotation_queries = AnnotationQuery.objects.filter(fragmentation_set = fragmentation_set_object, status='Completed Successfully')
    candidate_annotations = {}
    for annotation_query in associated_annotation_queries:
        candidate_annotations[annotation_query] = CandidateAnnotation.objects.filter(peak=peak,annotation_query=annotation_query).order_by('-confidence')
    number_of_fragments_in_spectra = len(fragmentation_spectra)
    preferred_annotation = peak.preferred_candidate_annotation
    context_dict = {
        'peak': peak,
        'fragmentation_peak_list': fragmentation_spectra,
        'number_of_fragments':number_of_fragments_in_spectra,
        'candidate_annotations' : candidate_annotations,
        'annotation_queries': associated_annotation_queries,
        'preferred_annotation': preferred_annotation,
    }
    return context_dict


def get_define_annotation_query_context_dict(fragmentation_set_name_slug, form, annotation_tool_slug):
    fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    annotation_tool = AnnotationTool.objects.get(slug=annotation_tool_slug)
    context_dict = {
        'annotation_query_form': form,
        'fragmentation_set': fragmentation_set,
        'annotation_tool': annotation_tool,
    }
    return context_dict


def get_specify_preferred_annotation_context_dict(fragmentation_set_name_slug, peak_name_slug, annotation_id, form):
    fragmentation_set_object = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    peak_object = Peak.objects.get(slug = peak_name_slug)
    annotation_object = CandidateAnnotation.objects.get(id = annotation_id)
    context_dict = {
        'fragmentation_set': fragmentation_set_object,
        'peak': peak_object,
        'annotation': annotation_object,
        'form': form,
    }
    return context_dict

def get_delete_experiment_context_dict(experiment_name_slug):
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    context_dict = {
        'experiment': experiment,
    }
    return context_dict

# Create your views here.

# View for the Index page of frank
@login_required
def index(request):
    return render(request, 'frank/index.html')

# View for the My Experiments page of frank
@login_required
def my_experiments(request):
    active_user = request.user
    context_dict = get_my_experiments_context_dict(user = active_user)
    return render(request, 'frank/my_experiments.html', context_dict)

@login_required
def add_experiment(request):
    active_user = request.user
    # if the request method is a POST
    if request.method == 'POST':
        # retrieve the form from the POST
        form = ExperimentForm(request.POST)
        # is the form valid?
        if form.is_valid():
            # commit the form to the database
            experiment = form.save(commit=False)
            # The user id is used to indicate the creator of the experiment
            experiment.created_by = active_user
            experiment.save()
            new_user = UserExperiment.objects.create(user = active_user, experiment = experiment)
            context_dict = get_my_experiments_context_dict(user = active_user)
            return render(request, 'frank/my_experiments.html', context_dict)
        else:
            # if the form is invalid, display the errors
            context_dict = get_add_experiment_context_dict(form)
            return render(request, 'frank/add_experiment.html', context_dict)
    else:
        form = ExperimentForm()
        context_dict = get_add_experiment_context_dict(form)
    return render(request, 'frank/add_experiment.html', context_dict)

@login_required
def experiment_summary(request, experiment_name_slug):
    context_dict = get_experiment_summary_context_dict(experiment_name_slug)
    return render(request, 'frank/experiment.html', context_dict)


@login_required
def add_experimental_condition(request, experiment_name_slug):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    if request.method == 'POST':
        form = ExperimentalConditionForm(request.POST)
        if form.is_valid():
            condition = form.save(commit=False)
            condition.experiment = experiment
            condition.save()
            context_dict = get_experiment_summary_context_dict(experiment_name_slug)
            return render(request, 'frank/experiment.html', context_dict)
        else:
            context_dict = get_add_experimental_condition_context_dict(experiment_name_slug, form)
            return render(request, 'frank/add_experimental_condition.html', context_dict)
    else:
        form = ExperimentalConditionForm()
        context_dict = get_add_experimental_condition_context_dict(experiment_name_slug, form)
        return render(request, 'frank/add_experimental_condition.html', context_dict)


@login_required
def condition_summary(request, experiment_name_slug, condition_name_slug):
    context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
    return render(request, 'frank/condition.html', context_dict)


@login_required
def add_sample (request, experiment_name_slug, condition_name_slug):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experimental_condition = ExperimentalCondition.objects.get(slug = condition_name_slug)
    if request.method == 'POST':
        sample_form = SampleForm(request.POST)
        if sample_form.is_valid():
            sample = sample_form.save(commit = False)
            sample.experimental_condition = experimental_condition
            sample.save()
            context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
            return render(request, 'frank/condition.html', context_dict)
        else:
            context_dict = get_add_sample_context_dict(experiment_name_slug, condition_name_slug, sample_form)
            return render(request, 'frank/add_sample.html', context_dict)
    else:
        sample_form = SampleForm()
        context_dict = get_add_sample_context_dict(experiment_name_slug, condition_name_slug, sample_form)
        return render(request, 'frank/add_sample.html', context_dict)


@login_required
def add_sample_file(request, experiment_name_slug, condition_name_slug, sample_slug):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experimental_condition = ExperimentalCondition.objects.get(slug = condition_name_slug)
    sample = Sample.objects.get(slug = sample_slug)
    if request.method == 'POST':
        sample_file_form = SampleFileForm(request.POST, request.FILES)
        if sample_file_form.is_valid():
            new_sample = sample_file_form.save(commit=False)
            new_sample.sample = sample
            new_sample.name = new_sample.address.name
            try:
                with transaction.atomic():
                    new_sample.save()
                context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
                return render(request, 'frank/condition.html', context_dict)
            except ValidationError:
                # Validation error will result from an attempt to add a duplicate
                # file to a sample
                sample_file_form.add_error("address", "This file already exists in the sample.")
                context_dict = get_add_sample_file_context_dict(experiment_name_slug, condition_name_slug, sample_slug, sample_file_form)
                return render(request, 'frank/add_sample_file.html', context_dict)
        else:
            context_dict = get_add_sample_file_context_dict(experiment_name_slug, condition_name_slug, sample_slug, sample_file_form)
            return render(request, 'frank/add_sample_file.html', context_dict)
    else:
        sample_file_form = SampleFileForm()
        context_dict = get_add_sample_file_context_dict(experiment_name_slug, condition_name_slug, sample_slug, sample_file_form)
        return render(request, 'frank/add_sample_file.html', context_dict)


@login_required
def create_fragmentation_set(request, experiment_name_slug):
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    if request.method == 'POST':
        fragment_set_form = FragmentationSetForm(request.POST)
        if fragment_set_form.is_valid():
            new_fragmentation_set = fragment_set_form.save(commit=False)
            new_fragmentation_set.experiment = experiment
            source_files = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)
            num_source_files = len(source_files)
            if num_source_files > 0:
                new_fragmentation_set.save()
                input_peak_list_to_database(experiment_name_slug, new_fragmentation_set.id)
                context_dict = get_experiment_summary_context_dict(experiment_name_slug)
                return render(request, 'frank/experiment.html', context_dict)
            else:
                fragment_set_form.add_error("name", "No source files found for experiment.")
                context_dict = get_create_fragmentation_set_context_dict(experiment_name_slug, fragment_set_form)
                return render(request, 'frank/create_fragmentation_set.html', context_dict)
        else:
            context_dict = get_create_fragmentation_set_context_dict(experiment_name_slug, fragment_set_form)
            return render(request, 'frank/create_fragmentation_set.html', context_dict)
    else:
        fragment_set_form = FragmentationSetForm()
        context_dict = get_create_fragmentation_set_context_dict(experiment_name_slug, fragment_set_form)
        return render(request, 'frank/create_fragmentation_set.html', context_dict)


@login_required
def fragmentation_set_summary(request):
    current_user = request.user
    context_dict = get_fragmentation_set_summary_context_dict(current_user)
    return render(request, 'frank/my_fragmentation_sets.html', context_dict)

@login_required
def fragmentation_set(request, fragmentation_set_name_slug):
    if request.method == 'POST':
        annotation_tool_selection_form = AnnotationToolSelectionForm(request.POST)
        if annotation_tool_selection_form.is_valid():
            user_tool_choice = annotation_tool_selection_form.cleaned_data['tool_selection'].name
            annotation_query_form = None
            if user_tool_choice == 'MassBank':
                annotation_query_form = MassBankQueryForm()
            elif user_tool_choice == 'NIST':
                annotation_query_form = NISTQueryForm()
            elif user_tool_choice == 'LCMS DDA Network Sampler':
                annotation_query_form = NetworkSamplerQueryForm()
            annotation_tool_slug = AnnotationTool.objects.get(name=user_tool_choice).slug
            context_dict = get_define_annotation_query_context_dict(fragmentation_set_name_slug, annotation_query_form, annotation_tool_slug)
            return render(request, 'frank/define_annotation_query.html', context_dict)
        else:
            context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug, annotation_tool_selection_form)
            return render(request, 'frank/fragmentation_set.html', context_dict)
    else:
        fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
        experiment = fragmentation_set.experiment
        form = AnnotationToolSelectionForm(experiment_object=experiment)
        context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug, form)
        return render(request, 'frank/fragmentation_set.html', context_dict)


@login_required
def peak_summary(request, fragmentation_set_name_slug, peak_name_slug):
    context_dict = get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug)
    return render(request, 'frank/peak_summary.html', context_dict)


@login_required
def define_annotation_query(request, fragmentation_set_name_slug, annotation_tool_slug):
    fragmentation_set = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    annotation_tool = AnnotationTool.objects.get(slug=annotation_tool_slug)
    annotation_query_form = None
    if request.method == 'POST':
        if annotation_tool.name == 'MassBank':
            annotation_query_form = MassBankQueryForm(request.POST)
        elif annotation_tool.name== 'NIST':
            annotation_query_form = NISTQueryForm(request.POST)
        elif annotation_tool.name == 'LCMS DDA Network Sampler':
            annotation_query_form = NetworkSamplerQueryForm(request.POST)
        elif annotation_tool.name == 'Precursor Mass Filter':
            annotation_query_form = PrecursorMassFilterForm(request.POST)
        if annotation_query_form.is_valid():
            new_annotation_query = annotation_query_form.save(commit=False)
            new_annotation_query.fragmentation_set = fragmentation_set
            currentUser = request.user
            paramaterised_query_object = set_annotation_query_parameters(new_annotation_query, annotation_query_form, currentUser)
            paramaterised_query_object.save()
            generate_annotations(paramaterised_query_object)
            experiment = fragmentation_set.experiment
            form = AnnotationToolSelectionForm(experiment_object=experiment)
            context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug, form)
            return render(request, 'frank/fragmentation_set.html', context_dict)
        else:
            context_dict = get_define_annotation_query_context_dict(fragmentation_set_name_slug, annotation_query_form, annotation_tool_slug)
            return render(request, 'frank/define_annotation_query.html', context_dict)
    else:
        if annotation_tool.name == 'MassBank':
            annotation_query_form = MassBankQueryForm()
        elif annotation_tool.name== 'NIST':
            annotation_query_form = NISTQueryForm()
        elif annotation_tool.name == 'LCMS DDA Network Sampler':
            annotation_query_form = NetworkSamplerQueryForm()
        elif annotation_tool.name == 'Precursor Mass Filter':
            annotation_query_form = PrecursorMassFilterForm()
        context_dict = get_define_annotation_query_context_dict(fragmentation_set_name_slug, annotation_query_form, annotation_tool_slug)
        return render(request, 'frank/define_annotation_query.html', context_dict)

@login_required
def specify_preferred_annotation(request, fragmentation_set_name_slug, peak_name_slug, annotation_id):
    if request.method == 'POST':
        preferred_annotation_form = PreferredAnnotationForm(request.POST)
        if preferred_annotation_form.is_valid():
            justification_for_annotation = preferred_annotation_form.cleaned_data['preferred_candidate_description']
            current_user = request.user
            current_time = datetime.datetime.now()
            annotation_object = CandidateAnnotation.objects.get(id=annotation_id)
            peak_for_update = Peak.objects.get(slug = peak_name_slug)
            peak_for_update.preferred_candidate_annotation = annotation_object
            peak_for_update.preferred_candidate_description = justification_for_annotation
            peak_for_update.preferred_candidate_user_selector = current_user
            peak_for_update.preferred_candidate_updated_date = current_time
            peak_for_update.save()
            context_dict = get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug)
            return render(request, 'frank/peak_summary.html', context_dict)
        else:
            context_dict = get_specify_preferred_annotation_context_dict(fragmentation_set_name_slug, peak_name_slug, annotation_id, preferred_annotation_form)
            return render(request, 'frank/specify_preferred_annotation.html', context_dict)
    else:
        preferred_annotation_form = PreferredAnnotationForm()
        context_dict = get_specify_preferred_annotation_context_dict(fragmentation_set_name_slug, peak_name_slug, annotation_id, preferred_annotation_form)
        return render(request, 'frank/specify_preferred_annotation.html', context_dict)


### Additional methods go here

def input_peak_list_to_database(experiment_name_slug, fragmentation_set_id):
    ## Remember to add the msnAnalysis method onto celery
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experiment_type = experiment.detection_method.name
    if experiment_type == 'Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition':
        tasks.msnGeneratePeakList.delay(experiment_name_slug, fragmentation_set_id)
    elif experiment_type == 'Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation':
        tasks.gcmsGeneratePeakList.delay(experiment_name_slug, fragmentation_set_id)


def generate_annotations(annotation_query_object):
    annotation_tool = annotation_query_object.annotation_tool
    if annotation_tool.name == 'MassBank':
        tasks.massBank_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'NIST':
        tasks.nist_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'LCMS DDA Network Sampler':
        pass
    elif annotation_tool.name == 'Precursor Mass Filter':
        tasks.precursor_mass_filter(annotation_query_object.id)

def set_annotation_query_parameters(annotation_query_object, annotation_query_form, currentUser):
    if isinstance(annotation_query_form, MassBankQueryForm):
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='MassBank')
        # Parameters for MassBank are...
        #   type - (hardcoded) the type of search (1 = batch search)
        #   mail_address - (generated automatically) the email of the recipiant of the results
        #   query_spectra - (generated automatically) retrieved from the database
        #   instruments - (selected by user) the instruments to be queried
        #   ion - (generated automatically) the polarity of the query spectra
        instrument_types_selected = annotation_query_form.cleaned_data['massbank_instrument_types']
        instrument_list = []
        for instrument in instrument_types_selected:
            # Loop converts unicode to utf-8
            instrument_list.append(str(instrument))
        mail_address = currentUser.email
        parameters = {
            'mail_address': mail_address,
            'instrument_types': instrument_list,
        }
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    elif isinstance(annotation_query_form, NISTQueryForm):
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='NIST')
        # Parameters for NIST are...
        #   number of hits - (selected by user) the maximum number of annotation hits for a spectra
        #   search type - (selected by user) the type of search to be performed
        #   main library - (selected by user) the library to be searched
        maximum_number_of_hits = annotation_query_form.cleaned_data['maximum_number_of_hits']
        selected_libraries = []
        search_type = str(annotation_query_form.cleaned_data['search_type'])
        libraries = annotation_query_form.cleaned_data['query_libraries']
        for library in libraries:
            # Loop converts unicode to utf-8
            selected_libraries.append(str(library))
        parameters = {
            'max_hits': maximum_number_of_hits,
            'search_type': search_type,
            'library': selected_libraries,
        }
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    elif isinstance(annotation_query_form, PrecursorMassFilterForm):
        positive_transforms = annotation_query_form.cleaned_data['positive_transforms']
        parameters = {}
        parameters['positive_transforms'] = positive_transforms
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='Precursor Mass Filter')
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    # elif isinstance(annotation_query_form, NetworkSamplerQueryForm):
    #     annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='LCMS DDA Network Sampler')
    # elif isinstance(annotation_query_form, DefaultQueryForm):
    #     annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='LCMS DDA Network Sampler')


def run_network_sampler(request):
    default_params = {
            'n_samples': 1000,
            'n_burn': 500,
            'delta': 1,
            'transformation_file': 'all_transformations_masses.txt',
        }
    frag_slug = 'beer-3-frag-set-5'
    aq_slug = 'beer-3-annotations-4'
    aq = AnnotationQuery.objects.get(slug=aq_slug)
    fs = FragmentationSet.objects.get(slug=frag_slug)

    pq,created = AnnotationQuery.objects.get_or_create(name='posterior',fragmentation_set=fs,
        massBank='False',massBank_params=jsonpickle.encode(default_params),parent_annotation_query=aq)
    edge_dict = tasks.runNetworkSampler.delay(frag_slug,'Beer_3_T10_POS.mzXML',pq.slug)
    # context_dict = {'edge_dict':  edge_dict}
    # return render(request,'frank/sampler_output.html',context_dict)
    return render(request,'frank/index.html')


def make_frag_spectra_plot(request, fragmentation_set_name_slug, peak_name_slug):
    parent_object = Peak.objects.get(slug = peak_name_slug)
    fragmentation_spectra = Peak.objects.filter(parent_peak = parent_object)

    parent_mass = parent_object.mass
    parent_intensity = parent_object.intensity
    fragment_masses = []
    fragment_intensities = []
    for peak in fragmentation_spectra:
        fragment_masses.append(peak.mass)
        fragment_intensities.append(peak.intensity)

    # define some colours
    parent_fontspec = {
        'size':'10',
        'color':'blue',
        'weight':'bold'
    }

        ###### PSEUDO RELATIVE INTENSITIES ########

        # make blank figure
    figsize=(10, 6)
    fig = plt.figure(figsize=figsize, facecolor='white')
    ax = fig.add_subplot(1,1,1)

    # plot the parent peak first
    plt.plot((parent_mass, parent_mass), (0, parent_intensity), linewidth=2.0, color='b')
    x = parent_mass
    y = parent_intensity
    label = "%.5f" % parent_mass
    plt.text(x, y, label, **parent_fontspec)

    highest_intensity = fragmentation_spectra.aggregate(Max('intensity'))['intensity__max']
    # scale the highest intensity value to the value of the parent intensity

    scale = parent_intensity/highest_intensity

    # plot all the fragment peaks of this parent peak
    num_peaks = len(fragment_masses)
    for j in range(num_peaks):
        mass = fragment_masses[j]
        intensity = (fragment_intensities[j]*scale)
        plt.plot((mass, mass), (0, intensity), linewidth=1.0, color='#FF9933')

    # set range of x- and y-axes
    xlim_upper = int(parent_mass + 50)
    ylim_upper = int(round(parent_intensity*Decimal(1.25)))
    plt.xlim([0, xlim_upper])
    plt.ylim([0, ylim_upper])
    ###########################################

    # show the axes info
    plt.xlabel('m/z')
    plt.ylabel('relative intensity')
    mz_value = ("%.5f" % parent_mass)
    rt_value = ("%.3f" % parent_object.retention_time)
    title = 'MS1 m/z=' + mz_value + ' RT=' + rt_value
    plt.title(title)

    # add legend
    blue_patch = mpatches.Patch(color='blue', label='Parent peak')
    yellow_patch = mpatches.Patch(color='#FF9933', label='Fragment peaks')
    plt.legend(handles=[blue_patch, yellow_patch])

    # change plot tick paramaters
    plt.tick_params(
        axis = 'both',
        which = 'both',
        bottom = 'off',
        top = 'off',
        left = 'off',
        right = 'off',
    )

    buffer = StringIO.StringIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    graphIMG = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    graphIMG.save(buffer, "PNG")
    pylab.close()

    return HttpResponse(buffer.getvalue(), content_type="image/png")