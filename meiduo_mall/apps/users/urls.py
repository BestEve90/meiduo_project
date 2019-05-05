from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view(),name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',
        views.UserCheckView.as_view()),
    url(r'^mobiles/(?P<phonenum>1[345789]\d{9})/count/$',
        views.PhoneCheckView.as_view()),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^info/$', views.InfoView.as_view(), name='logout'),
    url(r'^emails/$', views.EmailView.as_view(), name='message_identify'),
    url(r'^emails/verification/$', views.EmailVerifyView.as_view(), name='message_identify'),
    url(r'^addresses/$', views.AdressesView.as_view(), name='index'),
    url(r'^addresses/create/$', views.AdressesCreateView.as_view(), name='index'),

]