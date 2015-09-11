__author__ = 'Scott Greig'

from django.shortcuts import render
from frank.models import *
from frank.forms import *
from django.contrib.auth.decorators import login_required
from frank import tasks
from decimal import *
from django.db.models import Max
import datetime
import jsonpickle
from django.core.exceptions import ValidationError
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from matplotlib import pylab
from pylab import *
import PIL
import PIL.Image
import StringIO
from django.http import HttpResponse
from django.db import transaction

"""
To reduce code repetition, add a method for the context_dict
of each page here at the top of the page.
"""


def get_my_experiments_context_dict(user):
    """
    Method to generate the context_dict for 'My Experiments' page
    :param user: User object for the current user
    :return: context_dict:  The context dictionary for the page
    """

    experiment_list = Experiment.objects.filter(users=user)
    # Get all the user's experiments
    context_dict = {
        'experiment_list': experiment_list,
    }
    return context_dict


def get_add_experiment_context_dict(form):
    """
    Method to generate the context_dict for the 'Add Experiment' form page
    :param form: ExperimentForm object
    :return: context_dict:  The context dictionary for the page
    """

    context_dict = {
        'experiment_form': form,
    }
    return context_dict


def get_experiment_summary_context_dict(experiment_name_slug):
    """
    Method to generate the context_dictionary for the 'Experiment' page
    :param experiment_name_slug: String containing the unique slug for the experiment
    :return: context_dict:  The context dictionary for the page
    """

    # From the slug, get the experiment, the associated experimental condiditions and fragmentation sets
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    experimental_conditions = ExperimentalCondition.objects.filter(experiment=experiment)
    fragmentation_set_list = FragmentationSet.objects.filter(
        experiment=experiment
    )
    context_dict = {
        'experiment': experiment,
        'conditions': experimental_conditions,
        'fragmentation_sets': fragmentation_set_list,
    }
    return context_dict


def get_add_experimental_condition_context_dict(experiment_name_slug, form):
    """
    Method to generate the context dictionary for the 'Add Experimental' condition page
    :param experiment_name_slug: String containing the unique slug for the experiment
    :param form: ExperimentalConditionForm for the addition of the experimental condition
    :return: context_dict:  The context dictionary for the page
    """

    experiment = Experiment.objects.get(slug=experiment_name_slug)
    context_dict = {
        'experimental_condition_form': form,
        'experiment': experiment,
    }
    return context_dict


def get_condition_summary_context_dict(experiment_name_slug, condition_name_slug):
    """
    Method to generate the context dictionary for the 'Condition Summary' page
    :param experiment_name_slug: String containing the unique slug for the experiment
    :param condition_name_slug: String containing the unique slug for the condition
    :return: context_dict:  The context dictionary for the page
    """

    # Derive the experiment, experimental conditions, samples and sample files for the page
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    experimental_condition = ExperimentalCondition.objects.get(slug=condition_name_slug)
    samples = Sample.objects.filter(experimental_condition=experimental_condition)
    files = SampleFile.objects.filter(sample=samples)
    context_dict = {
        'experiment': experiment,
        'condition': experimental_condition,
        'samples': samples,
        'sample_files': files
    }
    return context_dict


def get_add_sample_context_dict(experiment_name_slug, condition_name_slug, sample_form):
    """
    Method to generate the context_dictionary for the 'Add Sample' page
    :param experiment_name_slug: String containing the unique slug for the experiment
    :param condition_name_slug: String containing the unique slug for the condition
    :param sample_form: SampleForm for the addition of a sample
    :return: context_dict:  The context dictionary for the page
    """

    # Derive both the experiment and experimental conditions for the experiment
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    condition = ExperimentalCondition.objects.get(slug=condition_name_slug)
    context_dict = {
        'experiment': experiment,
        'condition': condition,
        'sample_form': sample_form,
    }
    return context_dict


def get_add_sample_file_context_dict(experiment_name_slug, condition_name_slug, sample_slug, sample_file_form):
    """
    Method to create the context dictionary for the 'Add Sample File' page
    :param experiment_name_slug: String containing the unique slug for the experiment
    :param condition_name_slug: String containing the unique slug for the experimental condition
    :param sample_slug: String containing the unique slug for the experimental sample
    :param sample_file_form: SampleFileForm for the addition of an experimental sample
    :return: context_dict:  The context dictionary for the page
    """

    # The context dictionary includes the experiment, the condition, the sample and the file form
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    experimental_condition = ExperimentalCondition.objects.get(slug=condition_name_slug)
    sample = Sample.objects.get(slug=sample_slug)
    context_dict = {
        'experiment': experiment,
        'condition': experimental_condition,
        'sample': sample,
        'sample_file_form': sample_file_form,
    }
    return context_dict


def get_create_fragmentation_set_context_dict(experiment_name_slug, form):
    """
    Method to generate the context dictionary for the 'Create Fragmentation Set' page
    :param experiment_name_slug:    String containing the unique slug for the experiment
    :param form:    FragmentationSetForm for the addition of a new fragmentation set
    :return: context_dict:  The context dictionary for the page
    """

    experiment = Experiment.objects.get(slug=experiment_name_slug)
    context_dict = {
        'frag_set_form': form,
        'experiment': experiment
    }
    return context_dict


