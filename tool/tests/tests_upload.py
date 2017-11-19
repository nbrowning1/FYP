from django.test import TestCase

from django.urls import reverse

from django.core import mail

from django.contrib.auth.models import User

from ..models import Student, Staff, Module, Lecture, StudentAttendance

import os

class UploadTests(TestCase):
  
  def test_upload_valid_data(self):
    create_student('B00123456', '10519C')
    create_student('B00987654', '10518B')
    create_staff('e00123456')
    create_staff('e00987654')
    create_module('EEE312')
    
    # initial check that module is not linked to student
    unlinked_module = Module.objects.get(module_code='EEE312')
    self.assertEqual(len(unlinked_module.students.all()), 0)
    
    test_upload(self, 'upload_test_valid.csv', None)
    
    # post-upload check to assert that upload process linked module with students
    linked_module = Module.objects.get(module_code='EEE312')
    self.assertEqual(len(linked_module.students.all()), 2)
    self.assertEqual(linked_module.students.all()[0].user.username, 'B00123456')
    self.assertEqual(linked_module.students.all()[1].user.username, 'B00987654')
    
    lectures = Lecture.objects.all()
    self.assertEqual(len(lectures), 6)
    # should all be linked to module
    self.assertEqual(lectures[0].module.module_code, 'EEE312')
    self.assertEqual(lectures[5].module.module_code, 'EEE312')
    self.assertEqual(lectures[0].session_id, '170925 1228')
    self.assertEqual(lectures[1].session_id, 'EEE122 170926 1138')
    self.assertEqual(lectures[2].session_id, 'EEE122 171002 1211')
    self.assertEqual(lectures[3].session_id, 'EEE122/3-10-2017 171003 1526')
    self.assertEqual(lectures[4].session_id, 'EEE122_Lecture 171003 1010')
    self.assertEqual(lectures[5].session_id, 'EEE122/171005 0949')
    
    attendances = StudentAttendance.objects.all()
    self.assertEqual(len(attendances), 12)
    # first 6 linked to first student..
    self.assertEqual(attendances[0].student.user.username, 'B00123456')
    self.assertEqual(attendances[5].student.user.username, 'B00123456')
    self.assertEqual(attendances[0].lecture.session_id, '170925 1228')
    self.assertEqual(attendances[5].lecture.session_id, 'EEE122/171005 0949')
    self.assertEqual(attendances[0].attended, True)
    self.assertEqual(attendances[1].attended, True)
    self.assertEqual(attendances[2].attended, True)
    self.assertEqual(attendances[3].attended, False)
    self.assertEqual(attendances[4].attended, True)
    self.assertEqual(attendances[5].attended, False)
    
    # ..last 6 to second student
    self.assertEqual(attendances[6].student.user.username, 'B00987654')
    self.assertEqual(attendances[11].student.user.username, 'B00987654')
    self.assertEqual(attendances[6].lecture.session_id, '170925 1228')
    self.assertEqual(attendances[11].lecture.session_id, 'EEE122/171005 0949')
    self.assertEqual(attendances[6].attended, False)
    self.assertEqual(attendances[7].attended, True)
    self.assertEqual(attendances[8].attended, True)
    self.assertEqual(attendances[9].attended, True)
    self.assertEqual(attendances[10].attended, True)
    self.assertEqual(attendances[11].attended, False)
    
    # TODO: assert upload confirmation page
  
  def test_upload_unrecognised_module(self):
    # uploading valid data but without full DB setup
    test_upload(self, 'upload_test_valid.csv', 'Unrecognised module: EEE312')
    
  def test_upload_unrecognised_lecturer(self):
    create_module('EEE312')
    # uploading valid data but without full DB setup
    test_upload(self, 'upload_test_valid.csv', 'Unrecognised lecturer: e00987654')
    
  def test_upload_unrecognised_student(self):
    create_staff('e00123456')
    create_staff('e00987654')
    create_module('EEE312')
    # uploading valid data but without full DB setup
    test_upload(self, 'upload_test_valid.csv', 'Error with inputs: [[Unrecognised student: 10519C]] at line 2')
    
  def test_upload_invalid_attendance_data(self):
    create_student('B00123456', '10519C')
    create_student('B00987654', '10518B')
    create_staff('e00123456')
    create_staff('e00987654')
    create_module('EEE312')
    test_upload(self, 'upload_test_invalid.csv', 'Error with inputs: [[Unrecognised attendance value for 10519C: yes at column 1, Unrecognised attendance value for 10519C: no at column 4]] at line 2')
  
  def test_upload_incorrect_file_extension(self):
    test_upload(self, 'upload_test_wrong_ext.txt', 'Invalid file type. Only csv files are accepted.')
    
  def test_upload_no_file(self):
    test_upload(self, None, 'No file uploaded. Please upload a .csv file.')
    
def test_upload(self, file_path, expected_error_msg):
  authenticate_admin(self)
    
  response = self.client.get(reverse('tool:index'))
  self.assertEqual(response.status_code, 200)
  if expected_error_msg:
    self.assertNotContains(response, expected_error_msg)

  this_dir = os.path.dirname(os.path.abspath(__file__));
  # if no path specified, post without any upload data
  if file_path:
    res_path = os.path.join(this_dir, 'resources', file_path)
    with open(res_path) as fp:
      response = self.client.post(reverse('tool:upload'), {'upload-data': fp}, follow=True)
  else:
    res_path = ''
    response = self.client.post(reverse('tool:upload'), follow=True)
  
  self.assertEqual(response.status_code, 200)
  
  # if no error message expected, check for successfully making it to upload confirmation page
  if expected_error_msg:
    self.assertEqual(response.request['PATH_INFO'], '/tool/')
    self.assertContains(response, expected_error_msg)
  else:
    self.assertEqual(response.request['PATH_INFO'], '/tool/upload/')
    
  return response
    
def authenticate_admin(self):
  user = User.objects.create_superuser(username='test', password='12345', email='test@mail.com')
  self.client.login(username='test', password='12345')
  return user

def create_student(username, device_id):
  user = User.objects.create_user(username=username, password='12345')
  student = Student(user=user, device_id=device_id)
  student.save()
  return student
  
def create_staff(username):
  user = User.objects.create_user(username=username, password='12345')
  staff = Staff(user=user)
  staff.save()
  return staff

def create_module(module_code):
  module = Module(module_code=module_code)
  module.save()
  return module