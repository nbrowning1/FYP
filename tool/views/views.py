import csv
import io
import types
from collections import OrderedDict

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

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

    """
    mark_list = Mark.objects.order_by('-date')
    error_msg = request.session.pop('error_message', '')
    
    students_distinct = set(mark.student.student_code for mark in mark_list)
    
    # initial value - y-axis for data
    student_data = ['Date']
    for student_code in students_distinct:
      student_data.append(student_code)
      
    # order matters - we retrieved the dates in desc order, query could be changed but for now we'll just reverse since table still exists
    dates_distinct = reversed(list(OrderedDict.fromkeys(mark.date for mark in mark_list)))
    
    # data format:
  #  data =  [
  #    ...[ Y-axis, ...X-axis ]
  #  ]
    data = [ student_data ]
    for date in dates_distinct:
      data_item = []
      # y-axis value
      data_item.append(date)
      
      # marks achieved by students on date
      for student_code in students_distinct:
        # try to get existing student mark
        mark = Mark.objects.filter(student__student_code=student_code, date=date).first()
        if mark is not None:
          data_item.append(mark.mark)
        else:
          # set None (empty graph value)
          data_item.append(None)
  
      data.append(data_item)
  
    chart = LineChart(SimpleDataSource(data=data), options={'title': 'Marks over time'})
    
    return render(request, 'tool/index.html', {
      'mark_list': mark_list,
      'error_message': error_msg,
      'chart': chart
    })
    """


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
    user_type = None

    user_type = get_user_type(request)
    check_valid_user(user_type, request)

    if (user_type == STUDENT_TYPE):
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

    return render(request, 'tool/module.html', {
        'module': module,
        'student_attendances': student_attendances,
        'user_type': user_type
    })


@login_required
def student(request, student_id):
    user_type = None
    is_valid_user = False

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        raise Http404("Student does not exist")

    if request.user.is_staff:
        is_valid_user = True
    else:
        try:
            Staff.objects.get(user=request.user)
            is_valid_user = True
        except Staff.DoesNotExist:
            pass

        try:
            Student.objects.get(user=request.user)
            is_valid_user = True
        except Student.DoesNotExist:
            pass

    if not is_valid_user:
        return logout_and_redirect_login(request)

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
        'student_module_attendances': student_module_attendances,
        'user_type': user_type
    })


@login_required
def lecture(request, lecture_id):
    user_type = None
    is_valid_user = False

    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        raise Http404("Lecture does not exist")

    if request.user.is_staff:
        is_valid_user = True
    else:
        try:
            Staff.objects.get(user=request.user)
            is_valid_user = True
        except Staff.DoesNotExist:
            pass

        try:
            Student.objects.get(user=request.user)
            is_valid_user = True
        except Student.DoesNotExist:
            pass

    if not is_valid_user:
        return logout_and_redirect_login(request)

    # get attendances for lectures, sorted by student then date
    lecture_attendances = StudentAttendance.objects.filter(lecture__in=[lecture]).order_by('student', 'lecture__date')

    return render(request, 'tool/lecture.html', {
        'lecture': lecture,
        'lecture_attendances': lecture_attendances,
        'user_type': user_type
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