def get_fragmentation_set_summary_context_dict(user):
    """
    Method to generate the context dictionary for the 'My Fragmentation Sets' page
    :param user: User object corresponding to the current user
    :return: context_dict:  The context dictionary for the page
    """

    fragmentation_set_list = []
    # Derive the experiments the user has access to
    user_experiment_list = Experiment.objects.filter(users=user)
    for experiment in user_experiment_list:
        # For each experiment, derive which fragmentation sets are related to the experiment
        experiment_fragment_sets = FragmentationSet.objects.filter(experiment=experiment)
        fragmentation_set_list.extend(experiment_fragment_sets)
    # The list of the user's fragmentation sets is added to the context dictionary
    context_dict = {
        'fragmentation_sets': fragmentation_set_list,
    }
    return context_dict


def get_fragmentation_set_context_dict(fragmentation_set_name_slug, annotation_tool_selection_form):
    """
    Method to generate the context dictionary for the 'Fragmentation Set' page
    :param fragmentation_set_name_slug: String containing the unique slug for the fragmentation set
    :param annotation_tool_selection_form: AnnotationToolSelectionForm for the user to select an annotation tool
    for generating new AnnotationQueries
    :return: context_dict:  The context dictionary for the page
    """

    # Get the corresponding Fragmentation Set
    fragmentation_set_object = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    # Determine the MS1 peaks for display
    ms1_peaks = Peak.objects.filter(fragmentation_set=fragmentation_set_object, msn_level=1)
    number_of_ms1_peaks = len(ms1_peaks)
    # Determine the annotation queries associated with the Fragmentation Set
    annotation_queries = AnnotationQuery.objects.filter(fragmentation_set=fragmentation_set_object)
    # Determine which sample files are included in the Fragmentation Set
    sample_file_ids = ms1_peaks.values("source_file").distinct()
    ms1_peaks_by_file = {}
    # For each sample file in the fragmentation set, determine the MS1 peaks in
    # each sample file and group them by file
    for file_id in sample_file_ids:
        experimental_file = SampleFile.objects.get(id=file_id.get('source_file'))
        ms1_peaks_by_file[experimental_file] = ms1_peaks.filter(source_file=experimental_file).order_by('mass')
    context_dict = {
        'annotation_tool_form': annotation_tool_selection_form,
        'fragment_set': fragmentation_set_object,
        'number_of_peaks': number_of_ms1_peaks,
        'annotations': annotation_queries,
        'peaks_by_file': ms1_peaks_by_file,
    }
    return context_dict


def get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug):
    """
    Method to generate the context dictionary for the 'Peak Summary' page
    :param fragmentation_set_name_slug: String containing the unique slug of the fragmentation set
    :param peak_name_slug:  String containing the unique slug of the Peak
    :return: context_dict:  The context dictionary for the page
    """

    # Retrieve the Fragmentation Set and Peak for the page
    fragmentation_set_object = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    peak = Peak.objects.get(slug=peak_name_slug, fragmentation_set=fragmentation_set_object)
    # Get all peaks which comprise the fragmentation spectrum of the peak
    fragmentation_spectra = Peak.objects.filter(parent_peak=peak).order_by('mass')
    # Get the annotation queries which have been performed on the Fragmentation Set
    associated_annotation_queries = AnnotationQuery.objects.filter(
        fragmentation_set=fragmentation_set_object,
        status='Completed Successfully'
    )
    candidate_annotations = {}
    # Group the candidate annotations by the annotation query which generated them
    for annotation_query in associated_annotation_queries:
        candidate_annotations[annotation_query] = CandidateAnnotation.objects.filter(
            peak=peak,
            annotation_query=annotation_query
        ).order_by('-confidence')
    # Determine the number of peaks in the fragmentation spectra
    number_of_fragments_in_spectra = len(fragmentation_spectra)
    # And determine if the peak has a preferred annotation associated with it
    preferred_annotation = peak.preferred_candidate_annotation
    context_dict = {
        'peak': peak,
        'fragmentation_peak_list': fragmentation_spectra,
        'number_of_fragments': number_of_fragments_in_spectra,
        'candidate_annotations': candidate_annotations,
        'annotation_queries': associated_annotation_queries,
        'preferred_annotation': preferred_annotation,
    }
    return context_dict


def get_define_annotation_query_context_dict(fragmentation_set_name_slug, form, annotation_tool_slug):
    """
    Method to generate the context dictionary for the 'Define Annotation Query' page
    :param fragmentation_set_name_slug: String containing the unique slug of the Fragmentation Set
    :param form:    Subclass of the AnnotationQueryForm specific to the AnnotationTool selected
    :param annotation_tool_slug:    String containing the unique slug of the AnnotationTool
    :return: context_dict:  The context dictionary for the page
    """

    # Get both the FragmentationSet and the AnnotationTool from the database
    fragmentation_set_object = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    annotation_tool = AnnotationTool.objects.get(slug=annotation_tool_slug)
    context_dict = {
        'annotation_query_form': form,
        'fragmentation_set': fragmentation_set_object,
        'annotation_tool': annotation_tool,
    }
    return context_dict


