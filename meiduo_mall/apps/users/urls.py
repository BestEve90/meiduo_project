from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',
        views.UserCheckView.as_view()),
    url(r'^mobiles/(?P<phonenum>1[345789]\d{9})/count/$',
        views.PhoneCheckView.as_view()),
    url(r'^login/$', views.LoginView.as_view(), name='register'),

]