from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/login/$',views.OauthURLView.as_view(),name='register'),
    url(r'^oauth_callback$', views.OauthCallBackView.as_view(), name='register'),

]