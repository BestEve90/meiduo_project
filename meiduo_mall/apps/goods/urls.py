from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page>\d+)/$', views.ListView.as_view(), name='index'),
    url(r'^hot/(?P<category_id>\d+)/$', views.HotView.as_view(), name='index'),

]