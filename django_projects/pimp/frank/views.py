__author__ = 'Scott Greig'
from djcelery import celery
from django.shortcuts import render,redirect
from frank.models import *
from frank.forms import *
from django.contrib.auth.decorators import login_required
from frank import tasks
from frank import annotationTools
from decimal import *
from django.db.models import Max
import datetime
import jsonpickle
from django.core.exceptions import ValidationError
import StringIO
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
import json
import csv
import numpy as np
from matplotlib import patches as mpatches
from matplotlib import pyplot as plt
from matplotlib import pylab
import PIL

from experiments.models import Analysis
from projects.models import Project
from frank.annotationTools import ChemSpiderQueryTool
import logging
from celery.utils.log import get_task_logger

celery_logger = get_task_logger(__name__)
logger = logging.getLogger(__name__)

from MS2LDA.visualisation.networkx import lda_visualisation

try:
    from django.utils import simplejson
except:
    import json as simplejson
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

# returns the plot data for the MS2LDA visualisation graphs -
#  - topic_peaks: list MS1 peaks for each topic
#  - topic_fragments: fragmentation peaks for topic/ms1
#  - fragmentation_spectra: fragmentation spectra for each MS1 peak

def get_topic_graph_data (docdf, topicdf, ms2, mass2motif_count):

    topic_peaks = {}
    topic_fragments = {}
    fragmentation_spectra = {}
    max_topics=mass2motif_count

    for topic in range(0,max_topics):

        print ("   Mass2Motif "+str(topic)+" : building MS1 peak, MS2 Spectra and topic fragment data")
        ms2_rel_intensity = {}  #holds the relative intensity for each MS2 - used to populate the peaks in topic frags
        # get the peak ids for this topic
        column_values=np.array(docdf.columns.values)
        doc_dist = docdf.iloc[[topic]].as_matrix().flatten()
        # argsort in ascending order
        idx = np.argsort(doc_dist)[::-1]
        topic_d = np.array(column_values)[idx]
        topic_p = np.array(doc_dist)[idx]
        # pick the documents with non-zero values
        nnz_idx = topic_p > 0
        top_n_docs = topic_d[nnz_idx]
        parent_ids_mz=[]
        parent_ids=[]
        parent_frag_spectra=[]   #fragment spectra for each parent
        for peak in top_n_docs:
            #split the mz_rt_peakid string into tokens
            tokens = peak.split('_')
            peakid = int(tokens[2])
            parent_ids.append(peakid)
            mz = float(tokens[0])
            #rt = float(tokens[1])
            parent_peak=[]
            parent_peak.append([mz,100,peakid])
            parent_ids_mz.append(parent_peak)
            # get the fragmentation spectra for this ms1
            ms2_rows = ms2.loc[ms2['MSnParentPeakID']==peakid]
            peakids = ms2_rows[['peakID']]
            mzs = ms2_rows[['mz']]
            intensities = ms2_rows[['intensity']]
            parentids = ms2_rows[['MSnParentPeakID']]
            # convert from pandas dataframes to list
            peakids = peakids.values.ravel().tolist()
            mzs = mzs.values.ravel().tolist()
            intensities = intensities.values.ravel().tolist()
            max_intensity = max(intensities)
            relative_intensities = [100.0*i/max_intensity for i in intensities]
            parentids = parentids.values.ravel().tolist()
            # save the data into list
            items=[]
            for n in range(len(peakids)):
                mz = mzs[n]
                intensity = relative_intensities[n]
                peakid=peakids[n]
                item = (mz, intensity,peakid)
                ms2_rel_intensity[peakid]=intensity
                items.append(item)
            parent_frag_spectra.append(items)
        topic_peaks[topic]=parent_ids_mz
        fragmentation_spectra[topic]=parent_frag_spectra

        # get the fragment data for this topic
        column_values=np.array(topicdf.transpose().columns.values)
        word_dist = topicdf.transpose().iloc[[topic]].as_matrix().flatten()
        # argsort in ascending order
        idx = np.argsort(word_dist)[::-1]
        topic_w = np.array(column_values)[idx]
        topic_p = np.array(word_dist)[idx]
        # pick the words with non-zero values
        nnz_idx = topic_p > 0
        topic_w = topic_w[nnz_idx]
        topic_p = topic_p[nnz_idx]
        # split the words into fragment word tokens
        fragments = []
        fragments_p= []
        for w,p in zip (topic_w, topic_p):
            if w.startswith('fragment'):
                fragments.append(w)
                fragments_p.append(p)
        parent_topic_fragments = {}
        for t in zip(fragments, fragments_p):
            fragment = t[0]
            tokens = fragment.split('_')
            bin_id = tokens[1]
            bin_prob = t[1]
            ms2_rows = ms2.loc[ms2['fragment_bin_id']==bin_id]

            ms2_rows = ms2_rows.loc[ms2_rows['MSnParentPeakID'].isin(parent_ids)]

            peakids = ms2_rows[['peakID']]
            mzs = ms2_rows[['mz']]
            intensities = ms2_rows[['intensity']]
            parentids = ms2_rows[['MSnParentPeakID']]

            # convert from pandas dataframes to list
            peakids = peakids.values.ravel().tolist()
            mzs = mzs.values.ravel().tolist()
            intensities = intensities.values.ravel().tolist()
            parentids = parentids.values.ravel().tolist()

            for n in range(len(parentids)):
                parentid = parentids[n]
                mz = mzs[n]
                intensity = intensities[n]
                peakid = peakids[n]
                word = fragment
                item = (mz, ms2_rel_intensity[peakid],peakid)
                if parentid in parent_topic_fragments:
                    existing_list = parent_topic_fragments[parentid]
                    existing_list.append(item)
                else:
                    new_list = [item]
                    parent_topic_fragments[parentid] = new_list

        #covert from dict to list
        parent_topic_fragments_list = []
        for j,k in enumerate(topic_peaks[topic]):
            parentid=k[0][2]
            if parentid in parent_topic_fragments:
                parent_topic_fragments_list.append(parent_topic_fragments[parentid])
            else:
                parent_topic_fragments_list.append([])

        topic_fragments[topic]=parent_topic_fragments_list

    return topic_peaks, topic_fragments, fragmentation_spectra


