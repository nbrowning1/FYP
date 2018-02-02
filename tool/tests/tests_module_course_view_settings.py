import os

from django.test import TestCase
from django.urls import reverse

from ..models import *


class ModuleCourseViewSettingsTests(TestCase):
    def test_user_type_access(self):
        authenticate_admin(self)
        test_settings_and_save_pages(self, 404, 404)

        self.client.logout()
        authenticate_student(self)
        test_settings_and_save_pages(self, 404, 404)

        # only staff should have access
        self.client.logout()
        authenticate_staff(self)
        test_settings_and_save_pages(self, 200, 302)

    def test_unauthenticated_redirects(self):
        test_settings_and_save_pages(self, 302, 302)

    def test_can_see_modules_courses(self):
        authenticate_staff(self)
        create_db_props()
        response = get_settings_page(self)
        self.assertContains(response, 'EEE312')
        self.assertContains(response, 'COM999')
        self.assertContains(response, 'CourseCode_1')
        self.assertContains(response, 'CourseCode_2')

    def test_set_modules(self):
        authenticate_staff(self)
        staff = Staff.objects.get(user__username='teststaff')
        mod1 = create_module('EEE312', 'EEE312-1')
        mod2 = create_module('COM999', 'COM999-1')
        course1 = create_course('CourseCode_1')
        course2 = create_course('CourseCode_2')

        # should initially have no linked modules / courses
        self.assertEqual(len(staff.modules.all()), 0)
        self.assertEqual(len(staff.courses.all()), 0)

        response = self.client.post(reverse('tool:save_module_course_settings'),
                         {'modules[]': ['code_EEE312 crn_EEE312-1', 'code_COM999 crn_COM999-1'],
                          'courses[]': ['code_CourseCode_1']})

        # should redirect on success
        self.assertEqual(response.status_code, 302)
        # should now have linked modules / courses
        self.assertEqual(len(staff.modules.all()), 2)
        self.assertEqual(len(staff.courses.all()), 1)


def test_settings_and_save_pages(self, settings_status_code, save_status_code):
    response = get_settings_page(self)
    self.assertEqual(response.status_code, settings_status_code)
    response = get_save_page(self)
    self.assertEqual(response.status_code, save_status_code)


def get_settings_page(self):
    return self.client.get(reverse('tool:module_course_view_settings'))


def get_save_page(self):
    return self.client.get(reverse('tool:save_module_course_settings'))


def authenticate_admin(self):
    user = User.objects.create_superuser(username='test', password='12345', email='test@mail.com')
    self.client.login(username='test', password='12345')
    return user


def authenticate_student(self):
    user = create_student('teststudent', 'test').user
    self.client.login(username='teststudent', password='12345')
    return user


def authenticate_staff(self):
    user = create_staff('teststaff').user
    self.client.login(username='teststaff', password='12345')
    return user


def create_db_props():
    create_student('B00123456', '10519C')
    create_student('B00987654', '10518B')
    create_staff('e00123456')
    create_staff('e00987654')
    create_staff('e00555555')
    create_staff('e00666666')
    create_module('EEE312', 'EEE312-1')
    create_module('COM999', 'COM999-1')
    create_course('CourseCode_1')
    create_course('CourseCode_2')


def create_course(course_code):
    try:
        course = Course.objects.get(course_code=course_code)
        return course
    except Course.DoesNotExist:
        course = Course(course_code=course_code)
        course.save()
        return course


def create_student(username, device_id):
    user = User.objects.create_user(username=username, password='12345')
    course = create_course('Course Code')
    student = Student(user=user, device_id=device_id, course=course)
    student.save()
    return student


def create_staff(username):
    user = User.objects.create_user(username=username, password='12345')
    staff = Staff(user=user)
    staff.save()
    return staff


def create_module(module_code, crn):
    module = Module(module_code=module_code, module_crn=crn)
    module.save()
    return module
