from django.db import models
from fileupload.models import Picture, ProjFile, Sample, CalibrationSample
import datetime
from projects.models import Project

class TicFile(models.Model):
	ticplot = models.FilePathField(blank=True, null=True)
	meanticplot = models.FilePathField(blank=True, null=True)
	medianticplot = models.FilePathField(blank=True, null=True)

class TicGroup(models.Model):
	postic = models.ForeignKey(TicFile, related_name='postic', blank=True, null=True)
	negtic = models.ForeignKey(TicFile, related_name='negtic', blank=True, null=True)

class Group(models.Model):
	# print "group is creating!!"
	name = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

class Attribute(models.Model):
	# print "attribute is creating"
	name = models.CharField(max_length=150)
	group = models.ForeignKey(Group)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now_add=True)
	sample = models.ManyToManyField(Sample, through='SampleAttribute')
	calibrationsample = models.ManyToManyField(CalibrationSample, through='ProjfileAttribute')
	ticgroup = models.ForeignKey(TicGroup, blank=True, null=True)

	def __unicode__(self):
		if self.group :
			return self.name + " (" + str(self.group) + ")"
		else:
			return self.name

class SampleAttribute(models.Model):
	sample = models.ForeignKey(Sample)
	attribute = models.ForeignKey(Attribute)
	date_joined = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return str(self.attribute) + " (" + str(self.sample) + ")"


class ProjfileAttribute(models.Model):
	calibrationsample = models.ForeignKey(CalibrationSample)
	attribute = models.ForeignKey(Attribute)
	date_joined = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return str(self.attribute) + " (" + str(self.calibrationsample) + ")"

