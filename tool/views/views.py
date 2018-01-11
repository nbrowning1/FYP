import csv
import io
import types
from collections import OrderedDict

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from graphos.renderers.gchart import LineChart, PieChart
from graphos.sources.simple import SimpleDataSource

from ..data_rows import ModuleRow, StaffRow, AttendanceSessionRow, AttendanceRow
from ..models import Student, Staff, Module, Lecture, StudentAttendance

ADMIN_TYPE = "ADMIN"
STAFF_TYPE = "STAFF"
STUDENT_TYPE = "STUDENT"
VALID_TYPES = [ADMIN_TYPE, STAFF_TYPE, STUDENT_TYPE]


@login_required
def index(request):
    error_msg = request.session.pop('error_message', '')

    if request.user.is_staff:
        modules = Module.objects.all()
        lecturers = Staff.objects.all()
        students = Student.objects.all()
        lectures = Lecture.objects.all()
        user_type = 'ADMIN'
    else:
        is_valid_user = False

        # if lecturer exists, it's a lecturer
        try:
            lecturer = Staff.objects.get(user=request.user)

            modules = Module.objects.filter(lecturers__id__exact=lecturer.id)
            lecturers = []
            students = []
            for module in modules:
                for student in module.students.all():
                    students.append(student)
            students = list(OrderedDict.fromkeys(students))
            lectures = Lecture.objects.filter(module__in=modules)

            is_valid_user = True
            user_type = 'STAFF'
        except Staff.DoesNotExist:
            pass

        # otherwise try student
        try:
            student = Student.objects.get(user=request.user)

            modules = Module.objects.filter(students__id__exact=student.id)
            lecturers = []
            for module in modules:
                for lecturer in module.lecturers.all():
                    lecturers.append(lecturer)
            lecturers = list(OrderedDict.fromkeys(lecturers))
            students = []
            lectures = Lecture.objects.filter(module__in=modules)
            is_valid_user = True

            user_type = 'STUDENT'
        except Student.DoesNotExist:
            pass

        # if we made it this far, user is invalid - log user out
        if not is_valid_user:
            modules = []
            lecturers = []
            students = []
            lectures = []
            user_type = 'INVALID'
            return logout_and_redirect_login(request)

    return render(request, 'tool/index.html', {
        'error_message': error_msg,
        'modules': modules,
        'lecturers': lecturers,
        'students': students,
        'lectures': lectures,
        'user_type': user_type
    })


