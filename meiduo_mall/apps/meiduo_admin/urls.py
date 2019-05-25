from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistics_view

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', statistics_view.UerTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistics_view.DailyUerIncrementView.as_view()),
    url(r'^statistical/day_active/$', statistics_view.DailyActiveUserView.as_view()),
    url(r'^statistical/day_orders/$', statistics_view.DailyOrdersUserView.as_view()),
]