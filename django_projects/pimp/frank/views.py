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


# Create your views here.

def index(request):
    return render(request, 'frank/index.html')

def sign_up(request):
    # is the user currently registered
    registered = False
    # if the request if a 'POST'
    if request.method == 'POST':
        # Obtain the sign in form from the POST request
        user_form = SignUpForm(data=request.POST)
        # is the form valid?
        if user_form.is_valid():
            # if so, commit the changes to the database
            user = user_form.save()
            # retrieve unencrypted copy of password for automatic login
            password = user.password
            user.set_password(user.password)
            user.save()
            username = user.username
            registered = True
            # The user is signed in automatically and returned to the index page
            player = authenticate(username=username, password=password)
            login(request, player)
            return HttpResponseRedirect(reverse('index'))
        else:
            # if the form is invalid, display the errors to the user
            print user_form.errors
    else:
        # if the request method is not a 'POST' create a new form
        user_form = SignUpForm()
    return render(request, 'frank/sign_up.html',
                  {'user_form': user_form, 'registered': registered})

# View for user sign in (login) page
def sign_in(request):
    # is the request a 'POST'?
    if request.method == 'POST':
        # retrieve the username and password from the POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # If the user exists and has not been disabled then they are logged in and sent to the index page
            if user.is_active:
                login(request, user)
                # redirect the user to the index page
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your account is currently disabled")
        else:
            # display that login details were invalid
            print "Invalid Login Details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid Login Details Supplied")

    else:
        return render(request, 'frank/sign_in.html')

# View to logout the user and return them to the index page
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def generate_experiment_list(currentUser):
    experimentList = Experiment.objects.filter(users = currentUser)
    return experimentList


