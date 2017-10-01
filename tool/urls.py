from django.conf.urls import url

from . import views

app_name = 'tool'
urlpatterns = [
  # ex: /tool/
  url(r'^$', views.IndexView.as_view(), name='index'),
  # ex: /tool/upload/
  url(r'^upload$', views.upload, name='upload')
]
