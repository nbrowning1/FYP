import csv
import io
import os
import types
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from .views_utils import *
from ..models import *
from ..upload_data_save import DataSaver


@login_required
def index(request):
    error_msg = request.session.pop('error_message', '')

    if request.user.is_staff:
        modules = Module.objects.all()
        courses = Course.objects.all()
        lecturers = Staff.objects.all()
        students = Student.objects.all()
        lectures = Lecture.objects.all()
        user_type = UserType.ADMIN_TYPE.value
    else:
        is_valid_user = False

        # if lecturer exists, it's a lecturer
        try:
            lecturer = Staff.objects.get(user=request.user)

            modules = lecturer.modules.all()
            courses = lecturer.courses.all()
            lecturers = []
            students = []
            # TODO: add students from courses
            for module in modules:
                for student in module.students.all():
                    students.append(student)
            students = list(OrderedDict.fromkeys(students))
            lectures = Lecture.objects.filter(module__in=modules)

            is_valid_user = True
            user_type = UserType.STAFF_TYPE.value
        except Staff.DoesNotExist:
            pass

        # otherwise try student
        try:
            student = Student.objects.get(user=request.user)

            modules = Module.objects.filter(students__id__exact=student.id)
            courses = []
            lecturers = []
            students = []
            lectures = Lecture.objects.filter(module__in=modules)
            is_valid_user = True

            user_type = UserType.STUDENT_TYPE.value
        except Student.DoesNotExist:
            pass

        # if we made it this far, user is invalid - log user out
        if not is_valid_user:
            return logout_and_redirect_login(request)

    upload_example_filepath = os.path.join(os.path.dirname(__file__), '..', 'download_resources', 'upload_example.csv')

    return render(request, 'tool/index.html', {
        'error_message': error_msg,
        'modules': modules,
        'courses': courses,
        'lecturers': lecturers,
        'students': students,
        'lectures': lectures,
        'user_type': user_type,
        'upload_example_filepath': upload_example_filepath
    })


@login_required
def upload(request):
    if not request.user.is_staff:
        raise PermissionDenied("Insufficient permissions")

    if request.method == 'POST':
        number_of_uploads = 0
        # figure out how many uploads from number of files
        while request.FILES.getlist('upload-data-' + str(number_of_uploads)):
            number_of_uploads += 1

        if number_of_uploads == 0:
            return redirect_to_home_with_error(request, "No file uploaded. Please upload a .csv file.")

        saved_data = []
        for i in range(number_of_uploads):
            # for error messages. #1 makes more sense than #0
            error_index = i + 1
            module = None
            module_str = request.POST.get("module-" + str(i))
            if not module_str:
                return redirect_to_home_with_error(request, "No module selected for upload #" + str(error_index) + ". Please select a module from the list.")
            else:
                try:
                    code = module_str.split("code_")[1].split("crn_")[0].strip()
                    crn = module_str.split("crn_")[1].strip()
                except Exception:
                    return redirect_to_home_with_error(request,
                                                       "Invalid module selection for upload #" + str(error_index) + ". Please select a module from the list.")

                try:
                    module = Module.objects.get(module_code=code, module_crn=crn)
                except Module.DoesNotExist:
                    return redirect_to_home_with_error(request, "Unrecognised module for upload #" + str(error_index) + ". Please select a module from the list.")

            csv_file = request.FILES['upload-data-' + str(i)]
            if not (csv_file.name.lower().endswith('.csv')):
                return redirect_to_home_with_error(request, "Invalid file type for upload #" + str(error_index) + ". Only csv files are accepted.")

            decoded_file = csv_file.read().decode('utf-8')
            file_str = io.StringIO(decoded_file)

            reader = csv.reader(file_str)
            uploaded_data = DataSaver(reader).save_uploaded_data(module)
            if hasattr(uploaded_data, 'error'):
                error_msg = 'Error processing file ' + csv_file.name + ': ' + uploaded_data.error
                return redirect_with_error(request, reverse('tool:index'), error_msg)
            saved_data.append(uploaded_data)

        return render(request, 'tool/upload.html', {
            'uploaded_data': saved_data,
        })
    else:
        return HttpResponseRedirect(reverse('tool:index'))


def redirect_to_home_with_error(request, error_msg):
    # workaround to pass message through redirect
    request.session['error_message'] = error_msg
    return redirect(reverse('tool:index'), Permanent=True)


@login_required
def download(request, path):
    if not request.user.is_staff:
        raise PermissionDenied("Insufficient permissions")

    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


@login_required
def settings(request):
    return render(request, 'tool/settings.html')


@login_required
def module_course_view_settings(request):
    # only works for lecturers to configure which modules / courses they see
    try:
        lecturer = Staff.objects.get(user=request.user)

        # create list of all modules with lecturer-displayed ones listed first
        all_modules = list(Module.objects.all())
        lecturer_modules = lecturer.modules.all()
        modules = []
        for module in lecturer_modules:
            data_module = types.SimpleNamespace()
            data_module.module = module
            data_module.displayed = True
            modules.append(data_module)
            all_modules.remove(module)
        for module in all_modules:
            data_module = types.SimpleNamespace()
            data_module.module = module
            data_module.displayed = False
            modules.append(data_module)

        # same for courses
        all_courses = list(Course.objects.all())
        lecturer_courses = lecturer.courses.all()
        courses = []
        for course in lecturer_courses:
            data_course = types.SimpleNamespace()
            data_course.course = course
            data_course.displayed = True
            all_courses.remove(course)
            courses.append(data_course)
        for course in all_courses:
            data_course = types.SimpleNamespace()
            data_course.course = course
            data_course.displayed = False
            courses.append(data_course)

        return render(request, 'tool/module_course_view_settings.html', {
            'modules': modules,
            'courses': courses
        })
    except Staff.DoesNotExist:
        raise Http404


@login_required
def save_module_course_settings(request):
    # only works for lecturers to configure which modules / courses they see
    try:
        lecturer = Staff.objects.get(user=request.user)

        if request.method == 'POST':
            # clear down values to re-populate with data from form
            lecturer.modules.set([])
            lecturer.courses.set([])

            module_checkbox_vals = request.POST.getlist('modules[]')
            course_checkbox_vals = request.POST.getlist('courses[]')

            # save checked modules to lecturer
            for val in module_checkbox_vals:
                code = val.split("code_")[1].split("crn_")[0].strip()
                crn = val.split("crn_")[1].strip()

                try:
                    module = Module.objects.get(module_code=code, module_crn=crn)
                    lecturer.modules.add(module)
                except Module.DoesNotExist:
                    print("Could not find module with code: " + code + " crn: " + crn)

            # save checked courses to lecturer
            for val in course_checkbox_vals:
                code = val.split("code_")[1].strip()

                try:
                    course = Course.objects.get(course_code=code)
                    lecturer.courses.add(course)
                except Course.DoesNotExist:
                    print("Could not find course with code: " + code)

        return redirect(reverse('tool:index'), Permanent=True)
    except Staff.DoesNotExist:
        raise Http404


# workaround to pass message through redirect
def redirect_with_error(request, redirect_url, error_msg):
    request.session['error_message'] = error_msg
    return redirect(redirect_url, Permanent=True)


def logout_and_redirect_login(request):
    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
