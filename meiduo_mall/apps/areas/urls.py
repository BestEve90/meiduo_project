from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^addresses/$', views.AdressesView.as_view(), name='index'),
    url(r'^areas/$', views.AreaView.as_view(), name='index'),

]