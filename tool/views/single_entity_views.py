from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from graphos.renderers.gchart import LineChart, PieChart, BarChart
from graphos.sources.simple import SimpleDataSource

from .views_utils import UserType, ViewsUtils
from ..models import *


@login_required
def module(request, module_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    student = None
    if user_type == UserType.STUDENT_TYPE:
        student = Student.objects.get(user__username=request.user.username)

    try:
        module = Module.objects.get(id=module_id)
        # restrict access if student isn't linked to module
        if user_type == UserType.STUDENT_TYPE and not student in module.students.all():
            raise Http404("Not authorised to view this module")
    except Module.DoesNotExist:
        raise Http404("Module does not exist")

    module_data = get_module_data(module, user_type, student)
    module_feedback = get_module_feedback(module, student)

    pie_chart = get_attendance_pie_chart_from_percentages(request, module_data.student_attendances, 'Module Attendance Overview')
    line_chart = get_module_line_chart(module_data.lecture_attendances, len(module_data.student_attendances))

    return render(request, 'tool/single-entities/module.html', {
        'user_type': user_type.value,
        'module': module,
        'student_attendances': module_data.student_attendances,
        'module_feedback': module_feedback,
        'pie_chart': pie_chart,
        'line_chart': line_chart,
        'colours': ViewsUtils().get_pass_fail_colours_2_tone(request),
        'attendance_colours': ViewsUtils().get_pass_fail_colours_4_tone(request),
        'attendance_ranges': ViewsUtils().get_attendance_ranges(request)
    })


def get_module_feedback(module, student):
    # order by date descending - we'll want to see the newest feedback first
    if student:
        return ModuleFeedback.objects.filter(module=module, student=student).order_by('-date')
    else:
        return  ModuleFeedback.objects.filter(module=module).order_by('-date')


def get_module_line_chart(lecture_attendances, num_students):
    lecture_attendance_map = OrderedDict()
    for lecture_attendance in lecture_attendances:
        key = str(lecture_attendance.lecture.date) + ': \n' + lecture_attendance.lecture.session_id
        val = 1 if lecture_attendance.attended else 0
        lecture_attendance_map.setdefault(key, 0)
        lecture_attendance_map[key] = lecture_attendance_map[key] + val

    # initial values for what is shown, and value used
    title_data = ['Lecture', '% Attendance']

    chart_data = [title_data]
    for key, val in lecture_attendance_map.items():
        percentage_val = (val / num_students) * 100
        chart_data.append([key, percentage_val])

    return LineChart(SimpleDataSource(data=chart_data),
                     options={'title': 'Attendance per Lecture', 'pieHole': 0.4, 'colors': ['#3498db'],
                              'hAxis': {
                                  'title': "Lectures", 'titleTextStyle': {'bold': True, 'italic': False}
                              }}
                     )


@login_required
def course(request, course_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    if user_type == UserType.STUDENT_TYPE:
        raise Http404("Not authorised to view this lecturer")

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        raise Http404("Course does not exist")

    modules = course.modules.all()
    module_attendances = []
    for module in modules:
        module_data = get_module_data(module, user_type, student)
        module_attendance = types.SimpleNamespace()
        module_attendance.module = module
        module_attendance.percent_attended = get_attendance_percentage(module_data.student_attendances)
        module_attendances.append(module_attendance)

    pie_chart = get_attendance_pie_chart_from_percentages(request, module_attendances, 'Course Attendance Overview')

    return render(request, 'tool/single-entities/course.html', {
        'course': course,
        'module_attendances': module_attendances,
        'pie_chart': pie_chart,
        'attendance_colours': ViewsUtils().get_pass_fail_colours_4_tone(request),
        'attendance_ranges': ViewsUtils().get_attendance_ranges(request)
    })


def get_module_data(module, user_type, student):
    lectures = Lecture.objects.filter(module=module)

    # get attendances for lectures, sorted by student then date
    if (user_type == UserType.STUDENT_TYPE):
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=lectures, student__in=[student]).order_by('lecture__date')
    else:
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=lectures).order_by('student',
                                                                                              'lecture__date')
    # group by student - tried many many variations of annotate etc. and nothing worked
    grouped_attendances = OrderedDict()
    for grouped_attendance in lecture_attendances:
        grouped_attendances.setdefault(grouped_attendance.student, []).append(grouped_attendance)

    # link students and attendances from dict back into list with percentage attended
    student_attendances = []
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

    data = types.SimpleNamespace()
    data.lecture_attendances = lecture_attendances
    data.student_attendances = student_attendances
    return data


