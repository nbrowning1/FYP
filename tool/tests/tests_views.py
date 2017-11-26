from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Student, Staff, Module, Lecture, StudentAttendance
from django.urls import reverse
import datetime


class ViewsTests(TestCase):
    def test_login_view(self):
        url = reverse('tool:login')

        response = self.client.get(url)
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertNotContains(response, 'Please login to see this page.')

    def test_login_redirects_if_authenticated(self):
        authenticate_admin(self)

        url = reverse('tool:login')
        response = self.client.get(url)
        self.assertRedirects(response, '/tool/', status_code=302)

    def test_unauthenticated_index_view(self):
        url = reverse('tool:index')

        # first test redirect to correct URL
        response = self.client.get(url)
        self.assertRedirects(response, '/tool/login/?next=/tool/', status_code=302)

        # now follow redirect and test error message
        response = self.client.get(url, follow=True)
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertContains(response, 'Please login to see this page.')

    def test_authenticated_index_view(self):
        # test that when authenticated, it shows index view as expected
        authenticate_admin(self)

        response = go_to_index(self)
        self.assertContains(response, 'Home')
        self.assertNotContains(response, 'Username')
        self.assertNotContains(response, 'Password')

    def test_no_content_admin(self):
        authenticate_admin(self)

        response = go_to_index(self)
        self.assertContains(response, 'No modules are available.')
        self.assertContains(response, 'No lecturers are available.')
        self.assertContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

    def test_no_content_staff(self):
        authenticate_staff(self)

        response = go_to_index(self)

        # shouldn't see mention of 'lecturers'
        self.assertContains(response, 'No modules are available.')
        self.assertNotContains(response, 'No lecturers are available.')
        self.assertContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

    def test_no_content_student(self):
        authenticate_student(self)

        response = go_to_index(self)

        # shouldn't see mention of 'students'
        self.assertContains(response, 'No modules are available.')
        self.assertContains(response, 'No lecturers are available.')
        self.assertNotContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

    def test_content_admin(self):
        authenticate_admin(self)
        student_1 = create_student('test_student_1')
        student_2 = create_student('test_student_2')
        staff_1 = create_staff('test_staff_1')
        staff_2 = create_staff('test_staff_2')
        module = create_module('COM101')
        lecture = create_lecture(module)

        response = go_to_index(self)
        self.assertNotContains(response, 'No lecturers are available.')
        self.assertNotContains(response, 'No students are available.')
        self.assertNotContains(response, 'No modules are available.')
        self.assertNotContains(response, 'No lectures are available.')
        self.assertContains(response, 'test_student_1')
        self.assertContains(response, 'test_student_2')
        self.assertContains(response, 'test_staff_1')
        self.assertContains(response, 'test_staff_2')
        self.assertContains(response, 'COM101')
        self.assertContains(response, 'Lectures')

    def test_content_staff(self):
        test_staff = create_staff('test')
        self.client.login(username='test', password='12345')

        student_1 = create_student('test_student_1')
        student_2 = create_student('test_student_2')
        staff_1 = create_staff('test_staff_1')
        staff_2 = create_staff('test_staff_2')
        module_1 = create_module('COM101')
        module_2 = create_module('COM999')
        lecture_1 = create_lecture(module_1)
        lecture_2 = create_lecture(module_2)

        # nothing should appear when nothing is linked to staff
        response = go_to_index(self)
        self.assertContains(response, 'No students are available.')
        self.assertContains(response, 'No modules are available.')
        self.assertContains(response, 'No lectures are available.')

        # link module to 1 student and this staff member
        module_1.lecturers.add(test_staff)
        module_1.students.add(student_1)

        # linked items should now appear
        response = go_to_index(self)
        self.assertContains(response, 'test_student_1')
        self.assertNotContains(response, 'test_student_2')
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM999')
        self.assertContains(response, 'Lectures')

    def test_content_student(self):
        test_student = create_student('test')
        self.client.login(username='test', password='12345')

        student_1 = create_student('test_student_1')
        student_2 = create_student('test_student_2')
        staff_1 = create_staff('test_staff_1')
        staff_2 = create_staff('test_staff_2')
        module_1 = create_module('COM101')
        module_2 = create_module('COM999')
        lecture_1 = create_lecture(module_1)
        lecture_2 = create_lecture(module_2)

        # nothing should appear when nothing is linked to staff
        response = go_to_index(self)
        self.assertContains(response, 'No lecturers are available.')
        self.assertContains(response, 'No modules are available.')
        self.assertContains(response, 'No lectures are available.')

        # link module to 1 student and this staff member
        module_1.lecturers.add(staff_1)
        module_1.students.add(test_student)

        # linked items should now appear
        response = go_to_index(self)
        self.assertContains(response, 'test_staff_1')
        self.assertNotContains(response, 'test_staff_2')
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM999')
        self.assertContains(response, 'Lectures')

    def test_invalid_user(self):
        User.objects.create_user(username='test', password='12345')
        self.client.login(username='test', password='12345')

        # test invalid user log out is forced
        response = go_to_index(self)
        self.assertRedirects(response, '/tool/login/', status_code=302)


def go_to_index(self):
    url = reverse('tool:index')
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


def create_lecture(module):
    lecture = Lecture(module=module, session_id='session id', date=datetime.date(2017, 12, 1))
    lecture.save()
    return lecture
