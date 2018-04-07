from django.test import TestCase
from django.urls import reverse

from .utils import *


class SingleModuleViewTests(TestCase):
    def test_single_module_view_staff(self):
        TestUtils.authenticate_staff(self)
        test_valid_module_view(self)

    def test_single_module_view_student(self):
        user = TestUtils.authenticate_student(self)
        this_student = Student.objects.get(user=user)
        test_valid_module_view(self, this_student=this_student)

    def test_module_unauthenticated(self):
        TestUtils.create_module('COM101', 'COM101-crn')

        # check module that exists
        response = go_to_module(self, 1)
        self.assertRedirects(response, '/tool/login/?next=/tool/modules/1', status_code=302)

        # check module that doesnt exist - should be same response
        response = go_to_module(self, 10)
        self.assertRedirects(response, '/tool/login/?next=/tool/modules/10', status_code=302)

    def test_nonexistent_module(self):
        TestUtils.authenticate_staff(self)

        TestUtils.create_module('COM101', 'COM101-crn')
        response = go_to_module(self, 10)
        self.assertEqual(response.status_code, 404)


class SingleCourseViewTests(TestCase):
    def test_single_course_view_staff(self):
        TestUtils.authenticate_staff(self)
        test_valid_course_view(self, True)

    def test_single_course_view_student(self):
        TestUtils.authenticate_student(self)
        test_valid_course_view(self, False)

    def test_course_unauthenticated(self):
        TestUtils.create_course('Course Code')

        # check course that exists
        response = go_to_course(self, 1)
        self.assertRedirects(response, '/tool/login/?next=/tool/courses/1', status_code=302)

        # check course that doesnt exist - should be same response
        response = go_to_course(self, 10)
        self.assertRedirects(response, '/tool/login/?next=/tool/courses/10', status_code=302)

    def test_nonexistent_course(self):
        TestUtils.authenticate_staff(self)

        TestUtils.create_course('Course Code')
        response = go_to_course(self, 10)
        self.assertEqual(response.status_code, 404)


class SingleLecturerViewTests(TestCase):
    def test_single_lecturer_view_staff(self):
        user = TestUtils.authenticate_staff(self)
        this_lecturer = Staff.objects.get(user=user)
        test_valid_lecturer_view(self, False, this_lecturer=this_lecturer)

    def test_single_lecturer_view_student(self):
        user = TestUtils.authenticate_student(self)
        this_student = Student.objects.get(user=user)
        test_valid_lecturer_view(self, True, this_student=this_student)

    def test_lecturer_unauthenticated(self):
        TestUtils.create_staff('e00123456')

        # check lecturer that exists
        response = go_to_lecturer(self, 1)
        self.assertRedirects(response, '/tool/login/?next=/tool/lecturers/1', status_code=302)

        # check lecturer that doesnt exist - should be same response
        response = go_to_lecturer(self, 10)
        self.assertRedirects(response, '/tool/login/?next=/tool/lecturers/10', status_code=302)

    def test_nonexistent_lecturer(self):
        TestUtils.authenticate_staff(self)

        TestUtils.create_staff('e00123456')
        response = go_to_lecturer(self, 10)
        self.assertEqual(response.status_code, 404)


class SingleStudentViewTests(TestCase):
    def test_single_student_view_staff(self):
        TestUtils.authenticate_staff(self)
        test_valid_student_view(self, False)

    def test_single_student_view_student(self):
        user = TestUtils.authenticate_student(self)
        this_student = Student.objects.get(user=user)
        test_valid_student_view(self, True, this_student=this_student)

    def test_student_unauthenticated(self):
        TestUtils.create_student('B00123456')

        # check module that exists
        response = go_to_student(self, 1)
        self.assertRedirects(response, '/tool/login/?next=/tool/students/1', status_code=302)

        # check module that doesnt exist - should be same response
        response = go_to_student(self, 10)
        self.assertRedirects(response, '/tool/login/?next=/tool/students/10', status_code=302)

    def test_nonexistent_student(self):
        TestUtils.authenticate_staff(self)

        TestUtils.create_student('B00123456')
        response = go_to_student(self, 10)
        self.assertEqual(response.status_code, 404)


