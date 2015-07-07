from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from frank.models import *
from frank.forms import *
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from frank.MSNAnalysis import *

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
        context_dict = {'experiment': experiment,
                        'conditions': experimentalConditions
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
        print files
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


def analyse (request, experiment_name_slug):
    ## Remember to add the msnAnalysis method onto celery
    msnAnalysis(experiment_name_slug)
    return HttpResponse('Python Script Called')
