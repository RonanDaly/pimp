from django.contrib import admin
from frank.models import *

# The fields to be displayed in the Experiment page of django admin
class ExperimentAdmin (admin.ModelAdmin):
    list_display = ('title', 'description', 'created_by', 'time_created',
                    'last_modified', 'ionisation_method', 'detection_method',
                    'slug'
    )

# The fields to be displayed in the User Experiments page of admin
class UserExperimentsAdmin(admin.ModelAdmin):
    list_display = ('user', 'experiment')

# The fields to be displayed in the Experimental Condition page of admin
class ExperimentalConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'experiment', 'slug')

# The fields to be displayed in the Sample page of admin
class SampleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'experimental_condition', 'organism', 'slug')

# The fields to be displayed in the Sample File page of admin
class SampleFileAdmin(admin.ModelAdmin):
    list_display = ('name','polarity', 'address', 'sample')

# The fields to be displayed in the Fragmentation Set page of admin
class FragmentationSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'experiment', 'time_created', 'status', 'slug')

# The fields to be displayed in the Annotation Query page of admin
class AnnotationQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'fragmentation_set', 'time_created',
                    'status', 'slug', 'annotation_tool', 'annotation_tool_params',
    )

# The fields to be displayed in the AnnotationTool page of admin
class AnnotationToolAdmin(admin.ModelAdmin):
    list_display = ('name',)

# The fields to be displayed in the Compound page of admin
class CompoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'formula', 'exact_mass', 'inchikey', 'cas_code',)

# The fields to be displayed in the Peak page of admin
class PeakAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_file', 'mass', 'retention_time', 'intensity',
                    'parent_peak', 'msn_level', 'fragmentation_set',
                    'slug', 'preferred_candidate_annotation',
    )

# The fields to be displayed in the Candidate Annotation page of admin
class CandidateAnnotationAdmin(admin.ModelAdmin):
    list_display = ('compound', 'peak', 'confidence', 'annotation_query',
                    'mass_match', 'difference_from_peak_mass',
                    'adduct', 'instrument_type',
    )

# The fields to be displayed in the CompoundAnnotationTool page of admin
class CompoundAnnotationToolAdmin(admin.ModelAdmin):
    list_display = ('compound', 'annotation_tool', 'annotation_tool_identifier')


# The fields to be displayed in the ExperimentalProtocol page of the admin
class ExperimentalProtocolAdmin (admin.ModelAdmin):
    list_display = ('name',)


# The fields to be displayed in the AnnotationToolProtocols page of the admin
class AnnotationToolProtocolsAdmin (admin.ModelAdmin):
    list_display = ('annotation_tool', 'experimental_protocol')


class AnnotationQueryHierarchyAdmin (admin.ModelAdmin):
    list_display = ('parent_annotation_query', 'subquery_annotation_query')


# Register each of the models and admin classes for display to user in admin site
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(UserExperiments, UserExperimentsAdmin)
admin.site.register(ExperimentalCondition, ExperimentalConditionAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(SampleFile, SampleFileAdmin)
admin.site.register(FragmentationSet, FragmentationSetAdmin)
admin.site.register(AnnotationQuery, AnnotationQueryAdmin)
admin.site.register(AnnotationTool, AnnotationToolAdmin)
admin.site.register(Compound, CompoundAdmin)
admin.site.register(Peak, PeakAdmin)
admin.site.register(CandidateAnnotation, CandidateAnnotationAdmin)
admin.site.register(CompoundAnnotationTool, CompoundAnnotationToolAdmin)
admin.site.register(ExperimentalProtocol, ExperimentalProtocolAdmin)
admin.site.register(AnnotationToolProtocols, AnnotationToolProtocolsAdmin)
admin.site.register(AnnotationQueryHierarchy, AnnotationQueryHierarchyAdmin)