class SingleLectureViewTests(TestCase):
    def test_single_lecture_view_staff(self):
        TestUtils.authenticate_staff(self)
        test_valid_lecture_view(self, False)

    def test_single_lecture_view_student(self):
        user = TestUtils.authenticate_student(self)
        this_student = Student.objects.get(user=user)
        test_valid_lecture_view(self, True, this_student=this_student)

    def test_lecture_unauthenticated(self):
        TestUtils.create_student('B00123456')

        # check module that exists
        response = go_to_lecture(self, 1)
        self.assertRedirects(response, '/tool/login/?next=/tool/lectures/1', status_code=302)

        # check module that doesnt exist - should be same response
        response = go_to_lecture(self, 10)
        self.assertRedirects(response, '/tool/login/?next=/tool/lectures/10', status_code=302)

    def test_nonexistent_lecture(self):
        TestUtils.authenticate_staff(self)

        TestUtils.create_student('B00123456')
        response = go_to_lecture(self, 10)
        self.assertEqual(response.status_code, 404)


def test_valid_module_view(self, **kwargs):
    is_student = False
    if 'this_student' in kwargs:
        setup_data(kwargs['this_student'], None)
        is_student = True
    else:
        setup_data(None, None)

    # should only see information relating to COM101 module - first created
    response = go_to_module(self, 1)
    self.assertContains(response, 'COM101')
    self.assertNotContains(response, 'COM102')
    if not is_student:
        self.assertNotContains(response, 'B00123456')
        self.assertContains(response, 'B00987654')
        self.assertContains(response, "Student 1 Module 1 Feedback")
        self.assertContains(response, "Student 2 Module 1 Feedback")
        self.assertNotContains(response, "Student 1 Module 2 Feedback")
        # staff can't give feedback for module
        self.assertNotContains(response, 'Give Feedback')
    else:
        self.assertNotContains(response, 'B00123456')
        self.assertNotContains(response, 'B00987654')
        self.assertNotContains(response, "Student 1 Module 1 Feedback")
        self.assertContains(response, "Student 2 Module 1 Feedback")
        self.assertNotContains(response, "Student 1 Module 2 Feedback")
        self.assertContains(response, 'Give Feedback')
    self.assertContains(response, 'Session 1')
    self.assertContains(response, 'Session 2')
    self.assertContains(response, 'Dec. 1, 2017')

    # should only see information relating to COM102 module - second created
    response = go_to_module(self, 2)
    if not is_student:
        self.assertNotContains(response, 'COM101')
        self.assertContains(response, 'COM102')
        self.assertContains(response, 'No attendances are available.')
        self.assertNotContains(response, 'B00123456')
        self.assertNotContains(response, 'B00987654')
        self.assertNotContains(response, 'Session 1')
        self.assertNotContains(response, 'Session 2')
        self.assertNotContains(response, 'Dec. 1, 2017')
        self.assertNotContains(response, "Student 1 Module 1 Feedback")
        self.assertNotContains(response, "Student 2 Module 1 Feedback")
        self.assertContains(response, "Student 1 Module 2 Feedback")
    else:
        self.assertEqual(response.status_code, 404)

    response = go_to_module(self, 3)
    if not is_student:
        self.assertContains(response, 'No attendances are available.')
        self.assertContains(response, 'No feedback is available.')
    else:
        self.assertEqual(response.status_code, 404)


def test_valid_course_view(self, is_staff):
    setup_data(None, None)

    response = go_to_course(self, 1)
    # should only see if staff
    if is_staff:
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM102')
    else:
        self.assertEqual(response.status_code, 404)

    response = go_to_course(self, 2)
    self.assertEqual(response.status_code, 404)


def test_valid_lecturer_view(self, is_student, **kwargs):
    if 'this_lecturer' in kwargs:
        setup_data(None, kwargs['this_lecturer'])
    else:
        setup_data(None, None)

    # should only see information relating to e00123456 lecturer - first created
    response = go_to_lecturer(self, 1)
    if is_student:
        self.assertEqual(response.status_code, 404)
    else:
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM102')
        self.assertContains(response, '50.00%')
        if 'this_lecturer' in kwargs:
            self.assertContains(response, 'test')
        else:
            self.assertContains(response, 'e00123456')
        self.assertNotContains(response, 'e00987654')

    # should only see information relating to e00987654 lecturer - second created
    response = go_to_lecturer(self, 2)
    if is_student:
        self.assertEqual(response.status_code, 404)
    else:
        self.assertContains(response, 'No attendances are available.')


