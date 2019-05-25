from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistics_view

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', statistics_view.UerTotalCountView.as_view()),
]