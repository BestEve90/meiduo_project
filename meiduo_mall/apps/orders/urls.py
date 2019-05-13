from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^orders/settlement/$',views.PlaceOrderView.as_view(),name='register'),

]