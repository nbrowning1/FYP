from django.conf.urls import url

from .views import views

from django.urls import reverse_lazy

from django.contrib.auth import views as auth_views

app_name = 'tool'
urlpatterns = [
  # ex: /tool/
  url(r'^$', views.index, name='index'),
  
  # ex: /tool/upload/
  url(r'^upload/$', views.upload, name='upload'),
  
  url(r'^login/$', auth_views.LoginView.as_view(template_name='tool/login.html', redirect_authenticated_user=True), name='login'),
  
  url(r'^logout/$', auth_views.logout_then_login, name='logout'),
  
  # reverse_lazy call needed for password_change_done because of line here:
  # https://github.com/django/django/blob/6e40b70bf4c6e475266a9f011269c50f29f0f14e/django/contrib/auth/views.py#L334
  # reverse_lazy performed in the view doesn't supply the app namespace
  url(r'^password-change/$', auth_views.PasswordChangeView.as_view(template_name='tool/password_change.html', success_url=reverse_lazy('tool:password_change_done')), name='password_change'),
  
  url(r'^password-change-done/$', auth_views.PasswordChangeDoneView.as_view(template_name='tool/password_change_done.html'), name='password_change_done'),
  
  url(r'^password-reset/$', auth_views.PasswordResetView.as_view(template_name='tool/password_reset.html', success_url=reverse_lazy('tool:password_reset_done')), name='password_reset'),
  
  url(r'^password-reset-done/$', auth_views.PasswordResetDoneView.as_view(template_name='tool/password_reset_done.html'), name='password_reset_done'),
  
  url(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(template_name='tool/password_reset_confirm.html', success_url=reverse_lazy('tool:password_reset_complete')), name='password_reset_confirm'),
  
  url(r'password-reset-complete/$', auth_views.PasswordResetCompleteView.as_view(template_name='tool/password_reset_complete.html'), name='password_reset_complete'),
  
  url(r'^settings/$', views.settings, name='settings'),
]
