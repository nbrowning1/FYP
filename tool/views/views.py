import csv
import io
import json
import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from tool.utils import Utils
from .views_utils import *
from ..models import *
from ..upload_data_save import DataSaver

"""
General views in the system.
These views should always have a @login_required decorator and a call to ViewsUtils.check_valid_user()
to ensure that the user type is recognised.
"""


@login_required
def index(request):
    # Get an error message attached to the request if it exists
    error_msg = request.session.pop('error_message', '')

    is_valid_user = False

    # Get user type while grabbing entities related to that user type
    # Try staff first
    try:
        lecturer = Staff.objects.get(user=request.user)

        # Get modules and courses linked to this staff member
        modules = lecturer.modules.all()
        courses = lecturer.courses.all()
        lecturers = Staff.objects.all()
        students = []

        for module in modules:
            for student in module.students.all():
                students.append(student)
        students = list(OrderedDict.fromkeys(students))
        lectures = Lecture.objects.filter(module__in=modules)

        is_valid_user = True
        user_type = UserType.STAFF_TYPE.value
    except Staff.DoesNotExist:
        pass

    if not is_valid_user:
        # Try student next
        try:
            student = Student.objects.get(user=request.user)

            attendances = StudentAttendance.objects.filter(student=student)
            lectures = []
            for attendance in attendances:
                lectures.append(attendance.lecture)
            modules = []
            for lecture in lectures:
                if lecture.module not in modules:
                    modules.append(lecture.module)
            courses = []
            lecturers = []
            students = []

            is_valid_user = True
            user_type = UserType.STUDENT_TYPE.value
        except Student.DoesNotExist:
            pass

    if not is_valid_user:
        return logout_and_redirect_login(request)

    # Get example download resource path
    upload_example_filepath = os.path.join(os.path.dirname(__file__), '..', 'download_resources', 'upload_example.xlsx')

    # Representing the objects as lists that can be serialised to JSON for JS usage
    # Passed to client-side for pagination use in JS
    modulesjs = [{'url': reverse('tool:module', kwargs={'module_id': m.id}),
                  'code': m.module_code,
                  'crn': m.module_crn}
                 for m in modules]

    coursesjs = [{'url': reverse('tool:course', kwargs={'course_id': c.id}),
                  'name': c.course_code}
                 for c in courses]

    lecturersjs = [{'url': reverse('tool:lecturer', kwargs={'lecturer_id': l.id}),
                    'name': l.user.username}
                   for l in lecturers]

    studentsjs = [{'url': reverse('tool:student', kwargs={'student_id': s.id}),
                   'name': s.user.username}
                  for s in students]

    lecturesjs = [{'url': reverse('tool:lecture', kwargs={'lecture_id': l.id}),
                   'module_code': l.module.module_code,
                   'session_id': l.session_id,
                   'date': Utils.get_template_formatted_date(l.date)}
                  for l in lectures]

    return render(request, 'tool/index.html', {
        'error_message': error_msg,
        'modules': modules,
        'modulesjs': modulesjs,
        'courses': courses,
        'coursesjs': coursesjs,
        'lecturers': lecturers,
        'lecturersjs': lecturersjs,
        'students': students,
        'studentsjs': studentsjs,
        'lectures': lectures,
        'lecturesjs': lecturesjs,
        'user_type': user_type,
        'upload_example_filepath': upload_example_filepath
    })


@login_required
def upload(request):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    # Only allow staff users to upload attendance data
    if not (user_type == UserType.STAFF_TYPE):
        raise PermissionDenied("Insufficient permissions")

    # Should only be POSTing to this, if receiving anything else, just redirect
    if request.method == 'POST':
        return handle_upload(request)
    else:
        return HttpResponseRedirect(reverse('tool:index'))


