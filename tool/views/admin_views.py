from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from tool.forms.forms import *
from .views_utils import *

"""
Admin views for the creation of entities e.g. modules, courses.
These views should always have a @login_required decorator and a call to check_valid_user()
to ensure that the user type == Staff.
"""


@login_required
def create_module(request):
    return create_regular_entity(request, ModuleForm, 'Module', 'module_code', 'admin_create_module', 'create_module')


@login_required
def create_course(request):
    return create_regular_entity(request, CourseForm, 'Course', 'course_code', 'admin_create_course', 'create_course')


@login_required
def create_student(request):
    check_valid_user(request)

    if request.method == 'POST':
        user_form = StudentUserForm(request.POST)
        form = StudentForm(request.POST)
        if user_form.is_valid() and form.is_valid():
            # Save as new user
            user = user_form.save(commit=False)
            random_password = EncryptedUser.objects.make_random_password(length=20)
            user.set_password(random_password)
            user.save()

            # Save as new student - commit false so we can set user before actual save
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
        # Only user form - staff has no additional fields to be populated at this stage
        user_form = StaffUserForm(request.POST)
        if user_form.is_valid():
            # Save as new user
            user = user_form.save(commit=False)
            random_password = EncryptedUser.objects.make_random_password(length=20)
            user.set_password(random_password)
            user.save()

            # Save as new staff
            staff = Staff(user=user)
            staff.save()

            request.session['success_msg'] = 'Staff %s saved' % user_form.cleaned_data['username']
            return redirect(reverse('tool:admin_create_staff'), Permanent=True)
    else:
        user_form = StaffUserForm()

    return render_user_form(request, 'tool/admin/create_staff.html', user_form, None)


def create_regular_entity(request, form_type, entity_str, creation_indicator, view_redirect_str, template_str):
    """Creates a regular entity.

    :param request: HTTP request to get context from
    :param form_type: type of form to check and save model based on
    :param entity_str: type of entity to be saved as string, for message output e.g. 'Module'
    :param creation_indicator: field key to grab from form, for message output when saving
    :param view_redirect_str: view to redirect to as string after successful submit
    :param template_str: template to use to render form as string, from tool/admin/
    :return: HTTP response with fresh form, redirect etc. depending on context
    """

    check_valid_user(request)

    # If POST (submission), validate form and save if successful, otherwise create fresh form
    if request.method == 'POST':
        form = form_type(request.POST)
        if form.is_valid():
            # Save as new entity
            form.save()
            request.session['success_msg'] = '%s %s saved' % (entity_str, form.cleaned_data[creation_indicator])
            return redirect(reverse('tool:' + view_redirect_str), Permanent=True)
    else:
        form = form_type()

    return render_form(request, 'tool/admin/' + template_str + '.html', form)


def check_valid_user(request):
    """Check user is valid - in this case (because these are admin views) - checking whether user is Staff.

    :param request: HTTP request to check authenticated user from
    :return: whether user is valid and is a staff member, or throw 404
    """
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    if not (user_type == UserType.STAFF_TYPE):
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
