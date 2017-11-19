from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from ..models import Student, Staff, Module, Lecture, StudentAttendance

from ..data_rows import ModuleRow, StaffRow, AttendanceSessionRow, AttendanceRow

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart

from collections import OrderedDict

import csv, io, logging, types

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
      if not any(uploaded_student.user.username == saved_stu.user.username for saved_stu in module.students.all()):
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
  is_valid_user = False
  
  try:
    module = Module.objects.get(id=module_id)
  except Module.DoesNotExist:
    raise Http404("Poll does not exist")
    
  lectures = Lecture.objects.filter(module=module)
  
  try:
    lecturer = Staff.objects.get(user=request.user)
  except Staff.DoesNotExist:
    pass
  
  if request.user.is_staff or lecturer:
    students = []
    for student in module.students.all():
      students.append(student)
    students = list(OrderedDict.fromkeys(students))
    
    if request.user.is_staff:
      user_type = 'ADMIN'
    else:
      user_type = 'STAFF' 
    is_valid_user = True
  else:
    
    try:
      student = Student.objects.get(user=request.user)
      students = []
      user_type = 'STUDENT'
      is_valid_user = True
    except Student.DoesNotExist:
      pass
    
  if not is_valid_user:
    return logout_and_redirect_login(request)
  
  return render(request, 'tool/module.html', {
    'module': module,
    'students': students,
    'lectures': lectures,
    'user_type': user_type
  })
  

# workaround to pass message through redirect
def redirect_with_error(request, redirect_url, error_msg):
  request.session['error_message'] = error_msg
  return redirect(redirect_url, Permanent=True)

def logout_and_redirect_login(request):
  logout(request)
  return HttpResponseRedirect(reverse('tool:login'))
