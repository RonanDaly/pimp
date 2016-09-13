from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from registration.forms import RegistrationFormUniqueEmail
from registration.backends.default.views import RegistrationView
from gp_registration.forms import MyExtendedForm
########################## Deprecated version ########################
# from django.views.generic.simple import direct_to_template
########################## End deprecated version ########################
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ideomsite.views.home', name='home'),
    # url(r'^ideomsite/', include('ideomsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'home.views.index', name='index'),
    url(r'^chemical_library/$', 'home.views.chemical_library', name='chemical_library'),
    url(r'^polyomics_chemical_library/$', 'home.views.polyomics_chemical_library', name='polyomics_chemical_library'),
    # Temporary !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    url(r'^result/$', 'home.views.result', name='result'),
    url(r'^result/getpeaks/$', 'home.views.get_peaks', name='get_peaks'),
    # End temporary !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    url(r'^about/', 'home.views.about', name='about'),
    url(r'^register/$',
        RegistrationView.as_view(form_class = MyExtendedForm),
        name = 'registration_register'),
    url(r'^accounts/register/$',
        RegistrationView.as_view(form_class = MyExtendedForm),
        name = 'registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # url(r'^register/$',
    #     RegistrationView.as_view(form_class=RegistrationFormUniqueEmail),
    #     name='registration_register'),
    # TODO : Double check if this is correct
    # url(r'^accounts/profile/$', direct_to_template,
    #     {'template': 'registration/profile.html'},
    #     name='profile'),
    url(r'^accounts/profile/$', 'gp_registration.views.profile', name='profile'),
    # projects page : display all projects belonging to the user
    url(r'^accounts/project/$', 'projects.views.summary', name='project_summary'),
    # new project page : form to create a new project (title and comments only)
    url(r'^accounts/newproject/$', 'projects.views.newproject', name='newproject'),
    # porject details page : page from where you can manage your project (upload samples, add user, edit, create groups)
    url(r'^accounts/project/(?P<project_id>\d+)/$', 'projects.views.detail', name='project_detail'),
    # result page for an analysis
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/$', 'experiments.views.analysis_result', name='analysis_result'),
    # ajax request for peak info
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/peak_info/$', 'experiments.views.peak_info', name='get_peak_info'),
    # ajax request for peak info
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/peak_info_peak_id/$', 'experiments.views.peak_info_peak_id', name='get_peak_info_peak_id'),
    # ajax request for compound info
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/compound_info/$', 'experiments.views.compound_info', name='get_compound_info'),
    # ajax request for metabolite info
    url(r'^account/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/metabolite_info/$', 'experiments.views.get_metabolite_info', name='get_metabolite_info'),
    # ajax request for peaks chromatogram from compound
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/peaks_from_compound/$', 'experiments.views.get_peaks_from_compound', name='get_peaks_from_compound'),
    # ajax request for peaks chromatogram from compound
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/peaks_from_peak_id/$', 'experiments.views.get_peaks_from_peak_id', name='get_peaks_from_peak_id'),
    # ajax request for peaks chromatogram from compound
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/get_compounds_from_peak_id/$', 'experiments.views.get_compounds_from_peak_id', name='get_compounds_from_peak_id'),
    # ajax request to get info for MetExplpore
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/get_metexplore_info/$', 'experiments.views.get_metexplore_info', name='get_metexplore_info'),
    # ajax request to get identification table
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/get_metabolites_table/$', 'experiments.views.get_metabolites_table', name='get_metabolites_table'),
    # ajax request to get peak table
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/get_peak_table/$', 'experiments.views.get_peak_table', name='get_peak_table'),
    # ajax request to get single comparison table - comparison id is given as ajax parameter
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/get_single_comparison_table/(?P<comparison_id>\d+)/$', 'experiments.views.get_single_comparison_table', name='get_single_comparison_table'),
    # ajax request to get pathway map url
    url(r'^accounts/project/(?P<project_id>\d+)/analysis/(?P<analysis_id>\d+)/get_pathway_url/$', 'experiments.views.get_pathway_url', name='get_pathway_url'),
    # ajax request for peak discovery
    url(r'^accounts/project/(?P<project_id>\d+)/peak_discovery/$', 'projects.views.peak_discovery', name='peak_discovery'),
    # ajax request to start analysis
    url(r'^accounts/project/(?P<project_id>\d+)/start_analysis/$', 'experiments.views.start_analysis', name='start_analysis'),
    # ajax request to return tic plots
    url(r'^accounts/project/(?P<project_id>\d+)/(?P<attribute_id>\d+)/$', 'projects.views.get_tic', name='get_tic'),
    # ajax request to return group tic plots
    url(r'^accounts/project/(?P<project_id>\d+)/ticgroup/(?P<group_id>\d+)/$', 'projects.views.get_group_tic', name='get_group_tic'),
    # ajax request to return mzxml data
    url(r'^accounts/project/(?P<project_id>\d+)/sample/(?P<sample_id>\d+)/$', 'projects.views.get_mzxml_tic', name='get_mzxml'),
    # ajax request to return mzxml scan data (return mass spectra for a specific retention time)
    url(r'^accounts/project/(?P<project_id>\d+)/sample/(?P<sample_id>\d+)/scan/$', 'projects.views.get_scan', name='get_scan'),
    # project description page : form to edit description in a project
    url(r'^accounts/project/(?P<project_id>\d+)/edit_description/$', 'projects.views.editdescription', name='edit_description'),
	# project description page: form to edit title of a project
    url(r'^accounts/project/(?P<project_id>\d+)/edit_title/$', 'projects.views.edit_title', name='edit_title'),
    # add user on project page : form to add a user to a project
    url(r'^accounts/project/(?P<project_id>\d+)/adduser/$', 'projects.views.adduser', name='add_user'),
    # upload and delete file
    url(r'^accounts/project/(?P<project_id>\d+)/upload/', include('fileupload.urls')),
    # create group
    url(r'^accounts/project/(?P<project_id>\d+)/group/', 'groups.views.index', name='add_group'),
    # assign file to group
    url(r'^accounts/project/(?P<project_id>\d+)/attribute/', 'groups.views.create_calibration_groups', name='projfile_attribute'),
    # submit an experiment to create the dataset attached
    # url(r'^accounts/project/(?P<project_id>\d+)/experiment/(?P<experiment_id>\d+)/$', 'experiments.views.create_dataset', name='create_dataset'),
    # create an experiment
    url(r'^accounts/project/(?P<project_id>\d+)/experiment/', 'experiments.views.experiment', name='create_experiment'),
    # delete sample file
    url(r'^accounts/project/(?P<project_id>\d+)/samples/delete', 'projects.views.sampleDelete', name='delete-sample'),
    # delete project file
    url(r'^accounts/project/(?P<project_id>\d+)/projectfiles/delete', 'projects.views.projectFileDelete', name='delete-projectfile'),
    url(r'^accounts/project/(?P<project_id>\d+)/remove_user_project/(?P<user_id>\d+)/','projects.views.removeUserProject',name='remove_user_project'),
    #url(r'^accounts/project/(?P<project_id>\d+)/group/', 'projects.views.groupcreation', name='create_goupe'),
    #url(r'^accounts/project/(?P<project_id>\d+)/group/', include('groups.urls')),
    #url(r'^accounts/project/(?P<project_id>\d+)/group/', include('multiuploader.urls')),
    #url(r'^frank/', include('frank.urls')),
    url(r'^credits/$', 'home.views.credits', name='credits'),
    url(r'^licence/$', 'home.views.licence', name='licence'),
    url(r'^userguide/$', 'home.views.userguide', name='userguide'),
)

urlpatterns += staticfiles_urlpatterns()

import os
urlpatterns += patterns('', (r'^media/(.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')}),)
