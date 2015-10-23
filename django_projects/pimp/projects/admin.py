from django.contrib import admin
from projects.models import Project, UserProject

admin.site.register(Project)
admin.site.register(UserProject)