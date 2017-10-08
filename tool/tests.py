import datetime

from django.test import TestCase

from django.contrib.auth.models import User
from .models import Student, Staff, Module, Lecture, StudentAttendance

from .data_row import DataRow

class DataRowTests(TestCase):
  
  def test_valid_row(self):
    setup_test_db('B00112233', 'S00112233', 'COM101')
    data = setup_input_data('COM101','S00112233',1,1,'B00112233','Y') 
  
    self.assertEqual(data.get_error_message(), '')
    
  def test_invalid_student_message(self):
    setup_test_db('B00000000', 'S00112233', 'COM101')
    data = setup_input_data('COM101','S00112233',1,1,'B00112233','Y')
    
    self.assertEqual(data.get_error_message(), 'Unrecognised student: B00112233')
    
  def test_invalid_multiple(self):
    setup_test_db('B00000000', 'S00000000', 'COM000')
    data = setup_input_data('COM101','S00112233',100,-1,'B00112233','x')
    
    self.assertEqual(data.get_error_message(), 'Unrecognised module: COM101, Unrecognised lecturer: S00112233, Semester 100 out of range, Week -1 out of range, Unrecognised student: B00112233, Unrecognised attendance value: x')
    
  def test_it_trims_spaces(self):
    setup_test_db('B00112233', 'S00112233', 'COM101')
    data = setup_input_data('COM101 ','S00112233 ',1,1,'B00112233 ',' Y ') 
  
    self.assertEqual(data.get_error_message(), '')
    
  def test_multiple_lecturers(self):
    setup_test_db('B00112233', 'S00112233', 'COM101')
    # create a second staff member
    staff_user = User.objects.create_user(username='SS99887766', email='test@email.com', password='CorrectHorseBatteryStaple')
    lecturer = Staff(user=staff_user)
    lecturer.save()
  
    data = setup_input_data('COM101','S00112233;SS99887766',1,1,'B00112233','Y') 
  
    self.assertEqual(data.get_error_message(), '')
    
def setup_test_db(student_code, staff_code, module_code):
  student_user = User.objects.create_user(username=student_code, email='test@email.com', password='CorrectHorseBatteryStaple')
  student = Student(user=student_user)
  student.save()

  staff_user = User.objects.create_user(username=staff_code, email='test@email.com', password='CorrectHorseBatteryStaple')
  lecturer = Staff(user=staff_user)
  lecturer.save()

  module = Module(module_code=module_code)
  module.save()
  
def setup_input_data(module_code, staff_code, semester, week, student_code, attended):
  list_data = [module_code,staff_code,semester,week,student_code,attended]
  return DataRow(list_data)