@login_required
def lecturer(request, lecturer_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    try:
        lecturer = Staff.objects.get(id=lecturer_id)
    except Staff.DoesNotExist:
        raise Http404("Lecturer does not exist")

    if user_type == UserType.STUDENT_TYPE:
        raise Http404("Not authorised to view this lecturer")

    modules = lecturer.modules.all()
    module_attendances = []
    for module in modules:
        lectures = Lecture.objects.filter(module__in=[module])
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=lectures)
        num_attended = 0
        for lecture_attendance in lecture_attendances:
            if lecture_attendance.attended:
                num_attended += 1
        percent_attended = (num_attended / len(lecture_attendances)) * 100 \
            if (len(lecture_attendances) > 0) else 0
        module_attendance = types.SimpleNamespace()
        module_attendance.module = module
        module_attendance.percent_attended = percent_attended
        module_attendances.append(module_attendance)

    pie_chart = get_attendance_pie_chart_from_percentages(request, module_attendances, 'Modules Attendance Overview')
    bar_chart = get_lecturer_bar_chart(module_attendances)

    return render(request, 'tool/single-entities/lecturer.html', {
        'lecturer': lecturer,
        'module_attendances': module_attendances,
        'pie_chart': pie_chart,
        'bar_chart': bar_chart,
        'attendance_colours': ViewsUtils().get_pass_fail_colours_4_tone(request),
        'attendance_ranges': ViewsUtils().get_attendance_ranges(request)
    })


def get_lecturer_bar_chart(module_attendances):
    # data format:
    #  data =  [
    #    ...[ Title, Value ]
    #  ]
    # initial values for what is shown, and value used
    title_data = ['Module', '% Attendance']
    chart_data = [title_data]
    for module_attendance in module_attendances:
        chart_data.append([module_attendance.module.module_code, module_attendance.percent_attended])

    return BarChart(SimpleDataSource(data=chart_data),
                    options={'title': 'Attendance per Module', 'colors': ['#3498db'],
                             'hAxis': {'minValue': 0, 'maxValue': 100}}
                    )


@login_required
def student(request, student_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404("Student does not exist")

    if user_type == UserType.STUDENT_TYPE and request.user.username != student.user.username:
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

    pie_chart = get_attendance_pie_chart_from_percentages(request, student_module_attendances, 'Module Attendance Overview')

    return render(request, 'tool/single-entities/student.html', {
        'student': student,
        'student_module_attendances': student_module_attendances,
        'pie_chart': pie_chart,
        'colours': ViewsUtils().get_pass_fail_colours_2_tone(request),
        'attendance_colours': ViewsUtils().get_pass_fail_colours_4_tone(request),
        'attendance_ranges': ViewsUtils().get_attendance_ranges(request)
    })


@login_required
def lecture(request, lecture_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        raise Http404("Lecture does not exist")

    if user_type == UserType.STUDENT_TYPE:
        student = Student.objects.get(user__username=request.user.username)
        if student not in lecture.module.students.all():
            raise Http404("Not authorised to view this lecture")
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=[lecture], student=student).order_by(
            'lecture__date')
    else:
        # get attendances for lectures, sorted by student then date
        lecture_attendances = StudentAttendance.objects.filter(lecture__in=[lecture]).order_by('student',
                                                                                               'lecture__date')

    pie_chart = get_attendance_pie_chart_from_absolute_vals(request, lecture_attendances, 'Lecture Attendance Overview')

    return render(request, 'tool/single-entities/lecture.html', {
        'user_type': user_type.value,
        'lecture': lecture,
        'lecture_attendances': lecture_attendances,
        'pie_chart': pie_chart,
        'colours': ViewsUtils().get_pass_fail_colours_2_tone(request),
        'attendance_ranges': ViewsUtils().get_attendance_ranges(request)
    })


def get_attendance_pie_chart_from_percentages(request, attendances, title):
    attended_percent = get_attendance_percentage(attendances)
    non_attended_percent = 100 - attended_percent
    return build_attendance_pie_chart(request, attended_percent, non_attended_percent, title)


def get_attendance_percentage(attendances):
    total_attendance_percentage = 0
    for attendance in attendances:
        total_attendance_percentage += attendance.percent_attended

    attended_percent = (total_attendance_percentage / len(attendances)) \
        if (len(attendances) > 0) else 0
    return attended_percent


def get_attendance_pie_chart_from_absolute_vals(request, attendances, title):
    total_attendance = 0
    for attendance in attendances:
        if attendance.attended:
            total_attendance += 1

    attended_percent = (total_attendance / len(attendances)) * 100 \
        if (len(attendances) > 0) else 0
    non_attended_percent = 100 - attended_percent
    return build_attendance_pie_chart(request, attended_percent, non_attended_percent, title)


def build_attendance_pie_chart(request, attended_percent, non_attended_percent, title):
    # data format:
    #  data =  [
    #    ...[ Title, Value ]
    #  ]
    # initial values for what is shown, and value used
    title_data = ['Attendance', 'Attended?']
    attendance_data = ['Attended', attended_percent]
    non_attendance_data = ['Absent', non_attended_percent]
    chart_data = [title_data, non_attendance_data, attendance_data]
    colors = ViewsUtils().get_pass_fail_colours_2_tone(request)

    return PieChart(SimpleDataSource(data=chart_data),
                    options={'title': title, 'pieHole': 0.4, 'colors': colors})