@login_required
def upload(request):
    if request.method == 'POST' and request.FILES.get('upload-data', False):

        uploaded_list = []
        csv_file = request.FILES['upload-data']
        if not (csv_file.name.lower().endswith('.csv')):
            # workaround to pass message through redirect
            request.session['error_message'] = "Invalid file type. Only csv files are accepted."
            return redirect(reverse('tool:index'), Permanent=True)

        decoded_file = csv_file.read().decode('utf-8')
        file_str = io.StringIO(decoded_file)

        reader = csv.reader(file_str)

        module = None
        staff = []

        # finding module (step 1/3)
        found_module = False
        for counter, row in enumerate(reader):
            if found_module:
                module_data = ModuleRow(row)
                error_msg = module_data.get_error_message()
                if error_msg:
                    return redirect_with_error(request, reverse('tool:index'), error_msg)

                module = Module.objects.get(module_code=module_data.module)
                break

            if row[0] != 'Module Code':
                continue
            else:
                found_module = True
                continue

        # finding staff (step 2/3)
        found_staff = False
        for counter, row in enumerate(reader):
            if found_staff:
                if row[0].strip() and row[0].strip() != 'Student Attendance':
                    staff_data = StaffRow(row)
                    error_msg = staff_data.get_error_message()
                    if error_msg:
                        return redirect_with_error(request, reverse('tool:index'), error_msg)

                    staff.append(Staff.objects.get(user__username=staff_data.lecturer))
                else:
                    break

            if row[0] != 'Lecturers':
                continue
            else:
                found_staff = True
                continue

        # finally grabbing attendance data (step 3/3)
        attendance_session_data = None
        found_attendance = False
        for counter, row in enumerate(reader):
            # empty rows that can appear because of spreadsheet use
            if not ''.join(row).strip():
                continue

            if found_attendance:
                attendance_data = AttendanceRow(attendance_session_data, row)
                error_msg = attendance_data.get_error_message()
                if error_msg:
                    error_occurred_msg = 'Error with inputs: [[%s]] at line %s' % (error_msg, counter)
                    return redirect_with_error(request, reverse('tool:index'), error_occurred_msg)
                else:
                    uploaded_list.append(attendance_data)

            if row[0] != 'Device ID(s)':
                continue
            else:
                found_attendance = True
                attendance_session_data = AttendanceSessionRow(row)
                error_msg = attendance_session_data.get_error_message()
                if error_msg:
                    return redirect_with_error(request, reverse('tool:index'), error_msg)
                continue

        # associate lecturers with module if not already associated
        for lecturer in staff:
            if not any(lecturer.user.username == saved_lec.user.username for saved_lec in module.lecturers.all()):
                module.lecturers.add(lecturer)

        for uploaded_data in uploaded_list:
            uploaded_student = uploaded_data.student

            # associate student with module if not already associated
            if not any(uploaded_student.user.username == saved_stu.user.username for saved_stu in
                       module.students.all()):
                module.students.add(uploaded_student)

            for attendance_data in uploaded_data.attendances:
                session = attendance_data.session
                # TODO: extract outside so calls only performed once for lectures
                # create lectures if not already created
                lecture = Lecture.objects.filter(module=module,
                                                 session_id=session.session_id,
                                                 date=session.date).first()
                if not lecture:
                    new_lecture = Lecture(module=module, session_id=session.session_id, date=session.date)
                    new_lecture.save()
                    lecture = new_lecture

                # create attendance or update existing
                attended = attendance_data.attended
                stud_attendance = StudentAttendance.objects.filter(student=uploaded_student,
                                                                   lecture=lecture).first()
                if stud_attendance:
                    stud_attendance.attended = attended
                    stud_attendance.save()
                else:
                    new_attendance = StudentAttendance(student=uploaded_student,
                                                       lecture=lecture,
                                                       attended=attended)
                    new_attendance.save()

        uploaded_data = types.SimpleNamespace()
        uploaded_data.module = module
        uploaded_data.staff = staff
        uploaded_data.attendances = uploaded_list

        return render(request, 'tool/upload.html', {
            'uploaded_data': uploaded_data,
        })
    else:
        # workaround to pass message through redirect
        request.session['error_message'] = "No file uploaded. Please upload a .csv file."
        return redirect(reverse('tool:index'), Permanent=True)


@login_required
def settings(request):
    return render(request, 'tool/settings.html')


@login_required
def module(request, module_id):
    user_type = get_user_type(request)
    check_valid_user(user_type, request)

    if user_type == STUDENT_TYPE:
        student = Student.objects.get(user__username=request.user.username)

    try:
        module = Module.objects.get(id=module_id)
        # restrict access if student isn't linked to module
        if user_type == STUDENT_TYPE and not student in module.students.all():
            raise Http404("Not authorised to view this module")
    except Module.DoesNotExist:
        raise Http404("Module does not exist")

    lectures = Lecture.objects.filter(module=module)

    student_attendances = []
    # get attendances for lectures, sorted by student then date
    if (user_type == STUDENT_TYPE):
        lecture_attendances = StudentAttendance.objects.filter(student__in=[student]).order_by('lecture__date')
    else:
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=lectures).order_by('student',
                                                                                              'lecture__date')
    # group by student - tried many many variations of annotate etc. and nothing worked
    grouped_attendances = OrderedDict()
    for grouped_attendance in lecture_attendances:
        grouped_attendances.setdefault(grouped_attendance.student, []).append(grouped_attendance)

    # link students and attendances from dict back into list with percentage attended
    for student in grouped_attendances:
        student_attendance = types.SimpleNamespace()
        student_attendance.student = student
        student_attendance.attendances = []
        num_attended = 0
        for attendance in grouped_attendances[student]:
            student_attendance.attendances.append(attendance)
            if (attendance.attended):
                num_attended += 1
        student_attendance.percent_attended = (num_attended / len(student_attendance.attendances)) * 100
        student_attendances.append(student_attendance)

    # pie chart visualisation
    total_attendance_percentage = 0
    for student_attendance in student_attendances:
        total_attendance_percentage += student_attendance.percent_attended

    attended_percent = (total_attendance_percentage / len(student_attendances)) \
        if (len(student_attendances) > 0) else 0
    non_attended_percent = 100 - attended_percent

    # data format:
    #  data =  [
    #    ...[ Title, Value ]
    #  ]
    # initial values for what is shown, and value used
    title_data = ['Attendance', 'Attended?']
    attendance_data = ['Attended', attended_percent]
    non_attendance_data = ['Absent', non_attended_percent]
    chart_data = [title_data, non_attendance_data, attendance_data]

    chart = PieChart(SimpleDataSource(data=chart_data),
                     options={'title': 'Attendance', 'pieHole': 0.4, 'colors': ['#e74c3c', '#2ecc71']})

    return render(request, 'tool/module.html', {
        'module': module,
        'student_attendances': student_attendances,
        'chart': chart
    })


