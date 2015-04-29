from django.db import models
from projects.models import Project
import datetime
import os
from lxml import etree
import lxml.sax
from xml.sax.handler import ContentHandler
from django.conf import settings
from django.core.files.move import file_move_safe

class Curve(models.Model):

    x_axis = models.TextField(blank=True, null=True)
    y_axis = models.TextField(blank=True, null=True)
    mean = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)

def get_sample_path(instance, filename):
    return os.path.join('projects',str(instance.project.id), 'samples', filename.replace(" ", "_"))


class Picture(models.Model):

    # This is a small demo using just two fields. The slug field is really not
    # necessary, but makes the code simpler. ImageField depends on PIL or
    # pillow (where Pillow is easily installable in a virtualenv. If you have
    # problems installing pillow, use a more generic FileField instead.

    
    uploaded = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    file = models.FileField(upload_to=get_sample_path)
    #file = models.ImageField(upload_to="projects")
    polarity = models.CharField(max_length=1, blank=True, null=True)
    tic = models.ForeignKey(Curve, blank=True, null=True)
    name = models.CharField(max_length=60, blank=True, null=True)
    slug = models.SlugField(max_length=80, blank=True)

    def __unicode__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, my_value=None, *args, **kwargs):
        self.slug = self.file.name
        super(Picture, self).save(*args, **kwargs)

    def addproject(self, project):
        self.project = project
        self.save()

    def setname(self, name):
        self.name = name
        self.save()

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        print "prout"
        print "deleting!!!!!!!"
        if self.polarity == "+":
            if self.posdata.all()[0].negdata:
                print "il reste un negatif"
                self.posdata.clear()
                print "foreign key reset"
                super(Picture, self).delete(*args, **kwargs) 
            else:
                print "plus de negatif on supprime le positive et au dessus"
                super(Picture, self).delete(*args, **kwargs)
        if self.polarity == "-":
            if self.negdata.all()[0].posdata:
                print "il reste un negatif"
                self.negdata.clear()
                print "foreign key reset"
                super(Picture, self).delete(*args, **kwargs) 
            else:
                print "plus de positif on supprime le negatif et au dessus"
                super(Picture, self).delete(*args, **kwargs) 

    def setpolarity(self, polarity):
        if polarity == "+":
            new_path = os.path.join('projects',str(self.project.id), 'samples', 'POS', self.name)
        elif polarity == "-":
            new_path = os.path.join('projects',str(self.project.id), 'samples', 'NEG', self.name)
        
        # print new_path
        saved_to = self.file.storage.save(new_path, self.file)
        self.file.storage.delete(self.file.name)
        self.file = saved_to
        self.polarity = polarity
        self.save()
        
        # print "model file :",self.file
        # print "model slug :",self.slug
        # print "model name :",self.name
        # print "model polarity :",self.polarity
        # print "polarity in the model :",polarity
        # file_move_safe(file, "/POS"+file)
        # print handler.polarity

        # return polarity


def get_proj_file_path(instance, filename):
    print "get_sample_path : ",instance.project
    #print truc
    print "filename in get_sample_path : ", filename
    print "os path join : ",os.path.join('projects',str(instance.project.id), 'calibration_samples', filename)
    return os.path.join('projects',str(instance.project.id), 'calibration_samples', filename.replace(" ", "_"))

class ProjFile(models.Model):

    # This is a small demo using just two fields. The slug field is really not
    # necessary, but makes the code simpler. ImageField depends on PIL or
    # pillow (where Pillow is easily installable in a virtualenv. If you have
    # problems installing pillow, use a more generic FileField instead.

    
    uploaded = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    file = models.FileField(upload_to=get_proj_file_path)
    polarity = models.CharField(max_length=3, blank=True, null=True)
    tic = models.ForeignKey(Curve, blank=True, null=True)
    name = models.CharField(max_length=60, blank=True, null=True)
    slug = models.SlugField(max_length=80, blank=True)

    def __unicode__(self):
        return self.file.name

    @models.permalink
    def get_absolute_url(self):
        return ('upload-new', )

    def save(self, my_value=None, *args, **kwargs):
        print "I'm in the save methode!!"
        #print "my value is here les kikis: ",my_value
        print "in save method project: ",self.project
        print "in save method file name: ",self.file.name
        self.slug = self.file.name
        super(ProjFile, self).save(*args, **kwargs)

    def addproject(self, project):
        self.project = project
        #print "project added",project
        self.save()
        #print "iccccccccccccciiiiiiiiiii",self.project

    def setname(self, name):
        self.name = name
        self.save()
        #print "the name should be save here if that is working",self.name

    def delete(self, *args, **kwargs):
        self.file.delete(False)
        super(ProjFile, self).delete(*args, **kwargs)

    def setpolarity(self, polarity):
        if polarity == "+":
            new_path = os.path.join('projects',str(self.project.id), 'calibration_samples', 'POS', self.name)
        elif polarity == "-":
            new_path = os.path.join('projects',str(self.project.id), 'calibration_samples', 'NEG', self.name)
        elif polarity == "std":
            new_path = os.path.join('projects',str(self.project.id), 'calibration_samples', 'standard', self.name)
        
        # print new_path
        saved_to = self.file.storage.save(new_path, self.file)
        self.file.storage.delete(self.file.name)
        self.file = saved_to
        if polarity != "std":
            self.polarity = polarity
        self.save()


class SampleFileGroup(models.Model):
    
    type = models.CharField(max_length=20, blank=True, null=True)
    posdata = models.ForeignKey(Picture, related_name='posdata', blank=True, null=True)
    negdata = models.ForeignKey(Picture, related_name='negdata', blank=True, null=True)

class StandardFileGroup(models.Model):

    type = models.CharField(max_length=20, blank=True, null=True)
    data = models.ForeignKey(ProjFile, related_name='data', blank=True, null=True)
    posdata = models.ForeignKey(ProjFile, related_name='posdata', blank=True, null=True)
    negdata = models.ForeignKey(ProjFile, related_name='negdata', blank=True, null=True)

class Sample(models.Model):
    name = models.CharField(max_length=60, blank=True, null=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    samplefile = models.ForeignKey(SampleFileGroup, blank=True, null=True)

    def __unicode__(self):
        return self.name

class CalibrationSample(models.Model):

    name = models.CharField(max_length=60, blank=True, null=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    standardFile = models.ForeignKey(StandardFileGroup, blank=True, null=True)