def get_specify_preferred_annotation_context_dict(fragmentation_set_name_slug, peak_name_slug, annotation_id, form):
    """
    Method to generate the context dictionary for the 'Specify Preferred Annotation' page
    :param fragmentation_set_name_slug: String containing the unique slug of the fragmentation set
    :param peak_name_slug:  String containing the unique slug of the peak
    :param annotation_id: String containing the unique 'id' of the annotation
    :param form: PreferredAnnotationForm for the addition of a justification for selection
    :return: context_dict:  The context dictionary for the page
    """

    # Get the fragmentation set, the peak and the annotation object for the page
    fragmentation_set_object = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    peak_object = Peak.objects.get(slug=peak_name_slug)
    annotation_object = CandidateAnnotation.objects.get(id=annotation_id)
    context_dict = {
        'fragmentation_set': fragmentation_set_object,
        'peak': peak_object,
        'annotation': annotation_object,
        'form': form,
    }
    return context_dict

"""
The following are views, which contain the logic for each webpage
of the application.
"""


@login_required
def index(request):
    """
    View to render the index page
    :param request: Get request from the user for the index page.
    :return: render(request, 'frank/index.html'
    """

    return render(request, 'frank/index.html')


@login_required
def my_experiments(request):
    """
    View to render the 'My Experiments' page
    :param request: Get request for the 'My Experiments' page.
    :return: render(request, 'frank/my_experiments.html', context_dict)
    """

    active_user = request.user
    context_dict = get_my_experiments_context_dict(user=active_user)
    return render(request, 'frank/my_experiments.html', context_dict)


@login_required
def add_experiment(request):
    """
    View to add an experiment and render the 'Add Experiment' page.
    :param request: Get or POST request to the 'Add Experiment' page
    :return: render:    Either the my_experiments.html page or add_experiments.html page
    """

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
            # in addition to the experiment creator, the user must be added to
            # as a collaborator to the experiment
            new_user = UserExperiment.objects.create(user=active_user, experiment=experiment)
            # Get the context dictionary of the my_experiments page
            context_dict = get_my_experiments_context_dict(user=active_user)
            return render(request, 'frank/my_experiments.html', context_dict)
        else:
            # if the form is invalid, render the page displaying form errors
            context_dict = get_add_experiment_context_dict(form)
            return render(request, 'frank/add_experiment.html', context_dict)
    else:
        # If the request is a Get request, create a new form and render the page
        form = ExperimentForm()
        context_dict = get_add_experiment_context_dict(form)
        return render(request, 'frank/add_experiment.html', context_dict)


@login_required
def experiment_summary(request, experiment_name_slug):
    """
    View to render the 'Experiment' page
    :param request: Get request for the 'Experiment' page
    :param experiment_name_slug: String containing the unique slug of the experiment
    :return: render:    Render frank/experiment.html
    """

    context_dict = get_experiment_summary_context_dict(experiment_name_slug)
    return render(request, 'frank/experiment.html', context_dict)


@login_required
def add_experimental_condition(request, experiment_name_slug):
    """
    View to render the 'Add Experiment' page, adding experimental conditions
    to an associated experiment.
    :param request: Get or POST request posted to the 'Add Experimental Condition' page
    :param experiment_name_slug:    String containing the unique slug for the associated experiment
    :return: render:    Either renders 'frank/experiment.html' or 'frank/add_experimental_condition.html'
    """

    # Get the experiment the experimental condition is to be associated to
    experiment = Experiment.objects.get(slug=experiment_name_slug)
    # If the request is a POST
    if request.method == 'POST':
        # Retrieve the completed form
        form = ExperimentalConditionForm(request.POST)
        # Check to ensure form contains valid data
        if form.is_valid():
            # Convert the form to an experimental condition object
            condition = form.save(commit=False)
            # Add the experiment to the condition
            condition.experiment = experiment
            # Commit to the database
            condition.save()
            # Get the context dictionary and render the experiment page
            context_dict = get_experiment_summary_context_dict(experiment_name_slug)
            return render(request, 'frank/experiment.html', context_dict)
        else:
            # if the form has errors, render the add_experimental_condition page, displaying the form errors
            context_dict = get_add_experimental_condition_context_dict(experiment_name_slug, form)
            return render(request, 'frank/add_experimental_condition.html', context_dict)
    else:
        # If the request is a Get request, then create a new form
        form = ExperimentalConditionForm()
        # Get the context dictionary and render the 'add_experimental_condition' page
        context_dict = get_add_experimental_condition_context_dict(experiment_name_slug, form)
        return render(request, 'frank/add_experimental_condition.html', context_dict)


@login_required
def condition_summary(request, experiment_name_slug, condition_name_slug):
    """
    View to display an experimental condition, the 'Condition' page
    :param request: Get request for the 'Condition' page
    :param experiment_name_slug: String containing the unique slug for the experiment
    :param condition_name_slug: String containing the unique slug for the condition
    :return: render(request, 'frank/condition.html', context_dict)
    """

    context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
    return render(request, 'frank/condition.html', context_dict)


