from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Student, Staff, Module, Lecture, StudentAttendance
from django.urls import reverse
import datetime

class SingleModuleViewTests(TestCase):
    
  def test_single_module_view_admin(self):
    authenticate_admin(self)
    test_valid_module_view(self, True)
    
  def test_single_module_view_staff(self):
    authenticate_staff(self)
    test_valid_module_view(self, True)
    
  def test_single_module_view_student(self):
    authenticate_student(self)
    test_valid_module_view(self, False)
    
  def test_module_unauthenticated(self):
    module = create_module('COM101')
    
    # check module that exists
    response = go_to_module(self, 1)
    self.assertRedirects(response, '/tool/login/?next=/tool/modules/1', status_code=302)
    
    # check module that doesnt exist - should be same response
    response = go_to_module(self, 10)
    self.assertRedirects(response, '/tool/login/?next=/tool/modules/10', status_code=302)
    
  def test_nonexistent_module(self):
    authenticate_admin(self)
    
    module = create_module('COM101')
    response = go_to_module(self, 10)
    self.assertEqual(response.status_code, 404)
    
def test_valid_module_view(self, should_see_students):
  module1 = create_module('COM101')
  module2 = create_module('COM102')
  student1 = create_student('B00123456')
  student2 = create_student('B00987654')
  lecture1 = create_lecture(module1, 'Session 1')
  lecture2 = create_lecture(module1, 'Session 2')
  module1.students.add(student2)

  # should only see information relating to COM101 module - first created
  response = go_to_module(self, 1)
  self.assertContains(response, 'COM101')
  self.assertNotContains(response, 'COM102')
  if should_see_students:
    self.assertNotContains(response, 'B00123456')
    self.assertContains(response, 'B00987654')
  else:
    self.assertNotContains(response, 'B00123456')
    self.assertNotContains(response, 'B00987654')
  self.assertContains(response, 'Session 1')
  self.assertContains(response, 'Session 2')
  self.assertContains(response, 'Dec. 1, 2017')

  # should only see information relating to COM102 module - second created
  response = go_to_module(self, 2)
  self.assertNotContains(response, 'COM101')
  self.assertContains(response, 'COM102')
  if should_see_students:
    self.assertContains(response, 'No students are available.')
  else:
    self.assertNotContains(response, 'No students are available.')
  self.assertNotContains(response, 'B00123456')
  self.assertNotContains(response, 'B00987654')
  self.assertNotContains(response, 'Session 1')
  self.assertNotContains(response, 'Session 2')
  self.assertNotContains(response, 'Dec. 1, 2017')
  self.assertContains(response, 'No lectures are available.')


class SingleStudentViewTests(TestCase):
  

def go_to_module(self, module_id):
  url = reverse('tool:module', kwargs={ 'module_id': module_id })
  return self.client.get(url)
    
def authenticate_admin(self):
  user = User.objects.create_superuser(username='test', password='12345', email='test@mail.com')
  self.client.login(username='test', password='12345')
  return user

def authenticate_student(self):
  user = create_student('test').user
  self.client.login(username='test', password='12345')
  return user

def authenticate_staff(self):
  user = create_staff('test').user
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

def create_lecture(module, session_id):
  lecture = Lecture(module=module, session_id=session_id, date=datetime.date(2017, 12, 1))
  lecture.save()
  return lecture