def handle_upload(request):
    """Attempt to save attendance data from request. If failure, return as JSON response.
    If success, return content to be displayed inline on the page.

    :param request: HTTP request including file data to try saving
    :return: JSON failure response or HTML content to place in page
    """

    number_of_uploads = 0

    # Figure out how many uploads from number of files
    while request.FILES.getlist('upload-data-' + str(number_of_uploads)):
        number_of_uploads += 1

    if number_of_uploads == 0:
        return json_failure_response("No file uploaded. Please upload a .csv, .xls, or .xlsx file.")

    saved_data = []
    for i in range(number_of_uploads):
        # For error messages. #1 makes more sense than #0
        error_index = i + 1
        module = None

        # Check module is selected
        module_str = request.POST.get("module-" + str(i))
        if not module_str:
            return json_failure_response("No module selected for upload #" + str(
                error_index) + ". Please select a module from the list.")
        else:
            # Parse module code and CRN from string passed in request
            try:
                code = module_str.split("code_")[1].split("crn_")[0].strip()
                crn = module_str.split("crn_")[1].strip()
            except Exception:
                return json_failure_response("Invalid module selection for upload #" + str(
                    error_index) + ". Please select a module from the list.")

            # Validate that module actually exists
            try:
                module = Module.objects.get(module_code=code, module_crn=crn)
            except Module.DoesNotExist:
                return json_failure_response("Unrecognised module for upload #" + str(
                    error_index) + ". Please select a module from the list.")

        upload_file = request.FILES['upload-data-' + str(i)]
        # Change to lowercase for comparison on file extensions
        comparison_name = upload_file.name.lower()
        is_csv_file = comparison_name.endswith('.csv')
        is_excel_file = comparison_name.endswith('.xls') or comparison_name.endswith('.xlsx')

        # Validate on supported file extensions
        if not (is_csv_file or is_excel_file):
            return json_failure_response("Invalid file type for upload #" + str(
                error_index) + ". Only csv, xls, xlsx files are accepted.")

        # Parse file as CSV or xls/xlsx and attempt to save
        if is_csv_file:
            decoded_file = upload_file.read().decode('utf-8')
            file_str = io.StringIO(decoded_file)
            reader = csv.reader(file_str)
            uploaded_data = DataSaver.save_uploaded_data_csv(reader, module)
        else:
            contents = upload_file.read()
            uploaded_data = DataSaver.save_uploaded_data_excel(contents, module)

        # Final error check to see if anything went wrong while parsing the data
        if hasattr(uploaded_data, 'error'):
            error_msg = 'Error processing file ' + upload_file.name + ': ' + uploaded_data.error
            return json_failure_response(error_msg)
        saved_data.append(uploaded_data)

    return render(request, 'tool/upload/upload.html', {
        'uploaded_data': saved_data,
        'colours': ViewsUtils().get_pass_fail_colours_2_tone(request)
    })


def json_failure_response(error_msg):
    """Return JSON response in format { failure: 'error_msg' }
    Used for views called in AJAX requests to give indication as to what went wrong on failure

    :param error_msg: error message to return to reveal what went wrong
    :return: JSON response to indicate failure
    """

    json_str = {"failure": error_msg}
    return HttpResponse(json.dumps(json_str), content_type='application/json')


