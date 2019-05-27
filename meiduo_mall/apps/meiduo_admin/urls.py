from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistics_view, users_view, goods_view
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('goods/specs', goods_view.GoodSpecsView, base_name='specs')
router.register('skus', goods_view.SKUView, base_name='sku')
router.register('goods', goods_view.SPUView, base_name='spu')
router.register('specs/options', goods_view.OptionsView, base_name='spu')
print(router.urls)

urlpatterns = [
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^statistical/total_count/$', statistics_view.UerTotalCountView.as_view()),
    url(r'^statistical/day_increment/$', statistics_view.DailyUerIncrementView.as_view()),
    url(r'^statistical/day_active/$', statistics_view.DailyActiveUserView.as_view()),
    url(r'^statistical/day_orders/$', statistics_view.DailyOrdersUserView.as_view()),
    url(r'^statistical/month_increment/$', statistics_view.MonthUserIncrementView.as_view()),
    url(r'^statistical/goods_day_views/$', statistics_view.DailyCategoryVisitView.as_view()),
    url(r'^users/$', users_view.UsersView.as_view()),
    url(r'^skus/categories/$', goods_view.SKUCategoryView.as_view()),
    url(r'^goods/simple/$', goods_view.SPUNameView.as_view()),
    url(r'^goods/(?P<pk>\d+)/specs/$', goods_view.SPUSpecsView.as_view()),
    url(r'^goods/brands/simple/$', goods_view.BrandView.as_view()),
    url(r'^goods/channel/categories/$', goods_view.ChannelView.as_view()),
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', goods_view.SPUView.as_view({'get': 'get_sub_cats'})),
    url(r'^goods/specs/simple/$', goods_view.SpecsSimpleView.as_view()),
    url(r'^', include(router.urls)),

]
