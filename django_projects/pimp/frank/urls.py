__author__ = 'Scott Greig'

from django.conf.urls import patterns, url
from frank import views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='frank_index'),
    url(r'^my_experiments/$', views.my_experiments, name='my_experiments'),
    url(r'^my_experiments/add_experiment/$', views.add_experiment, name='add_experiment'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/$', views.experiment_summary, name='experiment_summary'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/add_experimental_condition/$',
        views.add_experimental_condition, name='add_experimental_condition'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/create_fragmentation_set/$',
        views.create_fragmentation_set, name='create_fragmentation_set'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/(?P<condition_name_slug>[\w\-]+)/$',
        views.condition_summary, name='condition_summary'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/(?P<condition_name_slug>[\w\-]+)/add_sample/$',
        views.add_sample, name='add_sample'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/(?P<condition_name_slug>[\w\-]+)'
        r'/(?P<sample_slug>[\w\-]+)/add_sample_file/$', views.add_sample_file, name='add_sample_file'),
    url(r'^my_fragmentation_sets/$', views.fragmentation_set_summary, name='fragmentation_set_summary'),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)/$',
        views.fragmentation_set, name='fragmentation_set'),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)/(?P<annotation_tool_slug>[\w\-]+)'
        r'/define_annotation_query_paramaters/$', views.define_annotation_query, name='define_annotation_query'),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)'
        r'/(?P<peak_name_slug>[\w\-]+)/$', views.peak_summary, name='peak_summary'),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)'
        r'/(?P<peak_name_slug>[\w\-]+)/msn_spectra_plot.png/$', views.make_frag_spectra_plot, name="make_spectra_plot"),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)/(?P<peak_name_slug>[\w\-]+)'
        r'/(?P<annotation_id>[\w\-]+)/specify_preferred_annotation/$',
        views.specify_preferred_annotation, name='specify_preferred_annotation'),
    url(r'^remove_preferred_annotations/(?P<fragmentation_set_name_slug>[\w\-]+)',
        views.remove_preferred_annotations, name='remove_preferred_annotations'),
    url(r'^delete_annotation_query/(?P<fragmentation_set_name_slug>[\w\-]+)'
        r'/(?P<annotation_query_slug>[\w\-]+)/$',views.delete_annotation_query, name='delete_annotation_query'),
    # Network sample URL added by Simon
    url(r'^network_sampler/$',views.run_network_sampler, name='network_sampler'),
    url(r'^connect/(?P<pimp_project_id>[\w\-]+)/(?P<pimp_analysis_id>[\w\-]+)/$',views.connect,name='connect'),
    url(r'^get_fragments_as_text/(?P<peak_name_slug>[\w\-]+)/(?P<format_type>[\w\-]+)/$',views.get_fragments_as_text, name='get_fragments_as_text'),
    # Mass2lda URL added by Claire.
    url(r'^ms2lda_visualisation/(?P<fragmentation_set_name_slug>[\w\-]+)/(?P<annotation_id>[\w\-]+)/$',
        views.mass2lda_vis, name='ms2lda_vis'),    
)