@login_required
def add_sample(request, experiment_name_slug, condition_name_slug):
    """
    View to add a sample to an experimental condition, rendering the 'Add Sample' page
    :param request: Get request for the 'Add Sample' page
    :param experiment_name_slug: String containing the unique
    :param condition_name_slug: String containing the unique slug for the condition
    :return: render:    Either the 'condition.html' or 'add_sample.html' page
    """

    # Retrieve the experimental condition from the database
    experimental_condition = ExperimentalCondition.objects.get(slug=condition_name_slug)
    # If the request is a POST
    if request.method == 'POST':
        # Extract the user completed form from the POST request
        sample_form = SampleForm(request.POST)
        # Check that the form is valid
        if sample_form.is_valid():
            # Convert the form to a sample object
            sample = sample_form.save(commit=False)
            # Add the associated experimental condition
            sample.experimental_condition = experimental_condition
            # Commit the sample to the database
            sample.save()
            # Get the context diction and render the condition page
            context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
            return render(request, 'frank/condition.html', context_dict)
        else:
            # If the form has errors, then render the 'add_sample' page displaying the form errors
            context_dict = get_add_sample_context_dict(experiment_name_slug, condition_name_slug, sample_form)
            return render(request, 'frank/add_sample.html', context_dict)
    else:
        # If the request is a Get request, then create a new SampleForm
        sample_form = SampleForm()
        # render the 'add_sample' page displaying the new form
        context_dict = get_add_sample_context_dict(experiment_name_slug, condition_name_slug, sample_form)
        return render(request, 'frank/add_sample.html', context_dict)


@login_required
def add_sample_file(request, experiment_name_slug, condition_name_slug, sample_slug):
    """
    View to add a sample file to a sample, rendering the 'Add Sample File' page
    :param request: Either a Get or Post request to the 'Add Sample File' page
    :param experiment_name_slug: String containing the unique slug of the experiment
    :param condition_name_slug: String containing the unique slug of the condition
    :param sample_slug: String containing the unique slug of the sample
    :return: render:    Either the 'condition' page or the 'add_sample_file' page
    """

    # Retrieve the sample from the database
    sample = Sample.objects.get(slug=sample_slug)
    # Check if the request was a POST
    if request.method == 'POST':
        # Extract the completed form from the POST request
        sample_file_form = SampleFileForm(request.POST, request.FILES)
        # Check if the form is valid
        if sample_file_form.is_valid():
            # Convert the form to a new sample file
            new_sample_file = sample_file_form.save(commit=False)
            # Add both the sample and the name of the sample file name
            new_sample_file.sample = sample
            new_sample_file.name = new_sample_file.address.name
            try:
                # The commit of the sample file is performed as an atomic transaction
                # in case a validation error occurs from adding a duplicate sample file
                # to the sample.
                with transaction.atomic():
                    new_sample_file.save()
                # if the new_sample_file is validated, then render the 'condition' page
                context_dict = get_condition_summary_context_dict(experiment_name_slug, condition_name_slug)
                return render(request, 'frank/condition.html', context_dict)
            except ValidationError:
                # Validation error will result from an attempt to add a duplicate
                # file to a sample
                # An error is added to the form here, as the validation error occurs
                # through the checking of the file hierarchy for a duplicate file upon file upload
                sample_file_form.add_error("address", "This file already exists in the sample.")
                # Render the 'add_sample_file' page to the user, indicating
                # that duplicate files cannot be added to the same sample
                context_dict = get_add_sample_file_context_dict(
                    experiment_name_slug,
                    condition_name_slug,
                    sample_slug,
                    sample_file_form
                )
                return render(request, 'frank/add_sample_file.html', context_dict)
        else:
            # If the form itself contains errors (such as not including a file for upload)
            # then render the 'add_sample_file' page indicating errors in the form
            context_dict = get_add_sample_file_context_dict(
                experiment_name_slug,
                condition_name_slug,
                sample_slug,
                sample_file_form
            )
            return render(request, 'frank/add_sample_file.html', context_dict)
    else:
        # if the request is a POST request, then create a new SampleFileForm
        sample_file_form = SampleFileForm()
        # Render the 'add_sample_file' page, displaying the new form
        context_dict = get_add_sample_file_context_dict(
            experiment_name_slug,
            condition_name_slug,
            sample_slug,
            sample_file_form
        )
        return render(request, 'frank/add_sample_file.html', context_dict)


