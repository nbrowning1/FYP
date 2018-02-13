import datetime

from django.http import HttpRequest
from django.test import TestCase

from tool.views.views_utils import *


class GeneralSettingsTests(TestCase):
    def test_unauthenticated(self):
        response = go_to_settings(self)
        self.assertRedirects(response, '/tool/login/?next=/tool/settings/', status_code=302)


class ColourBlindSettingsTests(TestCase):
    def test_colourblind_options_set_value(self):
        student = create_or_get_student('authteststudent')
        authenticate_student(self)
        self.assertEqual(len(Settings.objects.all()), 0)

        # set colourblind false, settings should be created for user with false set
        set_colourblind_options(self, False)
        self.assertEqual(len(Settings.objects.all()), 1)
        user_settings = Settings.objects.get(user=student.user)
        self.assertFalse(user_settings.colourblind_opts_on)

        # set colourblind true, settings should be set to true for user's colourblind settings
        set_colourblind_options(self, True)
        self.assertEqual(len(Settings.objects.all()), 1)
        user_settings = Settings.objects.get(user=student.user)
        self.assertTrue(user_settings.colourblind_opts_on)

    def test_pass_fail_colours_returned(self):
        student = create_or_get_student('authteststudent')
        authenticate_student(self)
        request = HttpRequest()
        request.user = student.user

        # no settings - default
        colours = ViewsUtils().get_pass_fail_colours_2_tone(request)
        self.assertEqual(colours, [Colours.RED.value, Colours.GREEN.value])

        set_colourblind_options(self, False)
        colours = ViewsUtils().get_pass_fail_colours_2_tone(request)
        self.assertEqual(colours, [Colours.RED.value, Colours.GREEN.value])

        set_colourblind_options(self, True)
        colours = ViewsUtils().get_pass_fail_colours_2_tone(request)
        self.assertEqual(colours, [Colours.ORANGE.value, Colours.BLUE.value])

    def test_colourblind_usages(self):
        setup_data()
        authenticate_staff(self)

        test_colourblind_usage(self, go_to_module, self)
        test_colourblind_usage(self, go_to_course, self)
        test_colourblind_usage(self, go_to_lecturer, self)
        test_colourblind_usage(self, go_to_student, self)
        test_colourblind_usage(self, go_to_lecture, self)


def test_colourblind_usage(self, method, arg):
    set_colourblind_options(self, False)
    test_response_colours(self, method(arg), False)
    set_colourblind_options(self, True)
    test_response_colours(self, method(arg), True)


def test_response_colours(self, response, colourblind_colours_expected):
    if colourblind_colours_expected:
        self.assertContains(response, Colours.BLUE.value)
        self.assertContains(response, Colours.ORANGE.value)
        self.assertNotContains(response, Colours.GREEN.value)
        self.assertNotContains(response, Colours.RED.value)
    else:
        self.assertContains(response, Colours.GREEN.value)
        self.assertContains(response, Colours.RED.value)
        self.assertNotContains(response, Colours.BLUE.value)
        self.assertNotContains(response, Colours.ORANGE.value)


def authenticate_student(self):
    self.client.login(username='authteststudent', password='12345')


def authenticate_staff(self):
    self.client.login(username='authteststaff', password='12345')


def go_to_settings(self):
    return self.client.get(reverse('tool:settings'))


def set_colourblind_options(self, set_value):
    value = "on" if set_value else ""
    return self.client.post(reverse('tool:settings'), {
        "colourblind-opts": value
    })


def go_to_module(self):
    url = reverse('tool:module', kwargs={'module_id': 1})
    return self.client.get(url)


def go_to_course(self):
    url = reverse('tool:course', kwargs={'course_id': 1})
    return self.client.get(url)


def go_to_lecturer(self):
    url = reverse('tool:lecturer', kwargs={'lecturer_id': 1})
    return self.client.get(url)


def go_to_student(self):
    url = reverse('tool:student', kwargs={'student_id': 1})
    return self.client.get(url)


def go_to_lecture(self):
    url = reverse('tool:lecture', kwargs={'lecture_id': 1})
    return self.client.get(url)


def setup_data():
    student = create_or_get_student('authteststudent')
    staff = create_or_get_staff('authteststaff')
    module = create_module('COM101')
    course = create_or_get_course('Course Code')
    module.students.add(student)
    staff.modules.add(module)
    staff.courses.add(course)
    course.modules.add(module)
    lec1 = create_lecture(module, 'id1')
    lec2 = create_lecture(module, 'id2')
    create_attendance(student, lec1, True)
    create_attendance(student, lec2, False)


def create_or_get_course(course_code):
    try:
        course = Course.objects.get(course_code=course_code)
        return course
    except Course.DoesNotExist:
        course = Course(course_code=course_code)
        course.save()
        return course


def create_or_get_student(username):
    try:
        return Student.objects.get(user__username=username)
    except Student.DoesNotExist:
        user = User.objects.create_user(username=username, password='12345')
        course = create_or_get_course('Course Code')
        student = Student(user=user, course=course)
        student.save()
        return student


def create_or_get_staff(username):
    try:
        return Staff.objects.get(user__username=username)
    except Staff.DoesNotExist:
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


def create_attendance(student, lecture, attended):
    attendance = StudentAttendance(student=student, lecture=lecture, attended=attended)
    attendance.save()
    return attendance
