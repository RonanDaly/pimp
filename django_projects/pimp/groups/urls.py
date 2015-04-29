from django.conf.urls.defaults import *

urlpatterns = patterns('',
#urlpatterns = patterns('dynamicform.views',
    (r'^$', 'groups.views.index', 'add_group'),
    (r'^$', 'groups.views.assignfile', 'submit'),
    #(r'thanks$', 'django.views.generic.simple.direct_to_template', {'template': 'todo/thanks.html'}),
)