@login_required
def create_fragmentation_set(request, experiment_name_slug):
    """
    View to create a new fragmentation set, via the 'Create Fragmentation Set' page
    :param request: Either a Get or POST request for the 'create_fragmentation_set' page
    :param experiment_name_slug: String containing the unique slug of the experiment
    :return: render:    Either the 'experiment.html' or 'create_fragmentation_set.html' pages
    """

    experiment = Experiment.objects.get(slug=experiment_name_slug)
    # Check if the request is a POST
    if request.method == 'POST':
        # Extract the form from the POST request
        fragment_set_form = FragmentationSetForm(request.POST)
        # Ensure the form is valid
        if fragment_set_form.is_valid():
            # Convert the form to a Fragmentation Set
            new_fragmentation_set = fragment_set_form.save(commit=False)
            # Set the experiment field of the fragmentation set
            new_fragmentation_set.experiment = experiment
            # A fragmentation set cannot be made if the there are no sample files uploaded
            # for the experiment
            # Try and check whether sample files have been uploaded
            source_files = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)
            num_source_files = len(source_files)
            # As long as sample files have been uploaded then the fragmentation set can
            # be added to the database
            if num_source_files > 0:
                new_fragmentation_set.save()
                # Begin the background process of deriving the peaks from the sample files
                input_peak_list_to_database(experiment_name_slug, new_fragmentation_set.id)
                # Render the experiment page, which should display the new fragmentation set
                context_dict = get_experiment_summary_context_dict(experiment_name_slug)
                return render(request, 'frank/experiment.html', context_dict)
            else:
                # However, if there are no sample files uploaded, then an error is added to the form
                fragment_set_form.add_error("name", "No source files found for experiment.")
                # Which is then displayed to the user
                context_dict = get_create_fragmentation_set_context_dict(experiment_name_slug, fragment_set_form)
                return render(request, 'frank/create_fragmentation_set.html', context_dict)
        else:
            # If the form itself contains an error (such as the existance of duplicate name)
            # Render the form, displaying the errors back to the user
            context_dict = get_create_fragmentation_set_context_dict(experiment_name_slug, fragment_set_form)
            return render(request, 'frank/create_fragmentation_set.html', context_dict)
    else:
        # If the request was a Get request, then create a new form
        fragment_set_form = FragmentationSetForm()
        # Render the new form on the 'create_fragmentation_set' page
        context_dict = get_create_fragmentation_set_context_dict(experiment_name_slug, fragment_set_form)
        return render(request, 'frank/create_fragmentation_set.html', context_dict)


@login_required
def fragmentation_set_summary(request):
    """
    View to display a list of the user's fragmentation sets, view 'my_fragmentation_sets.html'
    :param request: May either be a Get or Post request for the 'My Fragmentation Sets' page
    :return: render(request, 'frank/my_fragmentation_sets.html', context_dict)
    """

    current_user = request.user
    context_dict = get_fragmentation_set_summary_context_dict(current_user)
    return render(request, 'frank/my_fragmentation_sets.html', context_dict)


@login_required
def fragmentation_set(request, fragmentation_set_name_slug):
    """
    View to display the contents of a fragmentation set. The page, 'fragmentation_set.html',
    also provides a form for the selection of an AnnotationTool for creating a query.
    :param request: A Get or POST request to the 'Fragmentation Set' page
    :param fragmentation_set_name_slug: A string containing the unique slug of the Fragmentation Set
    :return: render:    Either the 'define_annotation_query.html' or 'fragmentation_set.html' pages
    """

    # Check to see if the request is a POST
    if request.method == 'POST':
        # Derive the form from the request
        annotation_tool_selection_form = AnnotationToolSelectionForm(request.POST)
        experiment = FragmentationSet.objects.get(slug=fragmentation_set_name_slug).experiment
        # Check the form is valid
        if annotation_tool_selection_form.is_valid():
            # The annotation_tool_selection form does not directly, correspond to a model
            # as most of the forms do. In this case, we are only interested in extracting the
            # user's choice of tool.
            user_tool_choice = annotation_tool_selection_form.cleaned_data['tool_selection'].name
            annotation_query_form = None
            # Check to see what selection the user made, each form is unique to the
            # annotation tool and may vary according to the experimental protocol used
            if user_tool_choice == 'MassBank':
                annotation_query_form = MassBankQueryForm(experiment_object=experiment)
            elif user_tool_choice == 'NIST':
                annotation_query_form = NISTQueryForm(experiment_object=experiment)
            elif user_tool_choice == 'LCMS DDA Network Sampler':
                annotation_query_form = NetworkSamplerQueryForm()
            elif user_tool_choice == 'Precursor Mass Filter':
                annotation_query_form = PrecursorMassFilterForm(fragmentation_set_name_slug)
            elif user_tool_choice == 'Clean Annotations':
                annotation_query_form = CleanFilterForm(fragmentation_set_name_slug)
            # For the context dictionary, the annotation tool slug is required to render the page
            annotation_tool_slug = AnnotationTool.objects.get(name=user_tool_choice).slug
            # redirect the user to the 'define_annotation_query' page which displays the form
            context_dict = get_define_annotation_query_context_dict(
                fragmentation_set_name_slug,
                annotation_query_form,
                annotation_tool_slug
            )
            return render(request, 'frank/define_annotation_query.html', context_dict)
        else:
            # If the form is not valid (i.e. the choice of tool doesn't correspond to an AnnotationTool in the database)
            context_dict = get_fragmentation_set_context_dict(
                fragmentation_set_name_slug,
                annotation_tool_selection_form
            )
            return render(request, 'frank/fragmentation_set.html', context_dict)
    else:
        # In the case of a Get request, the 'fragmentation set' page is simply
        # rendered containing a new AnnotationToolSelectionForm
        fragmentation_set = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
        experiment = fragmentation_set.experiment
        form = AnnotationToolSelectionForm(experiment_object=experiment)
        context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug, form)
        return render(request, 'frank/fragmentation_set.html', context_dict)