def get_ms2lda_vis_context_dict(fragmentation_set_name_slug, annotation_id):
    """
    Method to generate the context dictionary for the MS2LDA visualisation page
    :param fragmentation_set_name_slug: String containing the unique slug of the fragmentation set
    :param annotation_id:  number containing the unique slug of the annotatio
    :return: context_dict:  The context dictionary for the page
    """

    # resume project from file for this annotation
    print "Reading MS2LDA project file ..."
    ms2lda_dir=os.environ['HOME']+"/ms2lda_data/"  # directory holding MS2LDA project files
    ms2lda=tasks.Ms2Lda.resume_from(ms2lda_dir+"ms2lda_"+str(annotation_id)+".project")

    # get the data needed for the graphs -
    #   - ms1 peak data for each topic (for MS2 Spectra graph and Parent Ion graph)
    #   - fragment peaks associated with a topic/ms1 (for Parent Ion graph)
    #   - fragment spectra or each MS1 peak (for MS2 Spectra graph)
    print "Extracting data from MS2LDA object for MS2LDA graphs..."
    topic_peaks, topic_fragments, fragmentation_spectra = \
                     get_topic_graph_data (ms2lda.docdf, ms2lda.topicdf, ms2lda.ms2, ms2lda.mass2motif_count)


    topic_data=[]    # holds the parent peak, fragment spectra and topic fragments for each topic
    max_topics=ms2lda.mass2motif_count
    for i in range(max_topics):
        topic_data.append(0)

    for topic,topic_peaks_content in topic_peaks.iteritems():

        # Convert topic_fragments[topic] from dict to list
        # extract the peaks & associated fragments that are in this topic
        topic_data[topic]=[fragmentation_spectra[topic],topic_peaks[topic],topic_fragments[topic]]

    # get the annotation name
    annotation_query=AnnotationQuery.objects.get(id=annotation_id)

    # build json data needed for graph html
    to_highlight=None   # default to this.
    degree=20		# default to this.
    json_data,G = lda_visualisation.get_json_from_docdf(ms2lda.docdf.transpose(),to_highlight,degree)

    #DEBUG - Need to fix this. Currently when passing graph directly via contect dict there are
    #DEBUG   issues. Instead, will pass the data via file which is read in on the javascript
    json_outfile = ms2lda_dir+"graph.json"    
    with open(json_outfile, 'w') as f:
        json.dump(json_data, f, sort_keys=True, indent=4, ensure_ascii=False)

    context_dict = {
        'fragment_slug': fragmentation_set_name_slug,
        'annotation_name': annotation_query.name,
        'graph' : json.dumps(json_data),
        'topic_data' : json.dumps(topic_data)
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

    fragments = []
    plot_fragments = []
    if len(fragmentation_spectra) > 0:
        intensities = [float(i.intensity) for i in fragmentation_spectra]
        max_intensity = max(intensities)
        relative_intensities = [100.0*i/max_intensity for i in intensities]

        for i,fragment_peak in enumerate(fragmentation_spectra):
            fragments.append((fragment_peak,relative_intensities[i]))
            plot_fragments.append((float(fragment_peak.mass),relative_intensities[i]))

    parent_peak = []
    parent_peak.append((float(peak.mass),100))

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
        # 'fragmentation_peak_list': fragmentation_spectra,
        'number_of_fragments': number_of_fragments_in_spectra,
        'candidate_annotations': candidate_annotations,
        'annotation_queries': associated_annotation_queries,
        'preferred_annotation': preferred_annotation,
        'fragments': fragments,
        'plot_fragments': json.dumps(plot_fragments),
        'plot_parent': json.dumps(parent_peak),
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
def get_chemspider_info(request, compound_id):

    if request.is_ajax():
        csid_generator = ChemSpiderQueryTool()
        csid_generator.populate_compound_csid(compound_id)

        compound = Compound.objects.get(pk=compound_id)

        data = {"compound_id": compound_id, "image_url": compound.image_url, "cs_url": compound.cs_url, "csid": compound.csid, "cs_name": compound.name}
        print "the data being returned is", data

        response = simplejson.dumps(data)

        print "the response is", response

        return HttpResponse(response, content_type='application/json')
    else:
        raise PermissionDenied




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
            # SampleFile -> Sample -> experimental_condition -> experiment - KmcL
            source_files = SampleFile.objects.filter(sample__experimental_condition__experiment=experiment)
            num_source_files = len(source_files)
            # As long as sample files have been uploaded then the fragmentation set can
            # be added to the database
            if num_source_files > 0:
                new_fragmentation_set.save()              # Begin the background process of deriving the peaks from the sample files
                input_peak_list_to_database(experiment_name_slug, new_fragmentation_set.id)
                # Redirect to the the experiment page, which should display the new fragmentation set
                url = reverse('experiment_summary', kwargs={'experiment_name_slug': experiment_name_slug})
                return HttpResponseRedirect(url)
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
            elif user_tool_choice == 'SIRIUS':
                annotation_query_form = SIRIUSQueryForm(experiment_object=experiment)
            elif user_tool_choice == 'NIST':
                annotation_query_form = NISTQueryForm(experiment_object=experiment)
            elif user_tool_choice == 'LCMS DDA Network Sampler':
                annotation_query_form = NetworkSamplerForm()
            elif user_tool_choice == 'Precursor Mass Filter':
                annotation_query_form = PrecursorMassFilterForm(fragmentation_set_name_slug)
            elif user_tool_choice == 'Clean Annotations':
                annotation_query_form = CleanFilterForm(fragmentation_set_name_slug)
            elif user_tool_choice == 'Network Sampler':
                annotation_query_form = NetworkSamplerForm(fragmentation_set_name_slug)
            elif user_tool_choice == 'MS2LDA':
                annotation_query_form = MS2LDAQueryForm()

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
def mass2lda_vis(request, fragmentation_set_name_slug,annotation_id):
    """
    View to display the MS2LDA visualisation screen.
    :param request: A Get request for the 'MS2LDA annotation' page
    :param fragmentation_set_name_slug: A string containing the unique slug of the fragmentation set
    :param annotation_id: id of the annotation where the vis data was created
    :return: render(request, 'frank/ms2lda_vis.html', context_dict)
    """
    context_dict = get_ms2lda_vis_context_dict(fragmentation_set_name_slug,annotation_id)
    return render(request, 'frank/ms2lda_vis.html', context_dict)

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
        elif annotation_tool.name == 'SIRIUS':
            annotation_query_form = SIRIUSQueryForm(request.POST, experiment_object=experiment)
        elif annotation_tool.name == 'NIST':
            annotation_query_form = NISTQueryForm(request.POST, experiment_object=experiment)
        elif annotation_tool.name == 'LCMS DDA Network Sampler':
            annotation_query_form = NetworkSamplerForm(request.POST)
        elif annotation_tool.name == 'Precursor Mass Filter':
            annotation_query_form = PrecursorMassFilterForm(fragmentation_set_name_slug,request.POST)
        elif annotation_tool.name == 'Clean Annotations':
            annotation_query_form = CleanFilterForm(fragmentation_set_name_slug,request.POST)
        elif annotation_tool.name == 'Network Sampler':
            annotation_query_form = NetworkSamplerForm(fragmentation_set_name_slug,request.POST)
       	elif annotation_tool.name == 'MS2LDA':
            annotation_query_form = MS2LDAQueryForm(request.POST)

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
            # Redirect the user to their 'fragmentation_set' page
            url = reverse('fragmentation_set', kwargs={'fragmentation_set_name_slug': fragmentation_set_name_slug})
            return HttpResponseRedirect(url)
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
        elif annotation_tool.name == 'SIRIUS':
            annotation_query_form = SIRIUSQueryForm(experiment_object=experiment)
        elif annotation_tool.name == 'NIST':
            annotation_query_form = NISTQueryForm(experiment_object=experiment)
        elif annotation_tool.name == 'LCMS DDA Network Sampler':
            annotation_query_form = NetworkSamplerForm()
        elif annotation_tool.name == 'Precursor Mass Filter':
            annotation_query_form = PrecursorMassFilterForm(fragmentation_set_name_slug)
        elif annotation_tool.name == 'Clean Annotations':
            annotation_query_form = CleanFilterForm(fragmentation_set_name_slug)
        elif annotation_tool.name == 'Network Sampler':
            annotation_query_form = NetworkSamplerForm(fragmentation_set_name_slug)
        elif annotation_tool.name == 'MS2LDA':
            annotation_query_form = MS2LDAQueryForm()

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

def input_peak_list_to_database(experiment_name_slug, fragmentation_set_id, ms1_peaks=None):
    taskSignature = input_peak_list_to_database_signature(experiment_name_slug, fragmentation_set_id, ms1_peaks)
    taskSignature.apply_async()

def input_peak_list_to_database_signature(experiment_name_slug, fragmentation_set_id, ms1_peaks=None):

    """
    Method to start the extraction of peaks from the uploaded mzML data files
    :param experiment_name_slug: A string containing the unique slug of an experiment
    :param fragmentation_set_id: Integer id of the fragmentation set
    :param ms1_peaks: Table of MS1 peaks
    ms1_peaks will be none if this method is called from Frank, and will have a dataframe from Pimp
    """
    logger.info("In the modified peak list signature method")
    retval = tasks.msn_generate_peak_list.si(experiment_name_slug, fragmentation_set_id, ms1_peaks)
    return retval

def generate_annotations(annotation_query_object,user = None):

    """
    Method to begin the retrieval of candidate annotations as a background task
    :param annotation_query_object: The Annotation Query to be performed
    """

    annotation_tool = annotation_query_object.annotation_tool
    if annotation_tool.name == 'MassBank':
        # If MassBank is to be queried, run the batch search as a background process
        tasks.massbank_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'SIRIUS':
        #If Sirius is to be queried, run the batch service as a background process
        tasks.sirius_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'NIST':
        print "as NIST annotation tool"
        # If NIST is to be queried, run the batch service as a background process
        tasks.nist_batch_search.delay(annotation_query_object.id)
    elif annotation_tool.name == 'Network Sampler':
        tasks.runNetworkSampler(annotation_query_object.id)
    elif annotation_tool.name == 'Precursor Mass Filter':
        tasks.precursor_mass_filter.delay(annotation_query_object.id)
    elif annotation_tool.name == 'Clean Annotations':
        tasks.clean_filter.delay(annotation_query_object.id,user)
    elif annotation_tool.name == 'MS2LDA':
        tasks.run_ms2lda_analysis(annotation_query_object.id)


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

    # Else, the annotation query could correspond to SIRIUS
    elif isinstance(annotation_query_form, SIRIUSQueryForm):
        # Populate the annotation tool into the query object
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='SIRIUS')

        """
        Parameters for SIRIUS are...
        max ppm - (selected by user). The allowed mass deviation of the fragment peaks in ppm. By default,
            Q-TOF instruments use 10 ppm and Orbitrap instruments use 5 ppm. #KmcL: add these defaults??

        number of hits - (selected by user).  The number of candidates in the output. By default, SIRIUS will
        only write the five best candidates.


        profile type - (selected by the user) The used analysis profile to be used. User chooses either **qtof**,
            **orbitrap** or **fticr**. By default, **qtof** is selected. #KMcL: check this default.

        output format -    Specify the format of the output of the fragmentation trees. This
            can be either json (machine readable) or dot (visualizable). #KmcL: Is this used?

        """
        # Determine the maximum number of hits the user wishes to be returned
        maximum_number_of_hits = annotation_query_form.cleaned_data['maximum_number_of_hits']
        max_ppm = annotation_query_form.cleaned_data['max_ppm']

        # Determine which profile type the user wishes to perform and the format of the output file.
        profile_type = str(annotation_query_form.cleaned_data['profile_type'])

        output_format =str(annotation_query_form.cleaned_data['output_format'])


        #Sirius specific parameters passed from the form
        parameters = {
            'max_hits': maximum_number_of_hits,
            'profile_type': profile_type,
            'max_ppm': max_ppm,
            'output_format': output_format,
        }

        # Pickle the parameters and add them to the annotation_query_object
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        print ('About to return annotation object with parameters')
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
        parameters['do_preferred'] = annotation_query_form.cleaned_data['do_preferred']
        parameters['collapse_multiple'] = annotation_query_form.cleaned_data['collapse_multiple']
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='Clean Annotations')
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    elif isinstance(annotation_query_form, NetworkSamplerForm):
        parameters = {}
        parameters['parents'] = annotation_query_form.cleaned_data['parent_annotation_queries']
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='Network Sampler')
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object
    # End of Simon contribution
    elif isinstance(annotation_query_form, MS2LDAQueryForm):
        parameters = {}
        parameters['minimal_ms1_intensity']     = annotation_query_form.cleaned_data['minimal_ms1_intensity']
        parameters['minimal_ms2_intensity']     = annotation_query_form.cleaned_data['minimal_ms2_intensity']
        parameters['min_ms1_retention_time']    = annotation_query_form.cleaned_data['min_ms1_retention_time']
        parameters['max_ms1_retention_time']    = annotation_query_form.cleaned_data['max_ms1_retention_time']
        parameters['grouping_tol']              = annotation_query_form.cleaned_data['grouping_tol']
        parameters['scaling_factor']            = annotation_query_form.cleaned_data['scaling_factor']
        parameters['polarity']                  = annotation_query_form.cleaned_data['polarity']
        parameters['alpha_model_parameter']     = annotation_query_form.cleaned_data['alpha_model_parameter']
        parameters['beta_model_parameter']      = annotation_query_form.cleaned_data['beta_model_parameter']
        parameters['gibbs_sampling_number']     = annotation_query_form.cleaned_data['gibbs_sampling_number']
        parameters['mass2motif_count'] = annotation_query_form.cleaned_data['mass2motif_count']
        annotation_query_object.annotation_tool = AnnotationTool.objects.get(name='MS2LDA')
        annotation_query_object.annotation_tool_params = jsonpickle.encode(parameters)
        return annotation_query_object

