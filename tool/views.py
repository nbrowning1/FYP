from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Student, Mark

import csv
import io
import logging

# Create your views here.
class IndexView(generic.ListView):
  template_name = 'tool/index.html'
  context_object_name = 'mark_list'
  
  def get_queryset(self):
    """
    Return all marks
    """
    # lte = less than or equal to
    return Mark.objects.order_by('-date')
  
def upload(request):
  if request.method == 'POST' and request.FILES['upload-marks']:

    uploaded_list = []
    csv_file = request.FILES['upload-marks']
    if not (csv_file.name.lower().endswith('.csv')):
      return render(request, 'tool/index.html', {
        'error_message': "Invalid file type. Only csv files are accepted."
      })
    
    decoded_file = csv_file.read().decode('utf-8')
    file_str = io.StringIO(decoded_file)
    
    reader = csv.reader(file_str)
    for counter, row in enumerate(reader):
      if (counter == 0):
        continue
    
      try:
        # try to get existing student
        student = Student.objects.get(student_code=row[0])
      except Student.DoesNotExist:
        # create new student
        student = Student(student_code=row[0])
        student.save()
        
      mark = Mark(student=student, mark=row[1], date=row[2])
      mark.save()
        
      data = DataRow(row[0], row[1], row[2])
      uploaded_list.append(data)

    return render(request, 'tool/upload.html', {
      'uploaded_list': uploaded_list,
    })

class DataRow:
    def __init__(self, first, second, third):
        self.first = first
        self.second = second
        self.third = third