def my_experiments(request):
    if request.user.is_authenticated():
        activeUser = request.user
        experimentList = generate_experiment_list(currentUser = activeUser)
        context_dict = {
            'experiment_list': experimentList
        }
        return render(request, 'frank/my_experiments.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def add_experiment(request):
    if request.user.is_authenticated():
        activeUser = request.user
        # if the request method is a POST
        if request.method == 'POST':
            # retrieve the form from the POST
            form = ExperimentForm(request.POST)
            # is the form valid?
            if form.is_valid():
                # commit the form to the database
                experiment = form.save(commit=False)
                experiment.createdBy = activeUser
                experiment.save()
                newUser = UserExperiments.objects.create(user = activeUser, experiment = experiment)
                experimentList = generate_experiment_list(currentUser = activeUser)
                context_dict = {
                    'experiment_list': experimentList
                }
                return render(request, 'frank/my_experiments.html', context_dict)
            else:
                # if the form is invalid, display the errors
                print form.errors
        else:
            # if not a POST request, then create a new game form
            form = ExperimentForm()
            # add the celebrities and the form to the context dictionary
            context_dict = {
                'experiment_form': form,
            }
        return render(request, 'frank/add_experiment.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def experimentSummary(request, experiment_name_slug):
    if request.user.is_authenticated():
        experiment = Experiment.objects.get(slug = experiment_name_slug)
        experimentalConditions = ExperimentalCondition.objects.filter(experiment = experiment)
        fragmentation_set_list = FragmentationSet.objects.filter(
                    experiment = experiment
                )
        context_dict = {'experiment': experiment,
                        'conditions': experimentalConditions,
                        'fragmentation_sets': fragmentation_set_list,
        }
        return render(request, 'frank/experiment.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def add_experimental_condition(request, experiment_name_slug):
    if request.user.is_authenticated():
        experiment = Experiment.objects.get(slug = experiment_name_slug)
        if request.method == 'POST':
            form = ExperimentalConditionForm(request.POST)
            if form.is_valid():
                condition = form.save(commit=False)
                condition.experiment = experiment
                condition.save()
                experimentalConditions = ExperimentalCondition.objects.filter(experiment = experiment)
                context_dict = {'experiment': experiment,
                                'conditions': experimentalConditions
                                }
                return render(request, 'frank/experiment.html', context_dict)
            else:
                print form.errors
        else:
            form = ExperimentalConditionForm()
            print form
            context_dict = {
                'experimental_condition_form': form,
                'experiment_name': experiment.title,
                'experiment_slug': experiment.slug,
            }
            return render(request, 'frank/add_experimental_condition.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')


def add_experiment(request):
    if request.user.is_authenticated():
        activeUser = request.user
        # if the request method is a POST
        if request.method == 'POST':
            # retrieve the form from the POST
            form = ExperimentForm(request.POST)
            # is the form valid?
            if form.is_valid():
                # commit the form to the database
                experiment = form.save(commit=False)
                experiment.createdBy = activeUser
                experiment.save()
                newUser = UserExperiments.objects.create(user = activeUser, experiment = experiment)
                experimentList = generate_experiment_list(currentUser = activeUser)
                context_dict = {
                    'experiment_list': experimentList
                }
                return render(request, 'frank/my_experiments.html', context_dict)
            else:
                # if the form is invalid, display the errors
                print form.errors
        else:
            # if not a POST request, then create a new game form
            form = ExperimentForm()
            # add the celebrities and the form to the context dictionary
            context_dict = {
                'experiment_form': form,
            }
        return render(request, 'frank/add_experiment.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def add_sample (request, experiment_name_slug, condition_name_slug):
    if request.user.is_authenticated():
        experiment = Experiment.objects.get(slug = experiment_name_slug)
        experimentalCondition = ExperimentalCondition.objects.get(slug = condition_name_slug)
        if request.method == 'POST':
            sampleForm = SampleForm(request.POST)
            if sampleForm.is_valid():
                sample = sampleForm.save(commit = False)
                sample.experimentalCondition = experimentalCondition
                sample.save()
                samples = Sample.objects.filter(experimentalCondition = experimentalCondition)
                context_dict = {'experiment': experiment,
                        'condition': experimentalCondition,
                        'samples': samples
                }
                return render(request, 'frank/condition.html', context_dict)
            else:
                print sampleForm.errors
                context_dict= {'experiment': experiment,
                            'condition': experimentalCondition,
                            'sample_form':sampleForm,

                }
                return render(request, 'frank/add_sample.html', context_dict)
        else:
            sampleForm = SampleForm()
            context_dict = {'experiment': experiment,
                            'condition': experimentalCondition,
                            'sample_form':sampleForm,

            }
            return render(request, 'frank/add_sample.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def conditionSummary(request, experiment_name_slug, condition_name_slug):
    if request.user.is_authenticated():
        experiment = Experiment.objects.get(slug = experiment_name_slug)
        experimentalCondition = ExperimentalCondition.objects.get(slug = condition_name_slug)
        samples = Sample.objects.filter(experimentalCondition = experimentalCondition)
        files = SampleFile.objects.filter(sample = samples)
        context_dict = {'experiment': experiment,
                        'condition': experimentalCondition,
                        'samples': samples,
                        'sample_files': files
        }
        return render(request, 'frank/condition.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def addSampleFile(request, experiment_name_slug, condition_name_slug, sample_slug):
    if request.user.is_authenticated():
        experiment = Experiment.objects.get(slug = experiment_name_slug)
        experimentalCondition = ExperimentalCondition.objects.get(slug = condition_name_slug)
        sample = Sample.objects.get(slug = sample_slug)
        if request.method == 'POST':
            sampleFileForm = SampleFileForm(request.POST, request.FILES)
            if sampleFileForm.is_valid():
                new_sample = sampleFileForm.save(commit=False)
                new_sample.sample = sample
                new_sample.name = new_sample.address.name
                new_sample.save()
                samples = Sample.objects.filter(experimentalCondition = experimentalCondition)
                files = SampleFile.objects.filter(sample = samples)
                context_dict = {'experiment': experiment,
                        'condition': experimentalCondition,
                        'samples': samples,
                        'sample_files': files
                }
                return render(request, 'frank/condition.html', context_dict)
            else:
                print sampleFileForm.errors
                context_dict = {
                'experiment': experiment,
                'condition': experimentalCondition,
                'sample': sample,
                'sampleFileForm': sampleFileForm,
            }
            return render(request, 'frank/add_sample_file.html', context_dict)
        else:
            sample_file_form = SampleFileForm()
            context_dict = {
                'experiment': experiment,
                'condition': experimentalCondition,
                'sample': sample,
                'sampleFileForm': sample_file_form,
            }
            return render(request, 'frank/add_sample_file.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def create_fragmentation_set(request, experiment_name_slug):
    if request.user.is_authenticated():
        experiment = Experiment.objects.get(slug = experiment_name_slug)
        if request.method == 'POST':
            fragment_set_from = FragmentationSetForm(request.POST)
            if fragment_set_from.is_valid():
                new_fragmentation_set = fragment_set_from.save(commit=False)
                new_fragmentation_set.experiment = experiment
                new_fragmentation_set.save()
                input_peak_list_to_database(experiment_name_slug, new_fragmentation_set.id)
                experimentalConditions = ExperimentalCondition.objects.filter(experiment = experiment)
                fragmentation_set_list = FragmentationSet.objects.filter(
                    experiment = experiment
                )
                context_dict = {'experiment': experiment,
                                'conditions': experimentalConditions,
                                'fragmentation_sets': fragmentation_set_list,
                                }
                return render(request, 'frank/experiment.html', context_dict)
            else:
                print fragment_set_from.errors()
        else:
            fragment_set_from = FragmentationSetForm()
            context_dict = {
                'frag_set_form': fragment_set_from,
                'experiment': experiment
            }
            return render(request, 'frank/create_fragmentation_set.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')


def input_peak_list_to_database(experiment_name_slug, analysis_id):
    ## Remember to add the msnAnalysis method onto celery
    experiment = Experiment.objects.get(slug = experiment_name_slug)
    experiment_type = experiment.detectionMethod
    if experiment_type == 'LCMS DDA':
        tasks.msnGeneratePeakList.delay(experiment_name_slug, analysis_id)
    #msnAnalysis(experiment_name_slug)

def fragmentation_set_summary(request):
    if request.user.is_authenticated():
        current_user = request.user
        fragmentation_set_list = []
        user_experiment_list = Experiment.objects.filter(users=current_user)
        for experiment in user_experiment_list:
            experiment_fragment_sets = FragmentationSet.objects.filter(experiment=experiment)
            fragmentation_set_list.extend(experiment_fragment_sets)
        context_dict = {'fragmentation_sets': fragmentation_set_list,}
        return render(request, 'frank/my_fragmentation_sets.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')

def fragmentation_set(request, fragmentation_set_name_slug):
    if request.user.is_authenticated():
        fragment_set = FragmentationSet.objects.get(slug=fragmentation_set_name_slug)
        ## Display number of msn peaks
        list_of_peaks = Peak.objects.filter(fragmentation_set = fragment_set, msnLevel=1)
        number_of_peaks = len(list_of_peaks)
        annotation_queries = AnnotationQuery.objects.filter(fragmentation_set = fragment_set)
        sample_file_ids = list_of_peaks.values("sourceFile").distinct()
        ms1_peaks_by_file = {}
        for file_id in sample_file_ids:
            experimental_file = SampleFile.objects.get(id=file_id.get('sourceFile'))
            ms1_peaks_by_file[experimental_file] = list_of_peaks.filter(sourceFile = experimental_file).order_by('mass')
        context_dict = {
            'fragment_set': fragment_set,
            'peak_list': list_of_peaks,
            'number_of_peaks':number_of_peaks,
            'annotations': annotation_queries,
            'peaks_by_file': ms1_peaks_by_file,
        }
        return render(request, 'frank/fragmentation_set.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')


def peak_summary(request, fragmentation_set_name_slug, peak_name_slug):
    if request.user.is_authenticated():
        fragmentation_set = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
        peak = Peak.objects.get(slug=peak_name_slug, fragmentation_set = fragmentation_set)
        ## Display number of msn peaks
        list_of_peaks = Peak.objects.filter(parentPeak = peak)
        list_of_candidate_annotations = CandidateAnnotation.objects.filter(peak=peak)
        list_of_candidate_annotations = list_of_candidate_annotations.order_by('annotation_query','-confidence')
        number_of_fragments = len(list_of_peaks)
        context_dict = {
            'peak': peak,
            'fragmentation_peak_list': list_of_peaks,
            'number_of_fragments':number_of_fragments,
            'candidate_annotations': list_of_candidate_annotations,
        }
        return render(request, 'frank/peak_summary.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')


def define_annotation_query(request, fragmentation_set_name_slug):
    if request.user.is_authenticated():
        fragmentation_set = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
        if request.method == 'POST':
            annotation_query_form = AnnotationQueryForm(request.POST)
            if annotation_query_form.is_valid():
                new_annotation_query = annotation_query_form.save(commit=False)
                new_annotation_query.fragmentation_set = fragmentation_set
                new_annotation_query.save()
                generate_annotations(fragmentation_set, new_annotation_query)
                list_of_peaks = Peak.objects.filter(fragmentation_set = fragmentation_set, msnLevel=1)
                number_of_peaks = len(list_of_peaks)
                annotation_queries = AnnotationQuery.objects.filter(fragmentation_set = fragmentation_set)
                context_dict = {
                    'fragment_set': fragmentation_set,
                    'peak_list': list_of_peaks,
                    'number_of_peaks':number_of_peaks,
                    'annotations': annotation_queries,
                }
                return render(request, 'frank/fragmentation_set.html', context_dict)
            else:
                print annotation_query_form.errors()
        else:
            annotation_query_form = AnnotationQueryForm()
            context_dict = {
                'annotation_query_form': annotation_query_form,
                'fragmentation_set': fragmentation_set,
            }
            return render(request, 'frank/define_annotation_query.html', context_dict)
    else:
        return render(request, 'frank/sign_in.html')


def generate_annotations(fragmentation_set, annotation_query):
    if annotation_query.massBank == True:
        tasks.massBank_batch_search.delay(fragmentation_set.id, annotation_query.id)

def make_ms1_plot(request, fragmentation_set_name_slug, file_id):
    sample_file_object = SampleFile.objects.get(id = file_id)
    fragmentation_set_object = FragmentationSet.objects.get(slug = fragmentation_set_name_slug)
    file_peak_list = Peak.objects.filter(fragmentation_set = fragmentation_set_object, sourceFile = sample_file_object)

    peak_masses = []
    peak_intensities = []
    for peak in file_peak_list:
        peak_masses.append(peak.mass)
        peak_intensities.append(peak.intensity)

    # define some colours
    parent_fontspec = {
        'size':'10',
        'color':'blue',
        'weight':'bold'
    }

    # make blank figure
    figsize=(10, 6)
    fig = plt.figure(figsize=figsize, facecolor='white')
    ax = fig.add_subplot(1,1,1)

    # plot all the fragment peaks of this parent peak
    num_peaks = len(peak_masses)
    for j in range(num_peaks):
        mass = peak_masses[j]
        intensity = peak_intensities[j]
        plt.plot((mass, mass), (0, intensity), linewidth=1.0, color='#FF9933')

    # Determine the most intense and largest mass in peak query set
    highest_intensity = file_peak_list.aggregate(Max('intensity'))['intensity__max']
    highest_mass = file_peak_list.aggregate(Max('mass'))['mass__max']

    # set range of x- and y-axes
    xlim_upper = int(round(highest_mass*Decimal(1.1)))
    ylim_upper = int(round(highest_intensity*Decimal(1.1)))
    plt.xlim([0, xlim_upper])
    plt.ylim([0, ylim_upper])

    # show the axes info
    plt.xlabel('m/z')
    plt.ylabel('relative intensity')
    title = 'MS1 Spectra for '+sample_file_object.name
    plt.title(title)

    # add legend
    yellow_patch = mpatches.Patch(color='#FF9933', label='MS1 peaks')
    plt.legend(handles=[yellow_patch])

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

def make_spectra_plot(request, fragmentation_set_name_slug, peak_name_slug):
    parent_object = Peak.objects.get(slug = peak_name_slug)
    fragmentation_spectra = Peak.objects.filter(parentPeak = parent_object)

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

    # ###### DEFAULT INTENSITIES #######
    # # make blank figure
    # figsize=(10, 6)
    # fig = plt.figure(figsize=figsize, facecolor='white')
    # ax = fig.add_subplot(111)
    #
    # # plot the parent peak first
    # plt.plot((parent_mass, parent_mass), (0, parent_intensity), linewidth=2.0, color='b')
    # x = parent_mass
    # y = parent_intensity
    # label = "%.5f" % parent_mass
    # plt.text(x, y, label, **parent_fontspec)
    #
    # # plot all the fragment peaks of this parent peak
    # num_peaks = len(fragment_masses)
    # for j in range(num_peaks):
    #     mass = fragment_masses[j]
    #     intensity = fragment_intensities[j]
    #     plt.plot((mass, mass), (0, intensity), linewidth=1.0, color='#FF9933')
    #
    # # set range of x- and y-axes
    # xlim_upper = int(parent_mass + 50)
    # ylim_upper = int(round(parent_intensity*Decimal(1.25)))
    # plt.xlim([0, xlim_upper])
    # plt.ylim([0, ylim_upper])

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
    rt_value = ("%.3f" % parent_object.retentionTime)
    title = 'MS1 m/z=' + mz_value + ' RT=' + rt_value
    plt.title(title)

    # add legend
    blue_patch = mpatches.Patch(color='blue', label='Parent peak')
    yellow_patch = mpatches.Patch(color='#FF9933', label='Fragment peaks')
    plt.legend(handles=[blue_patch, yellow_patch])

    # change plot tick paramaters
    # plt.tick_params(
    #     axis = 'both',
    #     which = 'both',
    #     bottom = 'off',
    #     top = 'off',
    #     left = 'off',
    #     right = 'off',
    # )

    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

