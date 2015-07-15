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
    ### Views to be done ####
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/analyse$', views.analyse, name = 'analyse'),
    url(r'^my_experiments/(?P<experiment_name_slug>[\w\-]+)/annotate$', views.get_massBank_annotations, name = 'massBank'),
)
