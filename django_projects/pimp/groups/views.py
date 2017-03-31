from django.shortcuts import render_to_response
from django.shortcuts import render
from projects.models import Project
from groups.models import Attribute
from data.models import Dataset
from django.core.context_processors import csrf
from django.template import RequestContext # For CSRF
from django.forms.formsets import formset_factory, BaseFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
try:
	from django.utils import simplejson
except:
	import json as simplejson

# Pygal import for SVG file creation
# import pygal
# from pygal.style import CleanStyle
# from pygal import Config

# Rpy2 import for TIC creation
from rpy2.robjects.packages import importr

from groups.forms import *
from experiments.models import Analysis

import datetime

import os
import logging

# import PiMP settings
from django.conf import settings



logger = logging.getLogger(__name__)


def assignfile(request, project_id):
    if request.method == 'POST':
        print "curieux!!"
        return render(request, 'project/detail.html', {'project': project, 'permission':permission,})

    else :
        print "we are in asign file Yeah"
        try:
            project = Project.objects.get(pk=project_id)
            user = request.user
            permission = project.userproject_set.get(user=user).permission
            attribute_formset = request.session['attribute_formset']
            group_form = request.session['group_form']
        except Project.DoesNotExist:
            raise Http404
        c = {'group_form': group_form,
         'attribute_formset': attribute_formset,
         'project': project,
         'permission':permission,
        }
    print "group_form : ", group_form
    #c.update(csrf(request))
    return render(request, 'project/assignfile.html', c) 


# Deprecated function - to be removed? 
def getFilesFromMember(member):
    posFileList = []
    negFileList = []
    for sample in member.sample.all():
        if sample.samplefile.posdata:
            posFileList.append(sample.samplefile.posdata)
        if sample.samplefile.negdata:
            negFileList.append(sample.samplefile.negdata)
    return [posFileList,negFileList]


def createTicPlot(fileList, attribute, polarity, project):
    xcms = importr("xcms")
    mzxmlFileList = [file.file for file in fileList]
    intensityList = []
    timeList = []
    print "mzxmlFileList : ", mzxmlFileList[0]
    for i in range(len(mzxmlFileList)):
        print "mzxmlfile :",mzxmlFileList[i]
        file = xcms.xcmsRaw(mzxmlFileList[i].path)
        print "file opened"
        intensity = [int(i) for i in list(file.do_slot("tic"))]
        time = [str(i) for i in list(file.do_slot("scantime"))]
        timeList.append(time)
        intensityList.append(intensity)
        print "++++++++++++++++++++++++++++++++++++++++++++++"

    f = int(len(timeList[0])/4)

    config = pygal.Config(width=1600, height=1200, human_readable=True, show_dots=False, style=CleanStyle, x_labels_major_every=f,show_minor_x_labels=False, js = [
    '/Users/yoanngloaguen/Documents/ideomWebSite/static/js/svg.jquery.js',
    '/Users/yoanngloaguen/Documents/ideomWebSite/static/js/pygal-tooltips.js',
    #'./static/js/SVGPan.js',
    ])
    chart = pygal.Line(config)
    chart.add( 'All', [])

    print "chart created"
    chart.x_labels = timeList[0]
    for i in range (len(mzxmlFileList)):
        print "the file name is : ",mzxmlFileList[i].name
        filename = mzxmlFileList[i].name.split('/')[1:][len(mzxmlFileList[i].name.split('/')[1:])-1]
        name = filename.split('.')[:1][0]
        chart.add(name, intensityList[i])

    print "MEDIA_URL : ",settings.MEDIA_URL
    directory = os.path.join(settings.MEDIA_ROOT, 'projects/', str(project.id), 'TIC/', str(attribute.group.id), str(attribute.id), polarity)
    if not os.path.exists(directory):
        os.makedirs(directory)
    chart.render_to_file(os.path.join(directory, 'tic.svg'))
    filePath = os.path.join(settings.MEDIA_URL, 'projects/', str(project.id), 'TIC/', str(attribute.group.id), str(attribute.id), polarity, 'tic.svg')
    print "rendered!!!"
    print "filePath : ",filePath
    return filePath


