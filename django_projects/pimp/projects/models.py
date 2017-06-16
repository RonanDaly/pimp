from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import datetime
# Create your models here.

class Project(models.Model):

	title = models.CharField(max_length=100)
	# owner = models.CharField(max_length=100)
	user_owner = models.ForeignKey(User,related_name='user_owner')
	users = models.ManyToManyField(User, through='UserProject')
	description = models.CharField(max_length=300, blank=True, null=True)
	created = models.DateTimeField(editable=False)
	modified = models.DateTimeField()
	# organism = models.CharField(max_length=100, blank=True, null=True)
	#friends = models.ManyToManyField("self")

	class Meta:
		ordering = ['-modified']

	
	def __unicode__(self):
		return self.title

	def get_project(self, analysis_id):
		projects = Project.objects.filter(sample__attribute__comparison__experiment__analysis=analysis_id).distinct()
		if len(projects) != 1:
			raise Exception('More or less than one project for an analysis: %d projects, analysis_id=%s' % (len(projects),analysis_id))
		return projects[0]

class UserProject(models.Model):
	user = models.ForeignKey(User)
	project = models.ForeignKey(Project)
	date_joined = models.DateTimeField()
	permission = models.CharField(max_length=10)
	#invite_reason = models.CharField(max_length=64)
	#created_at = models.DateTimeField(auto_now_add = True)
	#updated_at = models.DateTimeField(auto_now = True)