__author__ = 'scott greig'

from django.contrib import admin
from frank.models import *


"""
 ModelAdminClasses - These classes simply define which attributes of the model classes are to be
 displayed in the Django admin pages.
"""


class ExperimentAdmin (admin.ModelAdmin):
    """
    Class to show the fields of the Experiment model in the django admin pages
    """
    list_display = (
        'title', 'description', 'created_by', 'time_created',
        'ionisation_method', 'detection_method', 'slug'
    )


class UserExperimentAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the UserExperiments model in the django admin pages
    """
    list_display = ('user', 'experiment')


class ExperimentalConditionAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the ExperimentalCondition model in the django admin pages
    """
    list_display = ('name', 'description', 'experiment', 'slug')


class SampleAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the Sample model in the django admin pages
    """
    list_display = ('name', 'description', 'experimental_condition', 'organism', 'slug')


class SampleFileAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the SampleFile model in the django admin pages
    """
    list_display = ('name', 'polarity', 'address', 'sample')


class FragmentationSetAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the FragmentationSet model in the django admin pages
    """
    list_display = ('name', 'experiment', 'time_created', 'status', 'slug')


class AnnotationQueryAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the AnnotationQuery model in the django admin pages
    """
    list_display = (
        'name', 'fragmentation_set', 'time_created',
        'status', 'slug', 'annotation_tool', 'annotation_tool_params',
    )


class AnnotationToolAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the AnnotationTool model in the django admin pages
    """
    list_display = ('name', "default_params")


class CompoundAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the Compound model in the django admin pages
    """
    list_display = ('name', 'formula', 'exact_mass', 'inchikey', 'cas_code',)


class PeakAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the Peak model in the django admin pages
    """
    list_display = (
        'id', 'source_file', 'mass', 'retention_time', 'intensity',
        'parent_peak', 'msn_level', 'fragmentation_set',
        'slug', 'preferred_candidate_annotation',
    )


class CandidateAnnotationAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the CandidateAnnotation model in the django admin pages
    """
    list_display = (
        'compound', 'peak', 'confidence', 'annotation_query',
        'mass_match', 'difference_from_peak_mass',
        'adduct', 'instrument_type', 'collision_energy'
    )


class CompoundAnnotationToolAdmin(admin.ModelAdmin):
    """
    Class to show the fields of the CompoundAnnotation model in the django admin pages
    """
    list_display = ('compound', 'annotation_tool', 'annotation_tool_identifier')


class ExperimentalProtocolAdmin (admin.ModelAdmin):
    """
    Class to show the fields of the ExperimentalProtocol model in the django admin pages
    """
    list_display = ('name',)


class AnnotationToolProtocolAdmin (admin.ModelAdmin):
    """
    Class to show the fields of the AnnotationToolProtocols model in the django admin pages
    """
    list_display = ('annotation_tool', 'experimental_protocol')


class AnnotationQueryHierarchyAdmin (admin.ModelAdmin):
    """
    Class to show the fields of the AnnotationQueryHierarchy model in the django admin pages
    """
    list_display = ('parent_annotation_query', 'subquery_annotation_query')


# Register each of the models and admin classes for display to user in admin site
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(UserExperiment, UserExperimentAdmin)
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
admin.site.register(AnnotationToolProtocol, AnnotationToolProtocolAdmin)
admin.site.register(AnnotationQueryHierarchy, AnnotationQueryHierarchyAdmin)