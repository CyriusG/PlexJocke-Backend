from django.conf.urls import url


from .views import (
    ShowListAPIView,
    ShowCreateAPIView,
    ShowCheckSeasonsAvailability,
    ShowDetailAPIView,
    ShowDeleteAPIView
)


urlpatterns = [
    url(r'^$', ShowListAPIView.as_view(), name='list'),
    url(r'^create/$', ShowCreateAPIView.as_view(), name='create'),
    url(r'^check/(?P<pk>\d+)/$', ShowCheckSeasonsAvailability.as_view(), name='check'),
    url(r'^(?P<pk>\d+)/$', ShowDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/delete/$', ShowDeleteAPIView.as_view(), name='delete'),
]
