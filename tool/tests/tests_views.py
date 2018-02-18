from django.test import TestCase
from django.urls import reverse

from .utils import *


class ViewsTests(TestCase):
    def test_login_view(self):
        url = reverse('tool:login')

        response = self.client.get(url)
        self.assertContains(response, 'Username')
        self.assertContains(response, 'Password')
        self.assertNotContains(response, 'Please login to see this page.')

    def test_login_redirects_if_authenticated(self):
        TestUtils.authenticate_admin(self)

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
        TestUtils.authenticate_admin(self)

        response = go_to_index(self)
        self.assertContains(response, 'Home')
        self.assertNotContains(response, 'Username')
        self.assertNotContains(response, 'Password')

    def test_no_content_admin(self):
        TestUtils.authenticate_admin(self)

        response = go_to_index(self)
        self.assertContains(response, 'No modules are available.')
        self.assertContains(response, 'No courses are available.')
        self.assertContains(response, 'No lecturers are available.')
        self.assertContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

    def test_no_content_staff(self):
        TestUtils.authenticate_staff(self)

        response = go_to_index(self)

        # shouldn't see mention of 'lecturers'
        self.assertContains(response, 'No modules added.')
        self.assertContains(response, 'No courses added.')
        self.assertNotContains(response, 'No lecturers are available.')
        self.assertContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

    def test_no_content_student(self):
        TestUtils.authenticate_student(self)

        response = go_to_index(self)

        # shouldn't see mention of 'courses' or 'students' or 'lecturers'
        # - student doesn't need to see their lecturers
        self.assertContains(response, 'No modules are available.')
        self.assertNotContains(response, 'No courses are available.')
        self.assertNotContains(response, 'No lecturers are available.')
        self.assertNotContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

    def test_content_admin(self):
        TestUtils.authenticate_admin(self)
        student_1 = TestUtils.create_student('test_student_1')
        student_2 = TestUtils.create_student('test_student_2')
        staff_1 = TestUtils.create_staff('test_staff_1')
        staff_2 = TestUtils.create_staff('test_staff_2')
        module = TestUtils.create_module('COM101', 'COM101-crn')
        lecture = create_lecture(module)

        response = go_to_index(self)
        self.assertNotContains(response, 'No modules are available.')
        self.assertNotContains(response, 'No courses are available.')
        self.assertNotContains(response, 'No lecturers are available.')
        self.assertNotContains(response, 'No students are available.')
        self.assertNotContains(response, 'No lectures are available.')
        self.assertContains(response, 'COM101')
        self.assertContains(response, 'Course Code')
        self.assertContains(response, 'test_student_1')
        self.assertContains(response, 'test_student_2')
        self.assertContains(response, 'test_staff_1')
        self.assertContains(response, 'test_staff_2')
        self.assertContains(response, 'Lectures')

    def test_content_staff(self):
        test_staff = TestUtils.create_staff('test')
        self.client.login(username='test', password='12345')

        student_1 = TestUtils.create_student('test_student_1')
        student_2 = TestUtils.create_student('test_student_2')
        staff_1 = TestUtils.create_staff('test_staff_1')
        staff_2 = TestUtils.create_staff('test_staff_2')
        module_1 = TestUtils.create_module('COM101', 'COM101-crn')
        module_2 = TestUtils.create_module('COM999', 'COM999-crn')
        lecture_1 = create_lecture(module_1)
        lecture_2 = create_lecture(module_2)

        # nothing should appear when nothing is linked to staff
        response = go_to_index(self)
        self.assertContains(response, 'No modules added.')
        self.assertContains(response, 'No courses added.')
        self.assertContains(response, 'No students are available.')
        self.assertContains(response, 'No lectures are available.')

        # link module to 1 student and this staff member
        test_staff.modules.add(module_1)
        module_1.students.add(student_1)
        test_staff.courses.add(Course.objects.get(course_code='Course Code'))

        # linked items should now appear
        response = go_to_index(self)
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM999')
        self.assertContains(response, 'Course Code')
        self.assertContains(response, 'test_student_1')
        self.assertNotContains(response, 'test_student_2')
        self.assertContains(response, 'Lectures')

    def test_content_student(self):
        test_student = TestUtils.create_student('test')
        self.client.login(username='test', password='12345')

        student_1 = TestUtils.create_student('test_student_1')
        student_2 = TestUtils.create_student('test_student_2')
        staff_1 = TestUtils.create_staff('test_staff_1')
        staff_2 = TestUtils.create_staff('test_staff_2')
        module_1 = TestUtils.create_module('COM101', 'COM101-crn')
        module_2 = TestUtils.create_module('COM999', 'COM999-crn')
        lecture_1 = create_lecture(module_1)
        lecture_2 = create_lecture(module_2)

        # nothing should appear when nothing is linked to staff
        response = go_to_index(self)
        self.assertNotContains(response, 'No lecturers are available.')
        self.assertContains(response, 'No modules are available.')
        self.assertContains(response, 'No lectures are available.')

        # link module to 1 student and this staff member
        staff_1.modules.add(module_1)
        module_1.students.add(test_student)

        # linked items should now appear
        response = go_to_index(self)
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


def create_lecture(module):
    return TestUtils.create_lecture(module, 'session id')