# Deprecated function - to be removed? 
def createTic(fileList, attribute, polarity, project):
    if not attribute.ticgroup:
        print "+++++++++++++???????????????????????????+++++++++++++++++++++"
        print "######################  NO TIC GROUP  #############################3"
        ticgroup = TicGroup.objects.create()
        ticgroup.save()
        attribute.ticgroup = ticgroup
        attribute.save()
    else:
        ticgroup = attribute.ticgroup
    if polarity == "POS":
        if not ticgroup.postic:
            postic = TicFile.objects.create()
            postic.save()
            ticgroup.postic = postic
            ticgroup.save()
        else:
            postic = ticgroup.postic
        postic.ticplot = createTicPlot(fileList, attribute, polarity, project)
        postic.save()
    else:
        if not ticgroup.negtic:
            negtic = TicFile.objects.create()
            negtic.save()
            ticgroup.negtic = negtic
            ticgroup.save()
        else:
            negtic = ticgroup.negtic
        negtic.ticplot = createTicPlot(fileList, attribute, polarity, project)
        negtic.save()


def index(request, project_id):
    """
    Create empty forms for group creation and return to a GET request.
    Validate form data for group creation, save the data into the database, return user to project detail.

    """
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    AttributeFormSet = formset_factory(AttributeForm, extra=0, max_num=20, formset=RequiredFormSet)

    SampleAttributeFormSet = formset_factory(SampleAttributeForm, extra=0, formset=RequiredFormSet)

    try:
        project = Project.objects.get(pk=project_id)
        user = request.user
        permission = project.userproject_set.get(user=user).permission
    except Project.DoesNotExist:
        raise Http404  # Http404 not imported, so this except does nothing...

    error_message = False

    if request.method == 'POST':
        print user.username + ' submitted a group creation form. Processing...'
        group_form = GroupForm(request.POST)
        attribute_formset = AttributeFormSet(request.POST, prefix='attributes')
        sample_attribute_formset = SampleAttributeFormSet(request.POST, prefix='samplesattributes')

        if attribute_formset.is_valid() and sample_attribute_formset.is_valid() and group_form.is_valid():

            # This series of if statements is used to check if the user tried to create
            # attributes without assigning samples to them, or tried to create a group
            # without adding any attributes.
            # Any attribute without samples is not saved to the database.
            # A group without attributes is not saved to the database.

            project.modified = datetime.datetime.now()

            group = group_form.save(commit=False)
            group_saved = False

            for attribute_form in attribute_formset.forms: # for each attribute
                attribute_object = attribute_form.save(commit=False)
                attribute_saved = False
                attribute_name = attribute_form.cleaned_data['name']
                print '\tChecking if attribute ' + attribute_name + ' has been assigned any samples...'

                for sample_attribute_form in sample_attribute_formset.forms: # for each sample
                    sample_attribute = sample_attribute_form.cleaned_data['attribute']

                    if sample_attribute == attribute_name: # if there is a sample assigned to the attribute, save it
                        print '\tA sample has been assigned to attribute ' + attribute_name

                        if not group_saved:  # ensure the group is only saved once
                            print '\tSaving group ' + group_form.cleaned_data['name']
                            group.save()
                            group_saved = True

                        if not attribute_saved:  # ensure the attribute is only saved once
                            print '\tSaving attribute ' + attribute_name
                            attribute_object.group = group
                            attribute_object.save()
                            attribute_saved = True

                        sample_id = sample_attribute_form.cleaned_data['sample']
                        print '\tSample ' + sample_id + ' has been added to ' + attribute_name + '\n'
                        sample = project.sample_set.get(id=sample_id)
                        attribute = group.attribute_set.get(name=attribute_name)
                        SampleAttribute.objects.create(sample=sample, attribute=attribute)

            project.save()
            print "Group creation processing finished."

            return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))

        else:  # at least one form isn't valid
            print "At least one form in the group creation view wasn't valid."
            error_message = True # Used on the template to display a general error message.
            logger.warning("attribute_formset errors: %s", attribute_formset.errors)
            logger.warning("sample_attribute_formset errors: %s", sample_attribute_formset.errors)
            logger.warning("group_form errors: %s", group_form.errors)
            group_form = GroupForm()
            attribute_formset = AttributeFormSet(prefix='attributes')
            sample_attribute_formset = SampleAttributeFormSet(prefix='samplesattributes')

    else:  # if the request method is GET
        group_form = GroupForm()
        attribute_formset = AttributeFormSet(prefix='attributes')
        sample_attribute_formset = SampleAttributeFormSet(prefix='samplesattributes')

    c = {
        'group_form': group_form,
        'attribute_formset': attribute_formset,
        'sample_attribute_formset': sample_attribute_formset,
        'project': project,
        'permission': permission,
        'error_message': error_message
    }

    return render(request, 'project/groupcreation_bs3.html', c)


