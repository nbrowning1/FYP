from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Student, Staff, Module, Lecture, StudentAttendance

from .data_row import DataRow

from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart

from collections import OrderedDict

import csv
import io
import logging

@login_required
def index(request):
  error_msg = request.session.pop('error_message', '')
    
  modules = Module.objects.all()
  lecturers = Staff.objects.all()
  students = Student.objects.all()
  lectures = Lecture.objects.all()
    
  return render(request, 'tool/index.html', {
    'error_message': error_msg,
    'modules': modules,
    'lecturers': lecturers,
    'students': students,
    'lectures': lectures,
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

    return render(request, 'tool/upload.html', {
      'uploaded_list': uploaded_list,
    })
  else:
    # workaround to pass message through redirect
    request.session['error_message'] = "No file uploaded. Please upload a .csv file."
    return redirect(reverse('tool:index'), Permanent=True)