@login_required
def peak_summary(request, fragmentation_set_name_slug, peak_name_slug):
    """
    View to display the fragmentation spectra of a peak and any candidate annotations
    on the 'Peak Summary' page.
    :param request: A Get request for the 'Peak Summary' page
    :param fragmentation_set_name_slug: A string containing the unique slug of the fragmentation set
    :param peak_name_slug:  A string containing the unique slug of the peak
    :return: render(request, 'frank/peak_summary.html', context_dict)
    """

    context_dict = get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug)
    return render(request, 'frank/peak_summary.html', context_dict)


@login_required
def define_annotation_query(request, fragmentation_set_name_slug, annotation_tool_slug):
    """
    View to specify the search parameters of an AnnotationQuery, via the
    'define_annotation_query' page.
    :param request:     Either a Get or POST request for the 'Define Annotation Query' page
    :param fragmentation_set_name_slug: A string containing the unique slug of the fragmentation set
    :param annotation_tool_slug: A string containing the unique slug of the annotation tool
    :return: render:    Either the 'fragmentation_set.html' or 'define_annotation_query.html' page
    """

    # Get the fragmentation set, annotation tool and experiment for the query
    fragmentation_set_object = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
    annotation_tool = AnnotationTool.objects.get(slug=annotation_tool_slug)
    annotation_query_form = None
    experiment = fragmentation_set_object.experiment
    # If the request method is a POST
    if request.method == 'POST':
        # Extract the form, depending on the AnnotationTool specified
        if annotation_tool.name == 'MassBank':
            annotation_query_form = MassBankQueryForm(request.POST, experiment_object=experiment)
        elif annotation_tool.name == 'NIST':
            annotation_query_form = NISTQueryForm(request.POST, experiment_object=experiment)
        elif annotation_tool.name == 'LCMS DDA Network Sampler':
            annotation_query_form = NetworkSamplerQueryForm(request.POST)
        elif annotation_tool.name == 'Precursor Mass Filter':
            annotation_query_form = PrecursorMassFilterForm(fragmentation_set_name_slug,request.POST)
        elif annotation_tool.name == 'Clean Annotations':
            annotation_query_form = CleanFilterForm(fragmentation_set_name_slug,request.POST)
        # Check that the form is valid
        if annotation_query_form.is_valid():
            # Check that the form is valid
            new_annotation_query = annotation_query_form.save(commit=False)
            # Add the fragmentation set to the new annotation query
            new_annotation_query.fragmentation_set = fragmentation_set_object
            current_user = request.user
            # Store the user-specified parameters for the annotation query
            # in the new AnnotationQuery object
            paramaterised_query_object = set_annotation_query_parameters(
                new_annotation_query,
                annotation_query_form,
                current_user
            )
            # Finally commit the query to the database
            paramaterised_query_object.save()
            # This section added by Simon
            parameters = jsonpickle.decode(paramaterised_query_object.annotation_tool_params)
            if 'parents' in parameters:
                for a in parameters['parents']:
                    parent_query = AnnotationQuery.objects.get(slug=a)
                    AnnotationQueryHierarchy.objects.create(
                        parent_annotation_query=parent_query,
                        subquery_annotation_query=paramaterised_query_object)
            # End of Simon's addition
            # Finally, begin running the retrieval of the annotations as a background process
            generate_annotations(paramaterised_query_object,user = request.user)
            # Return the user to the 'fragmentation_set' page
            form = AnnotationToolSelectionForm(experiment_object=experiment)
            context_dict = get_fragmentation_set_context_dict(fragmentation_set_name_slug, form)
            return render(request, 'frank/fragmentation_set.html', context_dict)
        else:
            # If the form is invalid then display the form errors back to the user
            context_dict = get_define_annotation_query_context_dict(
                fragmentation_set_name_slug,
                annotation_query_form,
                annotation_tool_slug
            )
            return render(request, 'frank/define_annotation_query.html', context_dict)
    else:
        # If the request is a Get request, then create a new form, specific to the annotation
        # tool and render the page.
        if annotation_tool.name == 'MassBank':
            annotation_query_form = MassBankQueryForm(experiment_object=experiment)
        elif annotation_tool.name == 'NIST':
            annotation_query_form = NISTQueryForm(experiment_object=experiment)
        elif annotation_tool.name == 'LCMS DDA Network Sampler':
            annotation_query_form = NetworkSamplerQueryForm()
        elif annotation_tool.name == 'Precursor Mass Filter':
            annotation_query_form = PrecursorMassFilterForm(fragmentation_set_name_slug)
        elif annotation_tool.name == 'Clean Annotations':
            annotation_query_form = CleanFilterForm(fragmentation_set_name_slug)
        context_dict = get_define_annotation_query_context_dict(
            fragmentation_set_name_slug,
            annotation_query_form,
            annotation_tool_slug
        )
        return render(request, 'frank/define_annotation_query.html', context_dict)


