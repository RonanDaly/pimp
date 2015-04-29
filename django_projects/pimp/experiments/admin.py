from django.contrib import admin
from experiments.models import *

admin.site.register(DefaultParameter)
admin.site.register(Experiment)
admin.site.register(Analysis)
admin.site.register(Comparison)
