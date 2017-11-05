from django.conf.urls import url

from .views import views

from django.contrib.auth import views as auth_views

app_name = 'tool'
urlpatterns = [
  # ex: /tool/
  url(r'^$', views.index, name='index'),
  # ex: /tool/upload/
  url(r'^upload/$', views.upload, name='upload'),
  # ex: /tool/login/
  url(r'^login/$', auth_views.LoginView.as_view(template_name='tool/login.html'), name='login'),
  # ex: /tool/logout/
  url(r'^logout/$', auth_views.logout_then_login, name='logout'),
]
