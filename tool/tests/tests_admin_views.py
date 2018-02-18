from django.test import TestCase
from django.urls import reverse

from .utils import *


class GeneralTests(TestCase):
    def test_unauthenticated(self):
        response = go_to_admin_create_module(self)
        self.assertRedirects(response, '/tool/login/?next=/tool/admin-create-module/', status_code=302)
        response = go_to_admin_create_course(self)
        self.assertRedirects(response, '/tool/login/?next=/tool/admin-create-course/', status_code=302)
        response = go_to_admin_create_student(self)
        self.assertRedirects(response, '/tool/login/?next=/tool/admin-create-student/', status_code=302)

    def test_permissions(self):
        # student should see nothing
        TestUtils.authenticate_student(self)
        response = go_to_admin_create_module(self)
        self.assertEqual(response.status_code, 404)
        response = go_to_admin_create_course(self)
        self.assertEqual(response.status_code, 404)
        response = go_to_admin_create_student(self)
        self.assertEqual(response.status_code, 404)

        # staff should be able to see
        TestUtils.authenticate_staff(self)
        response = go_to_admin_create_module(self)
        self.assertEqual(response.status_code, 200)
        response = go_to_admin_create_course(self)
        self.assertEqual(response.status_code, 200)
        response = go_to_admin_create_student(self)
        self.assertEqual(response.status_code, 200)


class CreateModuleTests(TestCase):
    def test_create_module(self):
        test_module_create_view(self, 'COM101', 'COM101-crn', None)
        module = Module.objects.get(module_code='COM101', module_crn='COM101-crn')
        self.assertEqual(module.module_code, 'COM101')
        self.assertEqual(module.module_crn, 'COM101-crn')

    def test_invalid_module(self):
        test_module_create_view(self, 'COM1000', 'COM101-crn',
                                ['Must be a valid module code e.g. COM101'])

    def test_module_already_exists(self):
        test_module_create_view(self, 'COM101', 'COM101-crn', None)
        # test same case
        test_module_create_view(self, 'COM101', 'COM101-crn',
                                'Module with this Module code and Module crn already exists.')
        # test case insensitive
        test_module_create_view(self, 'com101', 'com101-CRN',
                                'Module with this Module code and Module crn already exists.')


class CreateCourseTests(TestCase):
    def test_create_course(self):
        test_course_create_view(self, 'Course Code', None)
        course = Course.objects.get(course_code='Course Code')
        self.assertEqual(course.course_code, 'Course Code')

    def test_invalid_course(self):
        test_course_create_view(self,
                                '12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901',
                                ['Ensure this value has at most 100 characters (it has 101).'])

    def test_course_already_exists(self):
        test_course_create_view(self, 'Course Code', None)
        test_course_create_view(self, 'Course Code',
                                ['Course with this Course code already exists'])
        test_course_create_view(self, 'COURSE CODE',
                                ['Course with this Course code already exists'])


class CreateStudentTests(TestCase):
    def test_create_student(self):
        course = Course(course_code='Course Code')
        course.save()
        test_student_create_view(self, 'B00112233', 'Fname', 'Lname', 'test@email.com', '10101C', course.id, None)
        student = Student.objects.get(user__username='B00112233')
        self.assertEqual(student.device_id, '10101C')
        self.assertTrue(student.user.has_usable_password())

    def test_invalid_student(self):
        test_student_create_view(self, 'E00112233', '', '', 'test', '1-', -1,
                                 ['Must be a valid student code e.g. B00112233',
                                  'This field is required.',
                                  'Enter a valid email address.',
                                  'Must be a valid device ID e.g. 10101C',
                                  'Select a valid choice. That choice is not one of the available choices.'])

    def test_student_already_exists(self):
        course = Course(course_code='Course code')
        course.save()

        test_student_create_view(self, 'B00112233', 'Fname', 'Lname', 'test@email.com', '10101C', course.id, None)

        # same-case and case-sensitive checks for username
        # (case-insensitive fails because lowercase b doesnt match pattern)
        test_student_create_view(self, 'B00112233', 'Fname', 'Lname', 'test@email.com', '10101C', course.id,
                                 ['User with this Username already exists',
                                  'Student with this Device ID already exists'])
        test_student_create_view(self, 'b00112233', 'Fname', 'Lname', 'test@email.com', '10101c', course.id,
                                 ['Must be a valid student code e.g. B00112233',
                                  'Student with this Device ID already exists'])

        # same-case and case-sensitive checks for email
        test_student_create_view(self, 'B00112234', 'Fname', 'Lname', 'test@email.com', '10101c', course.id,
                                 ['User with this Email address already exists',
                                  'Student with this Device ID already exists']),
        test_student_create_view(self, 'B00112234', 'Fname', 'Lname', 'TEST@EMAIL.com', '10101c', course.id,
                                 ['User with this Email address already exists',
                                  'Student with this Device ID already exists'])


