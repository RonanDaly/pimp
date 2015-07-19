from django.conf.urls import patterns, url
from frank import views

urlpatterns = patterns ('',
    url(r'^$', views.index, name = 'frank_index'),
    url(r'^sign_up/$', views.sign_up, name = 'sign_up'),
    url(r'^sign_in/$', views.sign_in, name = 'sign_in'),
    url(r'^logout/$', views.user_logout, name = 'user_logout'),
    url(r'^my_experiments/$', views.my_experiments, name = 'my_experiments'),
    url(r'^my_experiments/add_experiment/$', views.add_experiment, name = 'add_experiment'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/$', views.experimentSummary, name = 'experimentSummary'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/add_experimental_condition/$',
        views.add_experimental_condition, name = 'add_experimental_condition'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/(?P<condition_name_slug>[\w\-]+)/$',
        views.conditionSummary, name = 'conditionSummary'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/(?P<condition_name_slug>[\w\-]+)/add_sample/$',
        views.add_sample, name = 'add_sample'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/(?P<condition_name_slug>[\w\-]+)/(?P<sample_slug>[\w\-]+)/add_sample_file/$',
        views.addSampleFile, name = 'add_sample_file'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/create_fragmentation_set$', views.create_fragmentation_set, name = 'create_fragmentation_set'),
    url(r'^my_fragmentation_sets/$', views.fragmentation_set_summary, name = 'fragmentation_set_summary'),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)$', views.fragmentation_set, name = 'fragmentation_set'),
    url(r'^my_fragmentation_sets/(?P<fragmentation_set_name_slug>[\w\-]+)/(?P<peak_name_slug>[\w\-]+)$', views.peak_summary, name = 'peak_summary'),



    ### Testing Views ####
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/analyse$', views.input_peak_list_to_database, name = 'analyse'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/annotate$', views.get_massBank_annotations, name = 'massBank'),
)
