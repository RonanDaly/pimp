from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from frank.models import *
from frank.forms import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from frank import tasks
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
#matplotlib inline
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import patches as mpatches
from decimal import *
from django.db.models import Max
import re

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
    context_dict = {
        'experiment': experiment,
        'conditions': experimental_conditions,
        'fragmentation_sets': fragmentation_set_list,
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

def get_fragmentation_set_context_dict(fragmentation_set_name_slug):
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
        'fragment_set': fragmentation_set,
        'number_of_peaks':number_of_ms1_peaks,
        'annotations': annotation_queries,
        'peaks_by_file': ms1_peaks_by_file,
    }
    return context_dict


def get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug):
    fragmentation_set = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    peak = Peak.objects.get(slug=peak_name_slug, fragmentation_set = fragmentation_set)
    ## Display number of msn peaks
    fragmentation_spectra = Peak.objects.filter(parent_peak = peak)
    associated_annotation_queries = AnnotationQuery.objects.filter(fragmentation_set = fragmentation_set)
    candidate_annotations = {}
    for annotation_query in associated_annotation_queries:
        candidate_annotations[annotation_query] = CandidateAnnotation.objects.filter(peak=peak,annotation_query=annotation_query).order_by('-confidence')
    number_of_fragments_in_spectra = len(fragmentation_spectra)
    context_dict = {
        'peak': peak,
        'fragmentation_peak_list': fragmentation_spectra,
        'number_of_fragments':number_of_fragments_in_spectra,
        'candidate_annotations' : candidate_annotations,
        'annotation_queries': associated_annotation_queries,
    }
    return context_dict


def get_define_annotation_query_context_dict(fragmentation_set_name_slug, form):
    fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    context_dict = {
        'annotation_query_form': form,
        'fragmentation_set': fragmentation_set,
    }
    return context_dict

# Create your views here.

# View for the Index page of frank
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
            new_user = UserExperiments.objects.create(user = active_user, experiment = experiment)
            context_dict = get_my_experiments_context_dict(user = active_user)
            return render(request, 'frank/my_experiments.html', context_dict)
        else:
            # if the form is invalid, display the errors
            print form.errors
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
            print form.errors
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
            print sample_form.errors
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
            new_sample.save()
            context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
            return render(request, 'frank/condition.html', context_dict)
        else:
            print sample_file_form.errors
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
            new_fragmentation_set.save()
            input_peak_list_to_database(experiment_name_slug, new_fragmentation_set.id)
            context_dict = get_experiment_summary_context_dict(experiment_name_slug)
            return render(request, 'frank/experiment.html', context_dict)
        else:
            print fragment_set_form.errors
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
    context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug)
    return render(request, 'frank/fragmentation_set.html', context_dict)


@login_required
def peak_summary(request, fragmentation_set_name_slug, peak_name_slug):
    context_dict = get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug)
    return render(request, 'frank/peak_summary.html', context_dict)


@login_required
def define_annotation_query(request, fragmentation_set_name_slug):
    fragmentation_set = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    if request.method == 'POST':
        annotation_query_form = AnnotationQueryForm(request.POST)
        if annotation_query_form.is_valid():
            new_annotation_query = annotation_query_form.save(commit=False)
            new_annotation_query.fragmentation_set = fragmentation_set
            if new_annotation_query.massBank == True:
                ## Need to build the massBank parameters and store them
                massbank_mail_address = request.user.email
                massbank_instrument_types = annotation_query_form.cleaned_data['mass_bank_instrument_types']
                # MassBank parameters take the format email;instrumenttype1,instrumenttype2;
                mass_bank_params = []
                mass_bank_params.append('Email:<'+massbank_mail_address+'>\n')
                instrument_types = []
                instrument_types.append('Instrument Types:')
                for instrument in massbank_instrument_types:
                    name_of_instrument = str(instrument)
                    instrument_types.append('<'+name_of_instrument+'>')
                mass_bank_params.append(''.join(instrument_types))
                new_annotation_query.massBank_params = ''.join(mass_bank_params)
            new_annotation_query.save()
            generate_annotations(fragmentation_set, new_annotation_query)
            context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug)
            return render(request, 'frank/fragmentation_set.html', context_dict)
        else:
            print annotation_query_form.errors
            context_dict = get_define_annotation_query_context_dict(fragmentation_set_name_slug, annotation_query_form)
            return render(request, 'frank/define_annotation_query.html', context_dict)
    else:
        annotation_query_form = AnnotationQueryForm()
        context_dict = get_define_annotation_query_context_dict(fragmentation_set_name_slug, annotation_query_form)
        return render(request, 'frank/define_annotation_query.html', context_dict)


### Additional methods go here

def input_peak_list_to_database(experiment_name_slug, fragmentation_set_id):
    ## Remember to add the msnAnalysis method onto celery
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experiment_type = experiment.detection_method
    if experiment_type == 'LCMS DDA':
        tasks.msnGeneratePeakList.delay(experiment_name_slug, fragmentation_set_id)
    elif experiment_type == 'GCMS EII':
        tasks.gcmsGeneratePeakList.delay(experiment_name_slug, fragmentation_set_id)


def generate_annotations(fragmentation_set, annotation_query):
    fragmentation_set_id = fragmentation_set.id
    annotation_query_id = annotation_query.id
    if annotation_query.massBank == True:
        tasks.massBank_batch_search.delay(fragmentation_set_id, annotation_query_id)
    if annotation_query.nist == True:
        tasks.nist_batch_search.delay(fragmentation_set_id, annotation_query_id)


def run_network_sampler(request):
    import jsonpickle
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


def make_spectra_plot(request, fragmentation_set_name_slug, peak_name_slug):
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

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