def delete_annotation_query(request,fragmentation_set_name_slug,annotation_query_slug):
    annotation_query = AnnotationQuery.objects.get(slug = annotation_query_slug)
    annotation_query.delete()
    return fragmentation_set(request,fragmentation_set_name_slug)

def remove_preferred_annotations(request,fragmentation_set_name_slug):
    # Removes all of the preferred annotations for a particular fragmentation set
    # Then returns to the fragmentation_set view
    # This should perhaps be a celery task?
    this_fragmentation_set = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    peaks = Peak.objects.filter(fragmentation_set = this_fragmentation_set,
                                preferred_candidate_annotation__isnull = False,
                                msn_level = 1)
    for peak in peaks:
        remove_preferred_annotation(peak)
        peak.save()
    return fragmentation_set(request,fragmentation_set_name_slug)

def remove_preferred_annotation(peak):
    peak.preferred_candidate_annotation = None
    peak.preferred_candidate_description = ""
    peak.preferred_candidate_user_selector = None
    peak.preferred_candidate_updated_date = None

def get_fragments_as_text(request,peak_name_slug,format_type):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(peak_name_slug)

    writer = csv.writer(response)

    # Get the peak
    peak = Peak.objects.get(slug=peak_name_slug)
    # Get the peak's children
    children = Peak.objects.filter(parent_peak=peak).order_by('mass')
    # Find most intense
    max_intensity = 0.0
    for fragment in children:
        if fragment.intensity > max_intensity:
            max_intensity = float(fragment.intensity)

    if format_type == 'list':
        for fragment in children:
            writer.writerow([fragment.mass,100.0*float(fragment.intensity)/max_intensity])
    elif format_type == 'mona':
        to_write = []
        writer = csv.writer(response,delimiter=' ')
        for fragment in children:
            to_write.append('{}:{}'.format(fragment.mass,100.0*float(fragment.intensity)/max_intensity))
        writer.writerow(to_write)

    return response

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


