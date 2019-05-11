from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^list/(?P<category_id>\d+)/(?P<page>\d+)/$', views.ListView.as_view(), name='index'),
    url(r'^hot/(?P<category_id>\d+)/$', views.HotView.as_view(), name='hot'),
    url(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.VisitCountView.as_view(), name='visitcount'),
    url(r'^browse_histories/$', views.HistoryView.as_view(), name='history'),

]