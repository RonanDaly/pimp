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

class UserProject(models.Model):
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    date_joined = models.DateTimeField()
    permission = models.CharField(max_length=10)
    #invite_reason = models.CharField(max_length=64)
    #created_at = models.DateTimeField(auto_now_add = True)
    #updated_at = models.DateTimeField(auto_now = True)