def create_calibration_groups(request, project_id):
    """
    A view to provide forms for assigning calibration samples to their groups (blank, QC, standard),
    or submit the completed forms to the database with validation.
    Even if no samples have been assigned to a calibration group (for example, no blanks provided),
    an attribute will be created. In the same way, if no samples are added to any calibration group
    and this view is run with request.method == 'POST', a new calibration_group group and attributes
    for the calibration groups will be created.

    """

    try:
        project = Project.objects.get(pk=project_id)
        user = request.user
        permission = project.userproject_set.get(user=user).permission
    except Project.DoesNotExist:
        raise Http404  # Http404 not imported, so this except does nothing...

        # Get the list of samples already assigned to a calibration group to set the total number of forms (extra)
    assigned_calibration_samples = project.calibrationsample_set.all().filter(attribute__isnull=False)

    # Create formset for calibration groups, the number of calibration groups is always 3 (extra=3)
    AttributeFormSet = formset_factory(AttributeForm, extra=3, max_num=3)
    # Create formset for sample-calibration group association with the correct number of existing association (extra=existing_number_of_association)
    # This is used to set the "TOTAL" number of entries to the right number in the template  
    SampleAttributeFormSet = formset_factory(ProjfileAttributeForm, extra=assigned_calibration_samples.count())

    # Get all calibration samples
    calibration_samples = project.calibrationsample_set.all()
        # Get all samples not already assigned to a calibration group
    unassigned_calibration_samples = project.calibrationsample_set.all().filter(attribute__isnull=True)
    # Get the existing calibration groups
    attribute_list = Attribute.objects.filter(calibrationsample=calibration_samples).distinct()

    # Create a dictonnary with calibration group - sample association information {group1: [sample1, sample2], group2: [sample3, sample4], ...}
    attribute_sample_association = {}
    for attribute in attribute_list:
        assigned_samples = project.calibrationsample_set.all().filter(attribute=attribute)
        attribute_sample_association[attribute.name] = assigned_samples

    dataset = Dataset.objects.filter(analysis__experiment__comparison__attribute__calibrationsample_in=assigned_calibration_samples).distinct()
    error_message = False

    if request.method == "POST":

            # print user.username + ' submitted a calibration group creation form. Processing...'

            attribute_formset = AttributeFormSet(request.POST, prefix='attributes')
            sample_attribute_formset = SampleAttributeFormSet(request.POST, prefix='samplesattributes')

            if attribute_formset.is_valid() and sample_attribute_formset.is_valid():

                # Delete existing datasets
                for ds in dataset:
                    analysis = ds.analysis
                    analysis.status = 'Ready'
                    analysis.save()
                    ds.delete()

                # Create a calibration group for the user if one doesn't exist
                group_exists = False
                for f in calibration_samples:
                    for attribute in f.attribute_set.all():
                        if attribute.group:
                            group = attribute.group
                            group_exists = True
                            break

                if not group_exists:
                    # print "\tCreating new calibration group"
                    group = Group.objects.create(name="calibration_group")
                # else:
                    # print "\tA calibration group already exists, so a new one wasn't created"

                # Delete all attribute if any exist
                attribute_list.delete()

                empty_group = True
                # print "\tProcessing attributes"
                for attribute_form in attribute_formset:

                    # Save the attribute if it doesn't exist
                    attribute_object, created = Attribute.objects.get_or_create(name=attribute_form.cleaned_data['name'], group=group)
                    if created:
                        # print "\t\tA new attribute " + attribute_form.cleaned_data['name'] + " was created."
                        attribute_object.save()
                    # else:
                        # print "\t\tThe attribute " + attribute_form.cleaned_data['name'] + \
                        #       " in this group already existed, so a new one wasn't created."

                    # print "\t\tProcessing sample attributes"
                    empty_attibute = True
                    for sample_attribute_form in sample_attribute_formset:

                        attribute = sample_attribute_form.cleaned_data['attribute']

                        if attribute == attribute_object.name:
                            empty_attibute = False
                            empty_group = False
                            sample_id = sample_attribute_form.cleaned_data['projfile']
                            sample_object = project.calibrationsample_set.get(id=sample_id)
                            _, created = ProjfileAttribute.objects.get_or_create(attribute=attribute_object, calibrationsample=sample_object)
                            # if created:
                            #     print "\t\t\tNew projfile attribute created for sample " + sample_id
                            # else:
                            #     print "\t\t\tThe projfile attribute already existed for sample " + sample_id + \
                            #           " and attribute " + attribute
                    # print "\t\tFinished processing sample attributes."

                    # If an attribute is created but no sample have been assigned to it, delete it
                    if empty_attibute:
                        attribute_object.delete()

                if empty_group:
                    group.delete()
                # print "\tFinished processing attributes"

                project.modified = datetime.datetime.now()
                project.save()
                # print "Finished adding calibration groups."

                return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))

            else:
                error_message = True
                # print "A form from the calibration group creation and sample assigment was invalid - user redirected" \
                #       "to project detail page."

                attribute_formset = AttributeFormSet(prefix='attributes', initial=[
                    {'name': 'qc'},
                    {'name': 'blank'},
                    {'name': 'standard'}
                ])

                sample_attribute_formset = SampleAttributeFormSet(prefix='samplesattributes')

                # attribute_formset = attribute_formset

                c = {
                    'error_message': error_message,
                    'sample_attribute_formset': sample_attribute_formset,
                    'attribute_formset': attribute_formset,
                    'project': project,
                    'permission': permission
                }

                return render(request, 'project/create_calibration_groups.html', c)

    else:  # if the request method is GET

        # Formset with the initial groups
        attribute_formset = AttributeFormSet(prefix='attributes', initial=[
            {'name': 'qc'},
            {'name': 'blank'},
            {'name': 'standard'}
        ])

        # Create calibration group-sample association formset - resulting form will be used as a template and is handled by javascript
        sample_attribute_formset = SampleAttributeFormSet(prefix='samplesattributes')

        # I don't know what this is, should probably remove it
        attribute_formset = attribute_formset

        # Create context dictonnary to be passed to the template
        c = {
            'error_message': error_message,
            'sample_attribute_formset': sample_attribute_formset,
            'attribute_formset': attribute_formset,
            'project': project,
            'permission': permission,
            'unassigned_calibration_samples': unassigned_calibration_samples,
            'assigned_calibration_samples': assigned_calibration_samples,
            'attribute_sample_association': attribute_sample_association,
            'dataset_exist': [dataset.exists(), dataset.count()]

        }

        return render(request, 'project/create_calibration_groups.html', c)


