from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from survey import views
import settings

admin.autodiscover()
media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')

urlpatterns = patterns('',
                       # Examples:
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^home/$', views.index, name='home'),
                       url(r'^survey/(?P<survey_id>\d+)/$', views.survey_detail, name='survey_detail'),
                       url(r'^confirm/(?P<uuid>\w+)/$', views.confirm, name='confirmation'),
                       url(r'^login/$', views.user_login, name='login'),
                       url(r'^register/$', views.register, name='register'),
                       url(r'^logout/$', views.user_logout, name='logout'),
                       url(r'^survey_list/$', views.survey_list, name='survey_list'),
                       )

# media url hackery. le sigh. 
urlpatterns += patterns('',
                        (r'^%s/(?P<path>.*)$' % media_url, 'django.views.static.serve',
                         {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
                        )
