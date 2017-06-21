from django.db import models
from groups.models import Attribute
from projects.models import Project

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

    def getControlAttribute(self):
        minac = min(self.attributecomparison_set.all(), key=lambda ac: ac.group)
        return minac.attribute

    def getCaseAttribute(self):
        maxac = max(self.attributecomparison_set.all(), key=lambda ac: ac.group)
        return maxac.attribute

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

    def __unicode__(self):
        return self.experiment.title

    def get_project(self):
        projects = Project.objects.filter(sample__attribute__comparison__experiment__analysis=self.id).distinct()
        if len(projects) != 1:
            raise Exception('More or less than one project for an analysis: %d projects, analysis_id=%s' % (len(projects),self.id))
        return projects[0]

class DefaultParameter(models.Model):
    name = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
    state = models.NullBooleanField(null=True)

