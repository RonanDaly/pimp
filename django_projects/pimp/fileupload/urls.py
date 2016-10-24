########################## Deprecated version ########################
# from django.conf.urls.defaults import *
########################## End deprecated version ########################

from django.conf.urls import *
from fileupload.views import PictureCreateView, PictureDeleteView, ProjfileCreateView, ProjfileDeleteView, FragfileCreateView, FragfileDeleteView

urlpatterns = patterns('',
    (r'^new/$', PictureCreateView.as_view(template_name="fileupload/file_upload_form.html"), {}, 'upload-new'),
    (r'^new/projectfile/$', ProjfileCreateView.as_view(template_name="fileupload/projfile_upload_form.html"), {}, 'upload-new-projFile'),
    (r'^new/fragmentfile/$', FragfileCreateView.as_view(template_name="fileupload/frag_upload_form.html"), {},'upload-new-fragFile'),

    (r'^delete/(?P<pk>\d+)$', PictureDeleteView.as_view(), {}, 'upload-delete'),
    (r'^deleteprojectfile/(?P<pk>\d+)$', ProjfileDeleteView.as_view(), {}, 'upload-projfile-delete'),
    (r'^deletefragmentfile/(?P<pk>\d+)$', FragfileDeleteView.as_view(), {}, 'upload-fragFile-delete'))


