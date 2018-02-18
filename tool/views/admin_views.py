import secrets
import string

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from tool.forms.forms import *
from .views_utils import *


@login_required
def create_module(request):
    check_valid_user(request)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            # save as new module
            form.save()
            request.session['success_msg'] = 'Module %s saved' % form.cleaned_data['module_code']
            return redirect(reverse('tool:admin_create_module'), Permanent=True)
    else:
        form = ModuleForm()

    return render_form(request, 'tool/admin/create_module.html', form)


@login_required
def create_course(request):
    check_valid_user(request)

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            # save as new course
            form.save()
            request.session['success_msg'] = 'Course %s saved' % form.cleaned_data['course_code']
            return redirect(reverse('tool:admin_create_course'), Permanent=True)
    else:
        form = CourseForm()

    return render_form(request, 'tool/admin/create_course.html', form)


@login_required
def create_student(request):
    check_valid_user(request)

    if request.method == 'POST':
        user_form = StudentUserForm(request.POST)
        form = StudentForm(request.POST)
        if user_form.is_valid() and form.is_valid():
            # save as new user
            user = user_form.save(commit=False)
            random_password = User.objects.make_random_password(length=20)
            user.set_password(random_password)
            user.save()

            # save as new student - commit false so we can set user before actual save
            student = form.save(commit=False)
            student.user = user
            student.save()

            request.session['success_msg'] = 'Student %s saved' % user_form.cleaned_data['username']
            return redirect(reverse('tool:admin_create_student'), Permanent=True)
    else:
        user_form = StudentUserForm()
        form = StudentForm()

    return render_user_form(request, 'tool/admin/create_student.html', user_form, form)


@login_required
def create_staff(request):
    check_valid_user(request)

    if request.method == 'POST':
        # only user form - staff has no additional fields to be populated at this stage
        user_form = StaffUserForm(request.POST)
        if user_form.is_valid():
            # save as new user
            user = user_form.save(commit=False)
            random_password = User.objects.make_random_password(length=20)
            user.set_password(random_password)
            user.save()

            # save as new staff
            staff = Staff(user=user)
            staff.save()

            request.session['success_msg'] = 'Staff %s saved' % user_form.cleaned_data['username']
            return redirect(reverse('tool:admin_create_staff'), Permanent=True)
    else:
        user_form = StaffUserForm()

    return render_user_form(request, 'tool/admin/create_staff.html', user_form, None)


def check_valid_user(request):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    if not (user_type == UserType.STAFF_TYPE or user_type == UserType.ADMIN_TYPE):
        raise Http404("Not authorised to view this page")


def render_form(request, template_path, form):
    success_msg = request.session.pop('success_msg', '')
    return render(request, template_path, {
        'success_message': success_msg,
        'form': form
    })


def render_user_form(request, template_path, user_form, form):
    success_msg = request.session.pop('success_msg', '')
    return render(request, template_path, {
        'success_message': success_msg,
        'user_form': user_form,
        'form': form
    })
