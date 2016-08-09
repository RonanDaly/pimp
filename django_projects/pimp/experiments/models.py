from django.db import models
from groups.models import Attribute

# Create your models here.
class Experiment(models.Model):
	title = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True)
	modified = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-modified']

	def __unicode__(self):
		return self.title

class Comparison(models.Model):
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=100)
	experiment = models.ForeignKey(Experiment)
	attribute = models.ManyToManyField(Attribute, through='AttributeComparison')

	def __unicode__(self):
		return self.name

class AttributeComparison(models.Model):
	# AttributeComparisons with the same group and comparison have been grouped together.
	# If there are two groups, the lower group is the control group.
	group = models.IntegerField()
	attribute = models.ForeignKey(Attribute)
	comparison = models.ForeignKey(Comparison)

class Parameter(models.Model):
	name = models.CharField(max_length=100)
	value = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
	state = models.NullBooleanField(null=True)

class Database(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
    	return self.name

class Params(models.Model):
	param = models.ManyToManyField(Parameter)
	databases = models.ManyToManyField(Database)

class Analysis(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	submited = models.DateTimeField(blank=True,null=True)
	owner = models.CharField(max_length=100)
	experiment = models.ForeignKey(Experiment)
	params = models.ForeignKey(Params)
	status = models.CharField(max_length=100) 

class DefaultParameter(models.Model):
	name = models.CharField(max_length=100)
	value = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
	state = models.NullBooleanField(null=True)

