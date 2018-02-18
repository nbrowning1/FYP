from django.test import TestCase
from django.urls import reverse

from ..models import *


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
        authenticate_student(self)
        response = go_to_admin_create_module(self)
        self.assertEqual(response.status_code, 404)
        response = go_to_admin_create_course(self)
        self.assertEqual(response.status_code, 404)
        response = go_to_admin_create_student(self)
        self.assertEqual(response.status_code, 404)

        # staff should be able to see
        authenticate_staff(self)
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

    def test_invalid_student(self):
        test_student_create_view(self, 'E00112233', '', '', 'test', '1-', -1,
                                 ['Must be a valid student code e.g. B00112233'])

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


def go_to_admin_create_module(self):
    url = reverse('tool:admin_create_module')
    return self.client.get(url)


def go_to_admin_create_course(self):
    url = reverse('tool:admin_create_course')
    return self.client.get(url)


def go_to_admin_create_student(self):
    url = reverse('tool:admin_create_student')
    return self.client.get(url)


def authenticate_admin(self):
    user = User.objects.create_superuser(username='test', password='12345', email='test@mail.com')
    self.client.login(username='test', password='12345')
    return user


def authenticate_student(self):
    user = create_student('teststudent').user
    self.client.login(username='teststudent', password='12345')
    return user


def authenticate_staff(self):
    user = create_staff('teststaff').user
    self.client.login(username='teststaff', password='12345')
    return user


def submit_create_module(self, module_code, module_crn):
    authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_module'),
                            {'module_code': module_code,
                             'module_crn': module_crn}, follow=True)


def submit_create_course(self, course_code):
    authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_course'),
                            {'course_code': course_code}, follow=True)


def submit_create_student(self, username, first_name, last_name, email, device_id, course_id):
    authenticate_staff(self)
    return self.client.post(reverse('tool:admin_create_student'),
                            {'username': username,
                             'first_name': first_name,
                             'last_name': last_name,
                             'email': email,
                             'device_id': device_id,
                             'course': course_id}, follow=True)


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


def create_course(course_code):
    try:
        course = Course.objects.get(course_code=course_code)
        return course
    except Course.DoesNotExist:
        course = Course(course_code=course_code)
        course.save()
        return course


def create_student(username):
    try:
        return Student.objects.get(user__username=username)
    except Student.DoesNotExist:
        user = User.objects.create_user(username=username, password='12345')
        course = create_course('Course Code')
        student = Student(user=user, course=course)
        student.save()
        return student


def create_staff(username):
    try:
        return Staff.objects.get(user__username=username)
    except Staff.DoesNotExist:
        user = User.objects.create_user(username=username, password='12345')
        staff = Staff(user=user)
        staff.save()
        return staff
