# import PiMP specific models and form
from fileupload.models import Picture, ProjFile, SampleFileGroup, Sample, StandardFileGroup, CalibrationSample
from fileupload.forms import FileForm
from projects.models import Project

# import django generic library
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
try:
	from django.utils import simplejson
except:
	import json as simplejson
from django.core.urlresolvers import reverse

# import os specific info
import datetime

# import python extra library (PiMP specific)
from lxml import etree
import lxml.sax
from xml.sax.handler import ContentHandler

# import PiMP settings
from django.conf import settings

def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"

class MyContentHandler(ContentHandler):
    def __init__(self):
        self.scan_amount = 0
        self.polarity = None
    def startElementNS(self, name, qname, attributes):
        uri, localname = name       
        if localname == 'scan':
            self.scan_amount += 1
            if self.scan_amount == 1 :
                attrs = {} 
                try: 
                    iter_attributes = attributes.iteritems() 
                except AttributeError: 
                    iter_attributes = attributes.items() 
                for name_tuple, value in iter_attributes:
                    if name_tuple[1] == 'polarity':
                      self.polarity = value
        elif localname == 'cvParam':
            self.scan_amount += 1
            if self.scan_amount <= 2 :
                attrs = {} 
                try: 
                    iter_attributes = attributes.iteritems() 
                except AttributeError: 
                    iter_attributes = attributes.items() 
                for name_tuple, value in iter_attributes:
                    if name_tuple[1] == 'value' and str(value) == 'Positive':
                        self.polarity = "+"
                    elif name_tuple[1] == 'value' and str(value) == 'Negative':
                        self.polarity = "-"

