from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from ..models import Student, Staff, Module, Lecture, StudentAttendance

from ..data_row import DataRow

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart

from collections import OrderedDict

import csv
import io
import logging

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
      logout(request)
      return HttpResponseRedirect(reverse('tool:login'))
    
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
    
    error_occurred_msg = ''
    reader = csv.reader(file_str)
    for counter, row in enumerate(reader):
      # skip first row - titles
      if counter == 0:
        continue
        
      # empty rows that can appear because of spreadsheet use
      if not ''.join(row).strip():
        break
    
      data = DataRow(row)
      error_with_data = data.get_error_message()
      if error_with_data:
        error_occurred_msg = 'Error with inputs: [[%s]] at line %s' % (error_with_data, counter)
        break
      else:
        uploaded_list.append(data)
      
    if error_occurred_msg:
      # workaround to pass message through redirect
      request.session['error_message'] = error_occurred_msg
      return redirect(reverse('tool:index'), Permanent=True)
    
    for uploaded_data in uploaded_list:
      saved_module = Module.objects.get(module_code=uploaded_data.module)
      uploaded_student = uploaded_data.student
      saved_student = Student.objects.get(user__username=uploaded_student)
      
      # associate lecturers with module if not already associated
      for lecturer in uploaded_data.lecturers:
        if not any(lecturer == saved_lec.user.username for saved_lec in saved_module.lecturers.all()):
          saved_lecturer = Staff.objects.get(user__username=lecturer)
          saved_module.lecturers.add(saved_lecturer)
          
      # associate student with module if not already associated
      if not any(uploaded_student == saved_stu.user.username for saved_stu in saved_module.students.all()):
        saved_module.students.add(saved_student)
        
      # create lecture if not already created
      lecture = Lecture.objects.filter(module__module_code=uploaded_data.module,
                                       semester=uploaded_data.semester,
                                       week=uploaded_data.week).first()
      if not lecture:
        new_lecture = Lecture(module=saved_module, semester=uploaded_data.semester, week=uploaded_data.week)
        new_lecture.save()
        lecture = new_lecture
        
      # create attendance or update existing
      attended_val = str(uploaded_data.attended).lower() in ("y", "1")
      stud_attendance = StudentAttendance.objects.filter(student=saved_student,
                                                    lecture=lecture).first()
      if stud_attendance:
        stud_attendance.attended = attended_val
        stud_attendance.save()
      else:
        new_attendance = StudentAttendance(student=saved_student,
                                          lecture=lecture,
                                          attended=attended_val)
        new_attendance.save()

    return render(request, 'tool/upload.html', {
      'uploaded_list': uploaded_list,
    })
  else:
    # workaround to pass message through redirect
    request.session['error_message'] = "No file uploaded. Please upload a .csv file."
    return redirect(reverse('tool:index'), Permanent=True)
  
@login_required
def settings(request):
  return render(request, 'tool/settings.html')
