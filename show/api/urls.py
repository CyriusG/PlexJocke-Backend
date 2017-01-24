from django.conf.urls import url


from .views import (
    ShowListAPIView,
    ShowCreateAPIView,
    ShowSearchAPIView,
    ShowDetailAPIView,
    ShowDeleteAPIView
)


urlpatterns = [
    url(r'^$', ShowListAPIView.as_view(), name='list'),
    url(r'^create/$', ShowCreateAPIView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', ShowDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/delete/$', ShowDeleteAPIView.as_view(), name='delete'),
]
