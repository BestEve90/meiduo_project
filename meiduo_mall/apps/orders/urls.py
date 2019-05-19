from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/settlement/$', views.PlaceOrderView.as_view(), name='to_settle'),
    url(r'^orders/commit/$', views.OrderCommitView.as_view(), name='order_commit'),
    url(r'^orders/success/$', views.OrderSuccessView.as_view(), name='order_success'),
    url(r'^orders/info/(?P<page_num>\d+)/$', views.OrderDisplayView.as_view(), name='order_info'),
    url(r'^orders/comment/$', views.OrderCommentView.as_view(), name='order_comment'),
    url(r'^comment/(?P<sku_id>\d+)/$', views.CommentListView.as_view(), name='comment_list'),

]
