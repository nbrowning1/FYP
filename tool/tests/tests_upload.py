from django.test import TestCase

from django.urls import reverse

from django.core import mail

from django.contrib.auth.models import User

from ..models import Student, Staff, Module, Lecture, StudentAttendance

import os

class UploadTests(TestCase):
  
  def test_upload_valid_data(self):
    create_student('B00123456')
    create_student('B00987654')
    create_staff('A00123456')
    create_staff('A00987654')
    create_module('COM101')
    create_module('COM999')
    
    # initial check that module is not linked to student
    unlinked_module = Module.objects.get(module_code='COM101')
    self.assertTrue(len(unlinked_module.students.all()) == 0)
    
    test_upload(self, 'upload_test_valid.csv', None)
    
    # post-upload check to assert that upload process linked module with student
    linked_module = Module.objects.get(module_code='COM101')
    self.assertTrue(len(linked_module.students.all()) == 1)
    self.assertEqual(linked_module.students.all()[0].user.username, 'B00123456')
    
    # TODO: assert upload confirmation page
  
  def test_upload_unrecognised_data(self):
    # uploading valid data but with unrecognised module, staff, student
    test_upload(self, 'upload_test_valid.csv', 'Error with inputs: [[Unrecognised module: COM101, Unrecognised lecturer: A00123456, Unrecognised student: B00123456]] at line 1')
  
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

def create_student(username):
  user = User.objects.create_user(username=username, password='12345')
  student = Student(user=user)
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