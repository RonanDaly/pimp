from django.contrib import admin
from frank.models import *

# The fields to be displayed in the Experiment page of admin
class ExperimentAdmin (admin.ModelAdmin):
    list_display = ('title', 'description', 'createdBy', 'timeCreated',
                    'lastModified', 'ionisationMethod', 'detectionMethod',
                    'slug'
    )

# The fields to be displayed in the UserExperiments page of admin
class UserExperimentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'experiment')

# The fields to be displayed in the ExperimentalCondition page of admin
class ExperimentalConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'experiment', 'slug')

# The fields to be displayed in the Sample page of admin
class SampleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'experimentalCondition', 'organism', 'slug')

# The fields to be displayed in the SampleFile page of admin
class SampleFileAdmin(admin.ModelAdmin):
    list_display = ('name','polarity', 'address', 'sample')

# The fields to be displayed in the Analysis page of admin
class FragmentationSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'timeCreated', 'status', 'slug')

# The fields to be displayed in the Analysis page of admin
class AnnotationQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'fragmentation_set', 'timeCreated', 'status', 'slug', 'massBank', 'massBank_params')

# The fields to be displayed in the Repository page of admin
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

# The fields to be displayed in the Compound page of admin
class CompoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'formula', 'exact_mass', 'inchikey')

# The fields to be displayed in the Peak page of admin
class PeakAdmin(admin.ModelAdmin):
    list_display = ('id', 'sourceFile', 'mass', 'retentionTime', 'intensity',
                    'parentPeak', 'msnLevel', 'fragmentation_set', 'slug', 'preferred_candidate_annotation')

# The fields to be displayed in the CandidateAnnotation page of admin
class CandidateAnnotationAdmin(admin.ModelAdmin):
    list_display = ('compound', 'peak', 'confidence', 'annotation_query', 'mass_match', 'difference_from_peak_mass', 'adduct', 'instrument_type')

# The fields to be displayed in the CompoundRepository page of admin
class CompoundRepositoryAdmin(admin.ModelAdmin):
    list_display = ('compound', 'repository', 'repository_identifier')


# Register each of the models and forms with the admin for display to user in admin site
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(UserExperiments, UserExperimentsAdmin)
admin.site.register(ExperimentalCondition, ExperimentalConditionAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SampleFile, SampleFileAdmin)
admin.site.register(FragmentationSet, FragmentationSetAdmin)
admin.site.register(AnnotationQuery, AnnotationQueryAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Compound, CompoundAdmin)
admin.site.register(Peak, PeakAdmin)
admin.site.register(CandidateAnnotation, CandidateAnnotationAdmin)
admin.site.register(CompoundRepository, CompoundRepositoryAdmin)