@login_required
def specify_preferred_annotation(request, fragmentation_set_name_slug, peak_name_slug, annotation_id):
    """
    View to select a preferred candidate annotation from those associated with
    a given peak.
    :param request: Either a Get or POST request for the page
    :param fragmentation_set_name_slug: A string containing the unique slug of the fragmentation set
    :param peak_name_slug: A string containing the unique slug of the peak
    :param annotation_id: Integer for the unique primary key of the candidate annotation
    :return: render:    Either the 'peak_summary' or 'specify_preferred_annotation' page
    """

    # If the request if a POST
    if request.method == 'POST':
        # Extract the PreferredAnnotationForm from the POST request
        preferred_annotation_form = PreferredAnnotationForm(request.POST)
        # Ensure the form is valid
        if preferred_annotation_form.is_valid():
            # The form does not directly correspond to a model,
            # therefore the justification is simply extracted from the form
            justification_for_annotation = preferred_annotation_form.cleaned_data['preferred_candidate_description']
            # In addition to the justification, the user making the selection
            # and the date/time of modification is added
            current_user = request.user
            current_time = datetime.datetime.now()
            annotation_object = CandidateAnnotation.objects.get(id=annotation_id)
            # Then update the peak, to include the preferred annotation
            peak_for_update = Peak.objects.get(slug=peak_name_slug)
            peak_for_update.preferred_candidate_annotation = annotation_object
            peak_for_update.preferred_candidate_description = justification_for_annotation
            peak_for_update.preferred_candidate_user_selector = current_user
            peak_for_update.preferred_candidate_updated_date = current_time
            with transaction.atomic():
                peak_for_update.save()
            # Return the user to the 'peak_summary' page
            context_dict = get_peak_summary_context_dict(fragmentation_set_name_slug, peak_name_slug)
            return render(request, 'frank/peak_summary.html', context_dict)
        else:
            # If the form is invalid, then render the errors back to the user
            context_dict = get_specify_preferred_annotation_context_dict(
                fragmentation_set_name_slug,
                peak_name_slug,
                annotation_id,
                preferred_annotation_form
            )
            return render(request, 'frank/specify_preferred_annotation.html', context_dict)
    else:
        # If the request is a Get request, then create a new PreferredAnnotationForm and render the page
        preferred_annotation_form = PreferredAnnotationForm()
        context_dict = get_specify_preferred_annotation_context_dict(
            fragmentation_set_name_slug,
            peak_name_slug,
            annotation_id,
            preferred_annotation_form
        )
        return render(request, 'frank/specify_preferred_annotation.html', context_dict)


"""
Any additional methods, which the views depend upon may be added here.
Typically, these relate to the background processes but are not themselves
run in the background.
"""


def input_peak_list_to_database(experiment_name_slug, fragmentation_set_id):

    """
    Method to start the extraction of peaks from the uploaded mzXML data files
    :param experiment_name_slug: A string containing the unique slug of an experiment
    :param fragmentation_set_id: Integer id of the fragmentation set
    """

    experiment = Experiment.objects.get(slug=experiment_name_slug)
    # Determine the type of experimental protocol used
    experiment_type = experiment.detection_method.name
    if experiment_type == 'Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition':
        # Run the LCMS-DDA peak extraction task in the background
        tasks.msn_generate_peak_list.delay(experiment_name_slug, fragmentation_set_id)
    elif experiment_type == 'Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation':
        tasks.gcms_generate_peak_list.delay(experiment_name_slug, fragmentation_set_id)
        # Run the LCMS-DDA peak extraction task in the background


def generate_annotations(annotation_query_object,user = None):

    """
    Method to begin the retrieval of candidate annotations as a background task
    :param annotation_query_object: The Annotation Query to be performed
    """

    annotation_tool = annotation_query_object.annotation_tool
    if annotation_tool.name == 'MassBank':
        # If MassBank is to be queried, run the batch search as a background process
        tasks.massbank_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'NIST':
        # If NIST is to be queried, run the batch service as a background process
        tasks.nist_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'LCMS DDA Network Sampler':
        # To be added later by Simon for the LCMS Network Sampler
        pass
    elif annotation_tool.name == 'Precursor Mass Filter':
        tasks.precursor_mass_filter(annotation_query_object.id)
    elif annotation_tool.name == 'Clean Annotations':
        tasks.clean_filter(annotation_query_object.id,user)