def connect(request,pimp_project_id,pimp_analysis_id):
    analysis = Analysis.objects.get(id = pimp_analysis_id)
    project= Project.objects.get(id = pimp_project_id)
    context_dict = {}
    context_dict['analysis'] = analysis
    context_dict['project'] = project
    fs = []
    frank_experiments = Experiment.objects.filter(created_by = request.user)
    for experiment in frank_experiments:
        fsets = experiment.fragmentationset_set.all()
        for f in fsets:
            fs.append(f)
    context_dict['fs'] = fs
    if len(fs)==0:
        fs = None


    if request.method=='POST':
        fs_form = SelectFragmentationSetForm(request.POST,current_user = request.user)
        if fs_form.is_valid():
            chosen_frag_set = fs_form.cleaned_data['fragmentation_sets']
            rt_tol = fs_form.cleaned_data['rt_tolerance']
            mass_tol = fs_form.cleaned_data['mass_tolerance']
            link = PimpAnalysisFrankFs.objects.get_or_create(pimp_analysis = analysis,frank_fs = chosen_frag_set,status='Processing')[0]
            tasks.simple_pimp_frank_linker.delay(pimp_analysis_id,chosen_frag_set.id,mass_tol,rt_tol,link.id)
        url = '/accounts/project/{}'.format(project.id)
        return redirect(url)

    else:
        fs_form = SelectFragmentationSetForm(current_user = request.user)
        context_dict['fs_form'] = fs_form
        print fs_form.fields
    return render(request,'frank/connect.html',context_dict)