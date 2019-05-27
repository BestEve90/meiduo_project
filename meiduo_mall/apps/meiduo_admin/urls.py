from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistics_view, users_view, goods_view
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('skus', goods_view.SKUView, base_name='sku')

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', statistics_view.UerTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistics_view.DailyUerIncrementView.as_view()),
    url(r'^statistical/day_active/$', statistics_view.DailyActiveUserView.as_view()),
    url(r'^statistical/day_orders/$', statistics_view.DailyOrdersUserView.as_view()),
    url(r'^statistical/month_increment/$', statistics_view.MonthUserIncrementView.as_view()),
    url(r'^statistical/goods_day_views/$', statistics_view.DailyCategoryVisitView.as_view()),
    url(r'^users/$', users_view.UsersView.as_view()),
    # url(r'^skus/$', goods_view.SKUView.as_view({'get': 'list', 'post': 'create'})),
    # url(r'^skus/(?P<pk>\d+)/$', goods_view.SKUView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    url(r'^', include(router.urls)),
    url(r'^skus/categories/$', goods_view.SKUCategoryView.as_view()),
    url(r'^goods/simple/$', goods_view.SPUNameView.as_view()),
    url(r'^goods/(?P<pk>\d+)/specs/$', goods_view.SPUSpecsView.as_view()),
]
