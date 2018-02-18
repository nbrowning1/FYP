from django.test import TestCase
from django.urls import reverse

from .utils import *


class ModuleCourseViewSettingsTests(TestCase):
    def test_user_type_access(self):
        TestUtils.authenticate_admin(self)
        test_settings_and_save_pages(self, 404, 404)

        self.client.logout()
        TestUtils.authenticate_student(self)
        test_settings_and_save_pages(self, 404, 404)

        # only staff should have access
        self.client.logout()
        TestUtils.authenticate_staff(self)
        test_settings_and_save_pages(self, 200, 302)

    def test_unauthenticated_redirects(self):
        test_settings_and_save_pages(self, 302, 302)

    def test_can_see_modules_courses(self):
        TestUtils.authenticate_staff(self)
        create_db_props()
        response = get_settings_page(self)
        self.assertContains(response, 'EEE312')
        self.assertContains(response, 'COM999')
        self.assertContains(response, 'CourseCode_1')
        self.assertContains(response, 'CourseCode_2')

    def test_set_modules(self):
        TestUtils.authenticate_staff(self)
        staff = Staff.objects.get(user__username='teststaff')
        TestUtils.create_module('EEE312', 'EEE312-1')
        TestUtils.create_module('COM999', 'COM999-1')
        TestUtils.create_course('CourseCode_1')
        TestUtils.create_course('CourseCode_2')

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


def create_db_props():
    TestUtils.create_student('B00123456')
    TestUtils.create_student('B00987654')
    TestUtils.create_staff('e00123456')
    TestUtils.create_staff('e00987654')
    TestUtils.create_staff('e00555555')
    TestUtils.create_staff('e00666666')
    TestUtils.create_module('EEE312', 'EEE312-1')
    TestUtils.create_module('COM999', 'COM999-1')
    TestUtils.create_course('CourseCode_1')
    TestUtils.create_course('CourseCode_2')