@login_required
def download(request, path):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    # Only allow staff to download example attendance upload resource
    if not (user_type == UserType.STAFF_TYPE):
        raise PermissionDenied("Insufficient permissions")

    if os.path.exists(path):
        with open(path, 'rb') as file:
            # Return in content type to allow xls/xlsx download
            response = HttpResponse(file.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


@login_required
def settings(request):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    # Fetch error to do with attendance from the request if present
    attendance_error_msg = request.session.pop('attendance_error', '')
    saved_settings = get_settings(request)

    # If POST, submit new settings as applicable
    if request.method == 'POST':
        if request.POST.get("accessibility-submit"):
            save_colourblind_settings(request, saved_settings)
        elif request.POST.get("attendance-submit"):
            error_msg = save_attendance_settings(request, saved_settings)
            if error_msg:
                return redirect_with_error_by_key(request, reverse('tool:settings'), 'attendance_error', error_msg)

        return redirect(reverse('tool:settings'), Permanent=True)

    return render(request, 'tool/settings/settings.html', {
        'user_type': user_type.value,
        'attendance_error_message': attendance_error_msg,
        'saved_settings': saved_settings
    })


def get_settings(request):
    """Get settings for current user if exists, or create default settings for user and return this.

    :param request: HTTP request to get currently-authenticated user from
    :return: existing or new default settings for user
    """

    try:
        return Settings.objects.get(user=request.user)
    except Settings.DoesNotExist:
        settings = Settings(user=request.user)
        settings.save()
        return settings


def save_colourblind_settings(request, saved_settings):
    """Save new colourblind settings for user

    :param request: HTTP request to get POST data from for new settings
    :param saved_settings: existing settings to update
    """

    # Set as false unless POST data indicates otherwise
    # POST data will not indicate the absence of this information, so we must default to false
    colourblind_opts_set = False
    if request.POST.get("colourblind-opts"):
        colourblind_opts_set = True

    saved_settings.colourblind_opts_on = colourblind_opts_set
    saved_settings.save()


def save_attendance_settings(request, saved_settings):
    """Save new attendance settings for user

    :param request: HTTP request to get POST data from for new settings
    :param saved_settings: existing settings to update
    :return: error message if there are any validation failures, otherwise empty string
    """

    attendance_range_1 = request.POST.get("attendance-range-1")
    attendance_range_2 = request.POST.get("attendance-range-2")
    attendance_range_3 = request.POST.get("attendance-range-3")

    # Validate presence of attendance range values
    if not (attendance_range_1 and attendance_range_2 and attendance_range_3):
        return 'Attendance ranges must have a value'
    else:
        # Validate ranges are whole numbers
        try:
            attendance_range_1 = int(attendance_range_1)
            attendance_range_2 = int(attendance_range_2)
            attendance_range_3 = int(attendance_range_3)
        except ValueError:
            return 'Attendance ranges must be whole numbers'

        # Validate that ranges are in correct range and follow range 1 < range 2 < range 3
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
    # Only works for lecturers to configure which modules / courses they see
    try:
        lecturer = Staff.objects.get(user=request.user)

        # Get all modules in system and modules linked to staff member
        all_modules = list(Module.objects.all())
        lecturer_modules = lecturer.modules.all()
        modules = []

        # Create list of all modules with lecturer-displayed ones listed first
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

        # Same as above for courses
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

        return render(request, 'tool/settings/module_course_view_settings.html', {
            'modules': modules,
            'courses': courses
        })
    except Staff.DoesNotExist:
        raise Http404


@login_required
def save_module_course_settings(request):
    # Only works for lecturers to configure which modules / courses they see
    try:
        lecturer = Staff.objects.get(user=request.user)

        # This view should only be POSTed to
        if request.method == 'POST':
            # Clear down values to re-populate with data from form
            lecturer.modules.set([])
            lecturer.courses.set([])

            # Get checked modules and courses (ones that the staff wants to save as visible)
            module_checkbox_vals = request.POST.getlist('modules[]')
            course_checkbox_vals = request.POST.getlist('courses[]')

            try:
                # Save checked modules to lecturer
                for val in module_checkbox_vals:
                    code = val.split("code_")[1].split("crn_")[0].strip()
                    crn = val.split("crn_")[1].strip()

                    try:
                        module = Module.objects.get(module_code=code, module_crn=crn)
                        lecturer.modules.add(module)
                    except Module.DoesNotExist:
                        print("Could not find module with code: " + code + " crn: " + crn)

                # Save checked courses to lecturer
                for val in course_checkbox_vals:
                    code = val.split("code_")[1].strip()

                    try:
                        course = Course.objects.get(course_code=code)
                        lecturer.courses.add(course)
                    except Course.DoesNotExist:
                        print("Could not find course with code: " + code)
            except Exception as e:
                print("Something went wrong. Exception: " + str(e))

        return redirect(reverse('tool:index'), Permanent=True)
    except Staff.DoesNotExist:
        raise Http404


def redirect_with_error_by_key(request, redirect_url, error_key, error_msg):
    """Workaround to pass message through redirect - place in session to pop later

    :param request: HTTP request to attach message to its session
    :param redirect_url: URL to redirect to
    :param error_key: error key to attach error message to in the session
    :param error_msg: error message to pass through redirect
    :return: HTTP redirection to redirect_url
    """

    request.session[error_key] = error_msg
    return redirect(redirect_url, Permanent=True)


def logout_and_redirect_login(request):
    """Log out of authenticated user and redirect to login page

    :param request: HTTP request to get authenticated user from to log out
    :return: HTTP redirect to login
    """

    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