@login_required
def lecturer(request, lecturer_id):
    user_type = get_user_type(request)
    check_valid_user(user_type, request)

    try:
        lecturer = Staff.objects.get(id=lecturer_id)
    except Staff.DoesNotExist:
        raise Http404("Lecturer does not exist")

    if user_type == STUDENT_TYPE:
        raise Http404("Not authorised to view this lecturer")

    modules = Module.objects.filter(lecturers__in=[lecturer])
    module_attendances = []
    for module in modules:
        lectures = Lecture.objects.filter(module__in=[module])
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=lectures)
        num_attended = 0
        for lecture_attendance in lecture_attendances:
            if lecture_attendance.attended:
                num_attended += 1
        percent_attended = (num_attended / len(lecture_attendances)) * 100
        module_attendance = types.SimpleNamespace()
        module_attendance.module = module
        module_attendance.percent_attended = percent_attended
        module_attendances.append(module_attendance)

    return render(request, 'tool/lecturer.html', {
        'lecturer': lecturer,
        'module_attendances': module_attendances
    })


@login_required
def student(request, student_id):
    user_type = get_user_type(request)
    check_valid_user(user_type, request)

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404("Student does not exist")

    if user_type == STUDENT_TYPE and request.user.username != student.user.username:
        raise Http404("Not authorised to view this student")

    student_module_attendances = []
    # get attendances for lectures, sorted by date
    lecture_attendances = StudentAttendance.objects.filter(student__in=[student]).order_by('lecture__date')
    # group by module
    grouped_attendances = OrderedDict()
    for grouped_attendance in lecture_attendances:
        grouped_attendances.setdefault(grouped_attendance.lecture.module, []).append(grouped_attendance)

    # link modules and attendances from dict back into list with percentage attended
    for module in grouped_attendances:
        student_module_attendance = types.SimpleNamespace()
        student_module_attendance.module = module
        student_module_attendance.attendances = []
        num_attended = 0
        for attendance in grouped_attendances[module]:
            student_module_attendance.attendances.append(attendance)
            if (attendance.attended):
                num_attended += 1
            student_module_attendance.percent_attended = (num_attended / len(
                student_module_attendance.attendances)) * 100
        student_module_attendances.append(student_module_attendance)

    return render(request, 'tool/student.html', {
        'student': student,
        'student_module_attendances': student_module_attendances
    })


@login_required
def lecture(request, lecture_id):
    user_type = get_user_type(request)
    check_valid_user(user_type, request)

    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        raise Http404("Lecture does not exist")

    if user_type == STUDENT_TYPE:
        student = Student.objects.get(user__username=request.user.username)
        if student not in lecture.module.students.all():
            raise Http404("Not authorised to view this lecture")
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=[lecture], student=student).order_by(
            'lecture__date')
    else:
        # get attendances for lectures, sorted by student then date
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=[lecture]).order_by('student',
                                                                                               'lecture__date')

    return render(request, 'tool/lecture.html', {
        'lecture': lecture,
        'lecture_attendances': lecture_attendances
    })


# workaround to pass message through redirect
def redirect_with_error(request, redirect_url, error_msg):
    request.session['error_message'] = error_msg
    return redirect(redirect_url, Permanent=True)


def get_user_type(request):
    if request.user.is_staff:
        return ADMIN_TYPE
    else:
        try:
            Staff.objects.get(user=request.user)
            return STAFF_TYPE
        except Staff.DoesNotExist:
            pass

        try:
            Student.objects.get(user=request.user)
            return STUDENT_TYPE
        except Student.DoesNotExist:
            pass

    return None


def check_valid_user(user_type, request):
    if not user_type in VALID_TYPES:
        logout_and_redirect_login(request)


def logout_and_redirect_login(request):
    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