class PictureCreateView(CreateView):
    model = Picture
    #fields = ('file','slug','project')
    form = FileForm

    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        return super(PictureCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(PictureCreateView, self).get_context_data(
            *args, **kwargs)
        print "context_data: ",context_data
        print "session_data: ",self.request.session
        print "user: ",self.request.user

        user = self.request.user

        # Add for space limitation - the following code is used to calculate how much space is left to restrict the upload size
        owned_projects = Project.objects.filter(user_owner=user)
        calibration_samples = ProjFile.objects.filter(project__in=owned_projects).order_by('project__id')
        samples = Picture.objects.filter(project__in=owned_projects).order_by('project__id')

        storage_taken = {'samples': 0, 'calibration_samples': 0}


        for calibration_sample in calibration_samples:
            storage_taken['calibration_samples'] += calibration_sample.file.size
        for sample in samples:
            storage_taken['samples'] += sample.file.size

        total_storage = 53687091200

        storage_used = storage_taken['calibration_samples'] + storage_taken['samples']
        storage_remaining = int(float(total_storage) - storage_used)

        print "storage_used: ",storage_used
        print "storage_remaining: ",storage_remaining

        # if 'new_project' in self.request.session and self.request.session['new_project']:
        #     print "my session : ",self.request.session['new_project']
        #     new_project = self.request.session['new_project']
        # else:
        #     new_project = False
        # if 'calibration' in self.request.session and self.request.session['calibration']:
        #     calibration = self.request.session['calibration']
        # else:
        #     calibration = False
        context_data.update({'project': self.project, 'storage_remaining': storage_remaining}) #,'new_project': new_project, 'calibration': calibration})
        # context_data.['pictures'] = Picture.objects.all()
        return context_data
    
    def findpolarity(self, file):
        tree = etree.parse(file)
        handler = MyContentHandler()
        lxml.sax.saxify(tree, handler)
        return handler.polarity        

    def form_valid(self, form):
        #print "form is valid, go to the next step!"
        #print form
        #print "le project est : ",self.project.id
        #my_value = self.project
        #file = form.cleaned_data['file']
        #slug = form.cleaned_data['slug']

        #print "FILEEEEEE : ",file
        #print "form project 1 : ",form.cleaned_data['project']
        
        #Attention !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!Project.objects.create(
        samples = [sample.name for sample in self.project.sample_set.all()]
        print "samples : ",samples
        print "here"
        self.project.modified = datetime.datetime.now()
        self.project.save()
        file = self.request.FILES['file']
        print "first file name : ",file.name
        polarity = self.findpolarity(file)
        print "HERE polarity in the view : ",polarity
        if file.name.replace(" ", "_") not in samples:
            self.object = Picture.objects.create(project=self.project)
            print "file in view : ",file
            self.object.file.save(file.name, file)
            #self.object = form.save()
            #remettre :
            #self.object.addproject(self.project)

            #print "IIIIIICCCCCCCCIIIIIIII"
            #self.object.file = file
            #Fin Attention !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #sample = Picture.objects.create(project=self.project)#, file=file)
            #sample.file.save(file.name, file)
            #sample.save()
            #print "------------------------------ form has been saved, come back later!"

            f = self.request.FILES.get('file')
            #remettre :
            self.object.setname(f.name.replace(" ", "_"))
            print "view file name : ",f.name.replace(" ", "_")
            #print "Files have been requested now"
            #print settings.MEDIA_URL
            #print f.name.replace(" ", "_")
            #print self.object.id
            print "url : ",settings.MEDIA_URL,"projects/",self.project.id,"/",f.name.replace(" ", "_")
            self.object.setpolarity(polarity)
            print "file : ",self.object.file.name

            ################ Sample creation ##################
            if polarity == "-":
                samplefilegroup = SampleFileGroup.objects.create(type="mzxml",negdata=self.object)
                samplefilegroup.save()
            elif polarity == "+":
                samplefilegroup = SampleFileGroup.objects.create(type="mzxml",posdata=self.object)
                samplefilegroup.save()
            else:
                print "BIG PROBLEM, THERE IS NO POLARITY IN THIS FILE!!!!!!!!"
            sample = Sample.objects.create(project=self.project,name=self.object.name,samplefile=samplefilegroup)
            sample.save()
        else:
            sample = self.project.sample_set.get(name=file.name.replace(" ", "_"))
            if not sample.samplefile.posdata and polarity == "+":
                self.object = Picture.objects.create(project=self.project)
                self.object.file.save(file.name, file)
                f = self.request.FILES.get('file')
                #remettre :
                self.object.setname(f.name.replace(" ", "_"))
                self.object.setpolarity(polarity)
                sample.samplefile.posdata = self.object
                sample.samplefile.save()
                print "POS DATA CREATED"
            if not sample.samplefile.negdata and polarity == "-":
                self.object = Picture.objects.create(project=self.project)
                self.object.file.save(file.name, file)
                f = self.request.FILES.get('file')
                #remettre :
                self.object.setname(f.name.replace(" ", "_"))
                self.object.setpolarity(polarity)
                sample.samplefile.negdata = self.object
                sample.samplefile.save()
                print "NEG DATA CREATED"
        #print self.project.title
        #print settings.MEDIA_URL,"projects/",self.project.title,self.project.id,"/",f.name.replace(" ", "_")
        #data = [{"name": f.name, "url": settings.MEDIA_URL + "pictures/" + f.name.replace(" ", "_"), "thumbnail_url": settings.MEDIA_URL + "pictures/" + f.name.replace(" ", "_"), "delete_url": reverse("upload-delete", args=[self.project.id ,self.object.id]), "delete_type": "DELETE"}]# reverse("upload-delete", args=[self.object.id]), "delete_type": "DELETE"}]
        ##################### Good One ##########################################
        # data = [{"name": f.name, "url": settings.MEDIA_URL + "projects/"  + str(self.project.id )+ "/samples/" + f.name.replace(" ", "_"), "thumbnail_url": settings.MEDIA_URL + "projects/"  + str(self.project.id )+ "/samples/" + f.name.replace(" ", "_"), "delete_url": reverse("upload-delete", args=[self.project.id ,self.object.id]), "delete_type": "DELETE"}]
        data = [{"name": f.name, "url": settings.MEDIA_URL + str(self.object.file.name), "thumbnail_url": settings.MEDIA_URL + str(self.object.file.name), "delete_url": reverse("upload-delete", args=[self.project.id ,self.object.id]), "delete_type": "DELETE"}]
        #print "works here!!!!!!!!!!!!"
        response = JSONResponse(data, {}, response_mimetype(self.request))
        #print "ca marche toujours iciiiiiiiiiiii"
        response['Content-Disposition'] = 'inline; filename=files.json'
        print "works bien encore laaaaaaaaaaaaaaa!"
        return response

class ProjfileCreateView(CreateView):
    model = ProjFile
    form = FileForm

    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        return super(ProjfileCreateView, self).dispatch(*args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context_data = super(ProjfileCreateView, self).get_context_data(
            *args, **kwargs)
        print "session_data: ",self.request.session
        print "user: ",self.request.user

        user = self.request.user

        # Add for space limitation - the following code is used to calculate how much space is left to restrict the upload size
        owned_projects = Project.objects.filter(user_owner=user)
        calibration_samples = ProjFile.objects.filter(project__in=owned_projects).order_by('project__id')
        samples = Picture.objects.filter(project__in=owned_projects).order_by('project__id')

        storage_taken = {'samples': 0, 'calibration_samples': 0}


        for calibration_sample in calibration_samples:
            storage_taken['calibration_samples'] += calibration_sample.file.size
        for sample in samples:
            storage_taken['samples'] += sample.file.size

        total_storage = 53687091200

        storage_used = storage_taken['calibration_samples'] + storage_taken['samples']
        storage_remaining = int(float(total_storage) - storage_used)

        print "storage_used: ",storage_used
        print "storage_remaining: ",storage_remaining

        # if 'new_project' in self.request.session and self.request.session['new_project']:
        #     print "my session : ",self.request.session['new_project']
        #     new_project = self.request.session['new_project']
        # else:
        #     new_project = False
        context_data.update({'project': self.project, 'storage_remaining': storage_remaining})#,'new_project': new_project})

        return context_data

    def findpolarity(self, file):
        tree = etree.parse(file)
        handler = MyContentHandler()
        lxml.sax.saxify(tree, handler)
        return handler.polarity

    def form_valid(self, form):
        print "here"
        calibrationsamples = [sample.name for sample in self.project.calibrationsample_set.all()]

        self.project.modified = datetime.datetime.now()
        self.project.save()
        file = self.request.FILES['file']
        print "file in view : ",file

        if file.name.replace(" ", "_") not in calibrationsamples:
            print "calibration sample doesn't exist"
            print file.name.split(".")[1:][0]
            if file.name.split(".")[1:][0].upper() == "MZXML":
                print "this is mzxml file"
                self.object = ProjFile.objects.create(project=self.project)
                polarity = self.findpolarity(file)
                self.object.file.save(file.name, file)
                f = self.request.FILES.get('file')
                #remettre :
                self.object.setname(f.name.replace(" ", "_"))
                print "view file name : ",f.name.replace(" ", "_")
                print "url : ",settings.MEDIA_URL,"projects/",self.project.id,"/",f.name.replace(" ", "_")
                self.object.setpolarity(polarity)
                print "file : ",self.object.file.name

                if polarity == "-":
                    print "neg pol"
                    standardfilegroup = StandardFileGroup.objects.create(type="mzxml",negdata=self.object)
                    print "after sample group creation"
                    print standardfilegroup
                    standardfilegroup.save()
                    print "saved"
                elif polarity == "+":
                    print "pos pol"
                    standardfilegroup = StandardFileGroup.objects.create(type="mzxml",posdata=self.object)
                    standardfilegroup.save()
                else:
                    print "BIG PROBLEM, THERE IS NO POLARITY IN THIS FILE!!!!!!!!"
                print "before calibration sample"
                calibrationsample = CalibrationSample.objects.create(project=self.project,name=self.object.name,standardFile=standardfilegroup)
                print "calibration sample created"
                calibrationsample.save()
                print "calibration sample saved"

            elif file.name.split(".")[1:][0].upper() == "CSV":
                print "this is mzxml file"
                self.object = ProjFile.objects.create(project=self.project)
                # polarity = self.findpolarity(file)
                self.object.file.save(file.name, file)
                f = self.request.FILES.get('file')
                #remettre :
                self.object.setname(f.name.replace(" ", "_"))
                print "view file name : ",f.name.replace(" ", "_")
                # print "url : ",settings.MEDIA_URL,"projects/",self.project.id,"/",f.name.replace(" ", "_")
                self.object.setpolarity("std")
                print "file : ",self.object.file.name
                standardfilegroup = StandardFileGroup.objects.create(type="toxid",data=self.object)
                print "after sample group creation"
                print standardfilegroup
                standardfilegroup.save()
                calibrationsample = CalibrationSample.objects.create(project=self.project,name=self.object.name,standardFile=standardfilegroup)
                print "calibration sample created"
                calibrationsample.save()

        else:
            if file.name.split(".")[1:][0].upper() == "MZXML":
                sample = self.project.calibrationsample_set.get(name=file.name.replace(" ", "_"))
                polarity = self.findpolarity(file)
                print "calibration sample found"
                print "posdata :",sample.standardFile.posdata
                print "negdata :",sample.standardFile.negdata
                print "polarity :",polarity
                if not sample.standardFile.posdata and polarity == "+":
                    print "calibration sample +"
                    self.object = ProjFile.objects.create(project=self.project)
                    self.object.file.save(file.name, file)
                    f = self.request.FILES.get('file')
                    #remettre :
                    self.object.setname(f.name.replace(" ", "_"))
                    self.object.setpolarity(polarity)
                    sample.standardFile.posdata = self.object
                    sample.standardFile.save()
                    print "POS DATA CREATED"
                if not sample.standardFile.negdata and polarity == "-":
                    print "calibration -"
                    self.object = ProjFile.objects.create(project=self.project)
                    self.object.file.save(file.name, file)
                    f = self.request.FILES.get('file')
                    #remettre :
                    self.object.setname(f.name.replace(" ", "_"))
                    self.object.setpolarity(polarity)
                    sample.standardFile.negdata = self.object
                    sample.standardFile.save()
                    print "NEG DATA CREATED"

        ############################# reprendre ici ####################################
        # self.object.file.save(file.name, file)
        # f = self.request.FILES.get('file')
        # self.object.setname(f.name.replace(" ", "_"))

        # print "view file name : ",f.name.replace(" ", "_")
        # print "url : ",settings.MEDIA_URL,"projects/",self.project.id,"/",f.name.replace(" ", "_")

        data = [{"name": f.name, "url": settings.MEDIA_URL + str(self.object.file.name), "thumbnail_url": settings.MEDIA_URL + str(self.object.file.name), "delete_url": reverse("upload-projfile-delete", args=[self.project.id ,self.object.id]), "delete_type": "DELETE"}]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        # self.request.session['projfile_upload'] = True
        print "works bien encore laaaaaaaaaaaaaaa!"
        return response



class PictureDeleteView(DeleteView):
    model = Picture

    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        return super(PictureDeleteView, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.project.modified = datetime.datetime.now()
        self.project.save()
        self.object = self.get_object()
        print self.object
        print "iiiiiiiiccccccccccciiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect('/upload/new')

class ProjfileDeleteView(DeleteView):
    model = ProjFile

    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=kwargs['project_id'])
        return super(ProjfileDeleteView, self).dispatch(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.project.modified = datetime.datetime.now()
        self.project.save()
        print "in delete"
        self.object = self.get_object()
        print "delete : ",self.object
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect('/upload/new/projectfile/')

class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self,obj='',json_opts={},mimetype="application/json",*args,**kwargs):
        content = simplejson.dumps(obj,**json_opts)
        super(JSONResponse,self).__init__(content,mimetype,*args,**kwargs)
