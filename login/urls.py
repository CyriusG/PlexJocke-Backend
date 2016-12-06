from django.conf.urls import url
from . import views

# These are url:s that are used for django administration (Back-End)
# Known as url routing
# Caret ^ = Start of url
# Dollar sign $ = End of url
# If no url is matched, user is prompted with a 404 not found
urlpatterns = [
    url(r'^$', views.authentication, name='authentication'),
    url(r'^test/', views.test, name='test'),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout, name='logout'),
]
