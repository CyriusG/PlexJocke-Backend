from django.conf.urls import url

from .views import (
    MovieCreateAPIView,
    MovieDeleteAPIView,
    MovieDetailAPIView,
    MovieListAPIView,
    )


urlpatterns = [
    url(r'^$', MovieListAPIView.as_view(), name='list'),
    url(r'^create/$', MovieCreateAPIView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', MovieDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/delete/$', MovieDeleteAPIView.as_view(), name='delete'),
]