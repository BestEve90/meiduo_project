from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^carts/$', views.CartsView.as_view(), name='index'),
    url(r'^carts/selection/$', views.CartsSelectionView.as_view(), name='index'),

]