def set_annotation_query_parameters(annotation_query_object, annotation_query_form, current_user):

    """
    Method to format the annotation query parameters specified by the user into a
    jsonpickle format for storage in the database
    :param annotation_query_object: The Annotation Query object to be populated
    :param annotation_query_form: The AnnotationQueryForm, from which the parameters are to be derived
    :param current_user: The object corresponding to the current user of the application
    :return: annotation_query_object: The AnnotationQuery object is returned with the search parameters populated
    """

    # Determine if the Form is for MassBank
    if isinstance(annotation_query_form, MassBankQueryForm):
        # Set the annotation tool which is to be used
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='MassBank')

        """
        Parameters for MassBank are...
           type - (hardcoded) the type of search (1 = batch search)
           mail_address - (generated automatically) the email of the recipiant of the results
           query_spectra - (generated automatically) retrieved from the database
           instruments - (selected by user) the instruments to be queried
           ion - (generated automatically) the polarity of the query spectra
        """

        # Determine the instrumentation choices the user has selected.
        # These correspond to distinct libraries of reference spectra in 'MassBank'
        instrument_types_selected = annotation_query_form.cleaned_data['massbank_instrument_types']
        instrument_list = []
        for instrument in instrument_types_selected:
            # Loop converts unicode to utf-8
            instrument_list.append(str(instrument))
        # Get the mail address of the user
        mail_address = current_user.email
        parameters = {
            'mail_address': mail_address,
            'instrument_types': instrument_list,
        }
        # Pickle the parameters for storage in the database
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        # return the populated annotation query object
        return annotation_query_object

    # Else, the annotation query could correspond to NIST
    elif isinstance(annotation_query_form, NISTQueryForm):
        # Populate the annotation tool into the query object
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='NIST')

        """
        Parameters for NIST are...
           number of hits - (selected by user) the maximum number of annotation hits for a spectra
           search type - (selected by user) the type of search to be performed
           main library - (selected by user) the library to be searched
        """

        # Determine the maximum number of hits the user wishes to be returned
        maximum_number_of_hits = annotation_query_form.cleaned_data['maximum_number_of_hits']
        selected_libraries = []
        # Determine which search type the user wishes to perform and on which reference libraries within NIST
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
        # Pickle the parameters and add them to the annotation_query_object
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    # Simon contribution
    elif isinstance(annotation_query_form, PrecursorMassFilterForm):
        parameters = {}
        parameters['positive_transforms'] = annotation_query_form.cleaned_data['positive_transforms']
        parameters['negative_transforms'] = annotation_query_form.cleaned_data['negative_transforms']
        parameters['parents'] = annotation_query_form.cleaned_data['parent_annotation_queries']
        parameters['mass_tol'] = annotation_query_form.cleaned_data['mass_tol']
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='Precursor Mass Filter')
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    elif isinstance(annotation_query_form, CleanFilterForm):
        parameters = {}
        parameters['parents'] = annotation_query_form.cleaned_data['parent_annotation_queries']
        parameters['preferred_threshold'] = annotation_query_form.cleaned_data['preferred_threshold']
        parameters['delete_original'] = annotation_query_form.cleaned_data['delete_original']
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='Clean Annotations')
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    # End of Simon contribution


def run_network_sampler(request):

    """
    Method for testing the Network sampler.
    __author__: Simon Rogers
    :param request:
    :return:
    """

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
    return render(request, 'frank/index.html')


def make_frag_spectra_plot(request, fragmentation_set_name_slug, peak_name_slug):
    """

    :param request: The request a Get from the 'peak_summary'page
    :param fragmentation_set_name_slug: A string corresponding to the unique slug of the fragmentation set
    :param peak_name_slug: A string corresponding to the unique slug of a peak
    :return: HttpResponse: An image of the graph is returned to the page for rendering
    """

    # Get the peak and derive all the peaks which correspond to the fragmentation spectra
    parent_object = Peak.objects.get(slug=peak_name_slug)
    fragmentation_spectra = Peak.objects.filter(parent_peak=parent_object)

    # Derive the mass and intensity of the parent, and the fragments of the spectra
    parent_mass = parent_object.mass
    parent_intensity = parent_object.intensity
    fragment_masses = []
    fragment_intensities = []
    for peak in fragmentation_spectra:
        fragment_masses.append(peak.mass)
        fragment_intensities.append(peak.intensity)

    # define some colours
    parent_fontspec = {
        'size': '10',
        'color': 'blue',
        'weight': 'bold'
    }

    # make blank figure
    figsize = (10, 6)
    fig = plt.figure(figsize=figsize, facecolor='white')
    ax = fig.add_subplot(1, 1, 1)

    # plot the parent peak first
    plt.plot((parent_mass, parent_mass), (0, parent_intensity/parent_intensity), linewidth=2.0, color='b')
    x = parent_mass
    y = parent_intensity/parent_intensity
    label = "%.5f" % parent_mass
    plt.text(x, y, label, **parent_fontspec)

    if len(fragmentation_spectra) > 0:
        highest_intensity = fragmentation_spectra.aggregate(Max('intensity'))['intensity__max']
        scale = parent_intensity/highest_intensity
    else:
        scale = 1
    # scale the highest intensity value to the value of the parent intensity
    """
    Due to the relatively low intensities of the product ions, the fragments
    must be scaled (in intensity) relative to the parent ion to allow for
    visual comparison. Otherwise the graph would be redundant to the users.
    """

    # plot all the fragment peaks of this parent peak
    num_peaks = len(fragment_masses)
    for j in range(num_peaks):
        mass = fragment_masses[j]
        intensity = (fragment_intensities[j]*scale/parent_intensity)
        plt.plot((mass, mass), (0, intensity), linewidth=1.0, color='#FF9933')

    # set range of x- and y-axes
    xlim_upper = int(parent_mass + 50)
    ylim_upper = 1.5
    plt.xlim([0, xlim_upper])
    plt.ylim([0, ylim_upper])

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
        axis='both',
        which='both',
        bottom='off',
        top='off',
        left='off',
        right='off',
    )

    # Render the graph on a canvas
    buffer = StringIO.StringIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()
    graphIMG = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    graphIMG.save(buffer, "PNG")
    pylab.close()
    # Return the graph to the page, allowing for display
    return HttpResponse(buffer.getvalue(), content_type="image/png")