# Deprecated function - to be removed?
def indexRate(request, project_id):
    # This class is used to make empty formset forms required
    # See http://stackoverflow.com/questions/2406537/django-formsets-make-first-required/4951032#4951032
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    AttributeFormSet = formset_factory(AttributeForm, extra=2, max_num=10, formset=RequiredFormSet)

    try:
        project = Project.objects.get(pk=project_id)
        user = request.user
        permission = project.userproject_set.get(user=user).permission
    except Project.DoesNotExist:
        raise Http404

    if request.method == 'POST': # If the form has been submitted...
        group_form = GroupForm(request.POST) # A form bound to the POST data
        # Create a formset from the submitted data
        print "we are in the post request view"
        attribute_formset = AttributeFormSet(request.POST, request.FILES)
        
        if group_form.is_valid() and attribute_formset.is_valid():
            #request.session['group_form'] = group_form
            #formlist = []
            #for form in attribute_formset.forms:
            #    formlist.append(form)
            #request.session['attribute_formset'] = formlist
            print "la liste marche, wouhouou"
            return HttpResponseRedirect(reverse('groups.views.assignfile', args=(project.id,)))
            #return redirect('assignfile', {'group_form': group_form, 'attribute_formset': attribute_formset, 'project': project}) 
            #group = group_form.save()
            #for form in attribute_formset.forms:
            #    attribute = form.save(commit=False)
            #    attribute.group = group
            #    attribute.save()
            #return render(request, 'project/detail.html', {'project': project, 'permission':permission,})
            #return HttpResponseRedirect('thanks') # Redirect to a 'success' page
    else:
        print "we are in the get request view"
        group_form = GroupForm()
        attribute_formset = AttributeFormSet()
    
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 

    c = {'group_form': group_form,
         'attribute_formset': attribute_formset,
         'project': project,
         'permission':permission,
        }
    c.update(csrf(request))
    return render(request, 'project/groupcreation.html', c)
    #return render_to_response('project/groupcreation.html', c)
