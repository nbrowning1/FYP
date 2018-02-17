from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from tool.forms.forms import ModuleForm

from .views_utils import *
from ..models import *

@login_required
def create_module(request):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    if not (user_type == UserType.STAFF_TYPE or user_type == UserType.ADMIN_TYPE):
        raise Http404("Not authorised to view this page")

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            # save as new module
            form.save()
            request.session['success_msg'] = 'Module %s saved' % form.cleaned_data['module_code']
            return redirect(reverse('tool:admin_create_module'), Permanent=True)
    else:
        form = ModuleForm()

    success_msg = request.session.pop('success_msg', '')
    return render(request, 'tool/admin/create_module.html', {
        'success_message': success_msg,
        'form': form
    })