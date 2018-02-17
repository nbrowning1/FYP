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

    upload_example_filepath = os.path.join(os.path.dirname(__file__), '..', 'download_resources', 'upload_example.xlsx')

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
                return redirect_to_home_with_error(request, "No module selected for upload #" + str(
                    error_index) + ". Please select a module from the list.")
            else:
                try:
                    code = module_str.split("code_")[1].split("crn_")[0].strip()
                    crn = module_str.split("crn_")[1].strip()
                except Exception:
                    return redirect_to_home_with_error(request,
                                                       "Invalid module selection for upload #" + str(
                                                           error_index) + ". Please select a module from the list.")

                try:
                    module = Module.objects.get(module_code=code, module_crn=crn)
                except Module.DoesNotExist:
                    return redirect_to_home_with_error(request, "Unrecognised module for upload #" + str(
                        error_index) + ". Please select a module from the list.")

            upload_file = request.FILES['upload-data-' + str(i)]
            comparison_name = upload_file.name.lower()
            is_csv_file = comparison_name.endswith('.csv')
            is_excel_file = comparison_name.endswith('.xls') or comparison_name.endswith('.xlsx')

            if not (is_csv_file or is_excel_file):
                return redirect_to_home_with_error(request, "Invalid file type for upload #" + str(
                    error_index) + ". Only csv, xls, xlsx files are accepted.")

            if is_csv_file:
                decoded_file = upload_file.read().decode('utf-8')
                file_str = io.StringIO(decoded_file)
                reader = csv.reader(file_str)
                uploaded_data = DataSaver().save_uploaded_data_csv(reader, module)
            else:
                contents = upload_file.read()
                uploaded_data = DataSaver().save_uploaded_data_excel(contents, module)

            if hasattr(uploaded_data, 'error'):
                error_msg = 'Error processing file ' + upload_file.name + ': ' + uploaded_data.error
                return redirect_with_error(request, reverse('tool:index'), error_msg)
            saved_data.append(uploaded_data)

        return render(request, 'tool/upload.html', {
            'uploaded_data': saved_data,
            'colours': ViewsUtils().get_pass_fail_colours_2_tone(request)
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
            response = HttpResponse(fh.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


@login_required
def settings(request):
    attendance_error_msg = request.session.pop('attendance_error', '')
    saved_settings = get_settings(request)
    if request.method == 'POST':
        if request.POST.get("accessibility-submit"):
            save_colourblind_settings(request, saved_settings)
        elif request.POST.get("attendance-submit"):
            error_msg = save_attendance_settings(request, saved_settings)
            if error_msg:
                return redirect_with_error_by_key(request, reverse('tool:settings'), 'attendance_error', error_msg)

        return redirect(reverse('tool:settings'), Permanent=True)
    return render(request, 'tool/settings.html', {
        'attendance_error_message': attendance_error_msg,
        'saved_settings': saved_settings
    })


def get_settings(request):
    try:
        return Settings.objects.get(user=request.user)
    except Settings.DoesNotExist:
        settings = Settings(user=request.user)
        settings.save()
        return settings


def save_colourblind_settings(request, saved_settings):
    colourblind_opts_set = False
    if request.POST.get("colourblind-opts"):
        colourblind_opts_set = True

    saved_settings.colourblind_opts_on = colourblind_opts_set
    saved_settings.save()


def save_attendance_settings(request, saved_settings):
    attendance_range_1 = request.POST.get("attendance-range-1")
    attendance_range_2 = request.POST.get("attendance-range-2")
    attendance_range_3 = request.POST.get("attendance-range-3")
    if not (attendance_range_1 and attendance_range_2 and attendance_range_3):
        return 'Attendance ranges must have a value'
    else:
        try:
            attendance_range_1 = int(attendance_range_1)
            attendance_range_2 = int(attendance_range_2)
            attendance_range_3 = int(attendance_range_3)
        except ValueError:
            return 'Attendance ranges must be whole numbers'

        if attendance_range_1 <= 0:
            return 'Attendance range 1 must be greater than 0'
        elif attendance_range_1 >= attendance_range_2:
            return 'Attendance range 2 must be greater than range 1'
        elif attendance_range_2 >= attendance_range_3:
            return 'Attendance range 3 must be greater than range 2'
        elif attendance_range_3 >= 100:
            return 'Attendance range 3 must be less than 100'
        else:
            saved_settings.attendance_range_1_cap = attendance_range_1
            saved_settings.attendance_range_2_cap = attendance_range_2
            saved_settings.attendance_range_3_cap = attendance_range_3
            saved_settings.save()
    return ''


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
    return redirect_with_error_by_key(request, redirect_url, 'error_message', error_msg)


# workaround to pass message through redirect
def redirect_with_error_by_key(request, redirect_url, error_key, error_msg):
    request.session[error_key] = error_msg
    return redirect(redirect_url, Permanent=True)


def logout_and_redirect_login(request):
    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