def test_valid_student_view(self, is_student, **kwargs):
    if 'this_student' in kwargs:
        setup_data(kwargs['this_student'], None)
    else:
        setup_data(None, None)

    # should only see information relating to B00123456 student - first created (or this user if student)
    response = go_to_student(self, 1)

    if not is_student:
        self.assertNotContains(response, 'COM101')
        self.assertNotContains(response, 'COM102')
        self.assertContains(response, 'No attendances are available.')
        self.assertContains(response, 'B00123456')
        self.assertNotContains(response, 'B00987654')
        self.assertNotContains(response, 'Session 1')
        self.assertNotContains(response, 'Session 2')
        self.assertNotContains(response, 'Dec. 1, 2017')
    else:
        # student looking at their own view ('test')
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM102')
        self.assertContains(response, 'test')
        self.assertNotContains(response, 'B00987654')
        self.assertContains(response, 'Session 1')
        self.assertContains(response, 'Session 2')
        self.assertContains(response, 'Dec. 1, 2017')

    # should only see information relating to B00987654 student - second created
    response = go_to_student(self, 2)
    if not is_student:
        self.assertContains(response, 'COM101')
        self.assertNotContains(response, 'COM102')
        self.assertNotContains(response, 'B00123456')
        self.assertContains(response, 'B00987654')
        self.assertContains(response, 'Session 1')
        self.assertContains(response, 'Session 2')
        self.assertContains(response, 'Dec. 1, 2017')
    else:
        self.assertEqual(response.status_code, 404)


def test_valid_lecture_view(self, is_student, **kwargs):
    if 'this_student' in kwargs:
        setup_data(kwargs['this_student'], None)
    else:
        setup_data(None, None)

    module3 = TestUtils.create_module('COM333', 'COM333-crn')
    student3 = TestUtils.create_student('B00555555')
    lecture3 = TestUtils.create_lecture(module3, 'Session 3')
    module3.students.add(student3)
    TestUtils.create_attendance(student3, lecture3, True)

    # should only see information relating to Session 1 lecture - first created
    response = go_to_lecture(self, 1)
    self.assertContains(response, 'Session 1')
    self.assertNotContains(response, 'Session 2')
    self.assertNotContains(response, 'Session 3')
    self.assertNotContains(response, 'B00123456')
    if not is_student:
        self.assertContains(response, 'B00987654')
    else:
        self.assertContains(response, 'test')

    # should only see information relating to Session 2 lecture - second created
    response = go_to_lecture(self, 2)
    if not is_student:
        self.assertNotContains(response, 'No attendances are available.')
    else:
        self.assertNotContains(response, 'Session 1')
        self.assertContains(response, 'Session 2')
        self.assertNotContains(response, 'Session 3')
        self.assertNotContains(response, 'B00123456')
        self.assertContains(response, 'test')

    # should only see information relating to Session 3 lecture - second created
    response = go_to_lecture(self, 3)
    if not is_student:
        self.assertNotContains(response, 'Session 1')
        self.assertNotContains(response, 'Session 2')
        self.assertContains(response, 'Session 3')
        self.assertContains(response, 'B00555555')
    else:
        self.assertEqual(response.status_code, 404)


def setup_data(this_student, this_lecturer):
    module1 = TestUtils.create_module('COM101', 'COM101-crn')
    module2 = TestUtils.create_module('COM102', 'COM102-crn')
    TestUtils.create_module('COM103', 'COM103-crn')
    student1 = TestUtils.create_student('B00123456')
    if this_student:
        student2 = this_student
    else:
        TestUtils.create_student('B00987654')
        student2 = Student.objects.get(user__username='B00987654')

    course = Course.objects.get(course_code='Course Code')
    course.modules.add(module1)

    if this_lecturer:
        lecturer1 = this_lecturer
    else:
        TestUtils.create_staff('e00123456')
        lecturer1 = Staff.objects.get(user__username='e00123456')
    TestUtils.create_staff('e00987654')
    lecture1 = TestUtils.create_lecture(module1, 'Session 1')
    lecture2 = TestUtils.create_lecture(module1, 'Session 2')
    module1.students.add(student2)
    lecturer1.modules.add(module1)
    TestUtils.create_attendance(student2, lecture1, True)
    TestUtils.create_attendance(student2, lecture2, False)
    TestUtils.create_feedback(student1, module1, "Student 1 Module 1 Feedback", True)
    TestUtils.create_feedback(student2, module1, "Student 2 Module 1 Feedback", False)
    TestUtils.create_feedback(student1, module2, "Student 1 Module 2 Feedback", True)


def go_to_module(self, module_id):
    url = reverse('tool:module', kwargs={'module_id': module_id})
    return self.client.get(url)


def go_to_course(self, course_id):
    url = reverse('tool:course', kwargs={'course_id': course_id})
    return self.client.get(url)


def go_to_lecturer(self, lecturer_id):
    url = reverse('tool:lecturer', kwargs={'lecturer_id': lecturer_id})
    return self.client.get(url)


def go_to_student(self, student_id):
    url = reverse('tool:student', kwargs={'student_id': student_id})
    return self.client.get(url)


def go_to_lecture(self, lecture_id):
    url = reverse('tool:lecture', kwargs={'lecture_id': lecture_id})
    return self.client.get(url)
