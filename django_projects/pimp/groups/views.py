from django.shortcuts import render_to_response
from django.shortcuts import render
from projects.models import Project
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

import datetime

import os

# import PiMP settings
from django.conf import settings


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


# Create categories for project files (QC, Blank, standatds.csv)
def createAttribute(request, project_id):

    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    AttributeFormSet = formset_factory(AttributeForm, extra=3, max_num=3, formset=RequiredFormSet)


    SampleAttributeFormSet = formset_factory(ProjfileAttributeForm, extra=1, formset=RequiredFormSet)



    try:
        project = Project.objects.get(pk=project_id)
        user = request.user
        permission = project.userproject_set.get(user=user).permission
    except Project.DoesNotExist:
        raise Http404

    groupExist = False
    calibrationsamples = project.calibrationsample_set.all()
    for f in calibrationsamples :
        for att in f.attribute_set.all() :
            if att.group :
                group = att.group
                groupExist = True
                print "group exist!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                break

    if not groupExist:
        group = Group.objects.create(name="calibration_group")
        group.save()
        print "group does not exist, just created!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

    if request.method == 'POST':
        attribute_formset = AttributeFormSet(request.POST, request.FILES, prefix='attributes')
        #print attribute_formset
        print " "
        sample_attribute_formset = SampleAttributeFormSet(request.POST, request.FILES, prefix='samplesattributes')

        if attribute_formset.is_valid():# and sample_attribute_formset.is_valid():
            project.modified = datetime.datetime.now()
            project.save()
            if not groupExist:
                for form in attribute_formset.forms:
                #    if form.cleaned_data['name'] not in attributeList:
                    print "AHHHHHHHHHHHHHH"
                    print form
                    print form.cleaned_data['name']



                    attribute = form.save(commit=False)
                    attribute.group = group
                    attribute.save()

                    #print attribute.created
                    print "attribute saved"
                    #print attribute
                    #attribute.save()
            attributeList = []
            for f in calibrationsamples :
                f.attribute_set.clear()
            #     print f
            #     for att in f.attribute_set.all() :
            #         if att not in attributeList :
            #             attributeList.append(att)
            # print "attributeList : ",attributeList
            # for att in attributeList:
            #     for file_att in att.projfile.all():
            #         print file_att
            #         att.projfile.remove(file_att)
            for form in sample_attribute_formset.forms:
                print "line 1"
                print form
                sampleId = form.cleaned_data['projfile']
                print "line 2"
                attributeName = form.cleaned_data['attribute']
                print "line 3"
                sample = project.calibrationsample_set.get(id=sampleId)
                print "sample found"
                print group.attribute_set.all()
                attribute = group.attribute_set.get(name=attributeName)
                print "attribute found"
                new_sample_attribute = ProjfileAttribute.objects.create(calibrationsample=sample, attribute=attribute)
                print "new_sample attribute created"


            if request.is_ajax():
                #return render(request, 'project/detail.html', {'project': project, 'permission':permission})
                print "here"
                # return "prout"
                # if 'new_project' in request.session and request.session['new_project']:
                #     request.session['calibration'] = True
                #     message = "new_project"
        
                # else:
                #     message = "none"
                    # return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))
                message = "success"
                response = simplejson.dumps(message)
                return HttpResponse(response, content_type='application/json')

            #for form in sample_attribute_formset.forms:
            #    print "line 1"
            #    sampleId = form.cleaned_data['sample']
            #    print "line 2"
            #    attributeName = form.cleaned_data['attribute']
            #    print "line 3"
            #    sample = project.projFile_set.get(id=sampleId)
            #    print "sample found"
            #    #print group.attribute_set.all()
            #    attribute = project.attribute_set.get(name=attributeName)
            #    print "attribute found"
            #    #new_sample_attribute = ProjfileAttribute.objects.create(sample=sample, attribute=attribute)
            #    print "new_sample attribute created"
        else:
            print "prout"

    
    else:
        print "we are in the get request view"
        attribute_formset = AttributeFormSet(prefix='attributes')
        sample_attribute_formset = SampleAttributeFormSet(prefix='samplesattributes')
    
    # For CSRF protection
    # See http://docs.djangoproject.com/en/dev/ref/contrib/csrf/ 
    attributes = []
    for sample in project.calibrationsample_set.all():
        if sample.attribute_set.all():
            attributeSet = set(attributes).union(set(sample.attribute_set.all()))
            attributes = list(attributeSet)


    c = {'attributes': attributes,
         'attribute_formset': attribute_formset,
         'sample_attribute_formset': sample_attribute_formset,
         'project': project,
         'permission':permission,
        }
    c.update(csrf(request))
    # print request.session['new_project']
    # return render_to_response('project/attributecreation.html', c, context_instance = RequestContext(request))
    return render(request, 'project/attributecreation.html', c)

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