class CreateStaffTests(TestCase):
    def test_create_staff(self):
        test_staff_create_view(self, 'E00112233', 'Fname', 'Lname', 'test@email.com', None)
        staff = Staff.objects.get(user__username='E00112233')
        self.assertEqual(staff.user.first_name, 'Fname')
        self.assertTrue(staff.user.has_usable_password())

    def test_invalid_staff(self):
        test_staff_create_view(self, 'B00112233', '', '', 'test',
                               ['Must be a valid staff code e.g. E00112233'])

    def test_staff_already_exists(self):
        test_staff_create_view(self, 'E00112233', 'Fname', 'Lname', 'test@email.com', None)

        # same-case and case-sensitive checks for username
        # (case-insensitive fails because lowercase e doesnt match pattern)
        test_staff_create_view(self, 'E00112233', 'Fname', 'Lname', 'test@email.com',
                               ['User with this Username already exists'])
        test_staff_create_view(self, 'e00112233', 'Fname', 'Lname', 'test@email.com',
                               ['Must be a valid staff code e.g. E00112233'])

        # same-case and case-sensitive checks for email
        test_staff_create_view(self, 'E00112234', 'Fname', 'Lname', 'test@email.com',
                               ['User with this Email address already exists']),
        test_staff_create_view(self, 'E00112234', 'Fname', 'Lname', 'TEST@EMAIL.com',
                               ['User with this Email address already exists'])


def go_to_admin_create_module(self):
    url = reverse('tool:admin_create_module')
    return self.client.get(url)


def go_to_admin_create_course(self):
    url = reverse('tool:admin_create_course')
    return self.client.get(url)


def go_to_admin_create_student(self):
    url = reverse('tool:admin_create_student')
    return self.client.get(url)


def submit_create_module(self, module_code, module_crn):
    TestUtils.authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_module'),
                            {'module_code': module_code,
                             'module_crn': module_crn}, follow=True)


def submit_create_course(self, course_code):
    TestUtils.authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_course'),
                            {'course_code': course_code}, follow=True)


def submit_create_student(self, username, first_name, last_name, email, device_id, course_id):
    TestUtils.authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_student'),
                            {'username': username,
                             'first_name': first_name,
                             'last_name': last_name,
                             'email': email,
                             'device_id': device_id,
                             'course': course_id}, follow=True)


def submit_create_staff(self, username, first_name, last_name, email):
    TestUtils.authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_staff'),
                            {'username': username,
                             'first_name': first_name,
                             'last_name': last_name,
                             'email': email}, follow=True)


def test_module_create_view(self, module_code, module_crn, expected_errors):
    get_num_objs_fn = Module.objects.all
    initial_modules_num = len(get_num_objs_fn())
    response = submit_create_module(self, module_code, module_crn)
    saved_str = "Module %s saved" % module_code
    test_admin_create_view(self, initial_modules_num, response, expected_errors, get_num_objs_fn, saved_str)


def test_course_create_view(self, course_code, expected_errors):
    get_num_objs_fn = Course.objects.all
    initial_courses_num = len(get_num_objs_fn())
    response = submit_create_course(self, course_code)
    saved_str = "Course %s saved" % course_code
    test_admin_create_view(self, initial_courses_num, response, expected_errors, get_num_objs_fn, saved_str)


def test_student_create_view(self, username, first_name, last_name, email, device_id, course_id, expected_errors):
    get_num_objs_fn = Student.objects.all
    initial_courses_num = len(get_num_objs_fn())
    response = submit_create_student(self, username, first_name, last_name, email, device_id, course_id)
    saved_str = "Student %s saved" % username
    test_admin_create_view(self, initial_courses_num, response, expected_errors, get_num_objs_fn, saved_str)


def test_staff_create_view(self, username, first_name, last_name, email, expected_errors):
    TestUtils.authenticate_staff(self)
    get_num_objs_fn = Staff.objects.all
    initial_courses_num = len(get_num_objs_fn())
    response = submit_create_staff(self, username, first_name, last_name, email)
    saved_str = "Staff %s saved" % username
    test_admin_create_view(self, initial_courses_num, response, expected_errors, get_num_objs_fn, saved_str)


def test_admin_create_view(self, initial_objs_num, response, expected_errors, get_num_objs_fn, saved_str):
    if expected_errors:
        for expected_error in expected_errors:
            self.assertContains(response, expected_error)
        # should be no new modules
        self.assertTrue(initial_objs_num == len(get_num_objs_fn()))
    else:
        # should be exactly one new module created
        self.assertTrue((initial_objs_num + 1) == len(get_num_objs_fn()))
        self.assertContains(response, saved_str)
