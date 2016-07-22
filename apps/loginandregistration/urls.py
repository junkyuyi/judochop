from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.register, name='register'),
    url(r'^signin$', views.signin, name='signin'),
    url(r'^travels$', views.travels, name='travels'),
    url(r'^travels/destination/(?P<id>\d+)$', views.destination, name='destination'),
    url(r'^travels/add$', views.add, name='add'),
    url(r'^travels/join/(?P<id>\d+)$', views.join, name='join'),
    url(r'^logoff$', views.logoff, name='logoff')
]