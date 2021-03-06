from django.http import HttpRequest
from django.test import TestCase

from tool.views.views_utils import *
from .utils import *


class GeneralSettingsTests(TestCase):
    def test_unauthenticated(self):
        response = go_to_settings(self)
        self.assertRedirects(response, '/tool/login/?next=/tool/settings/', status_code=302)

    def test_user_types(self):
        setup_data()

        # shouldn't see admin
        TestUtils.authenticate_student(self)
        response = go_to_settings(self)
        self.assertContains(response, 'Accessibility')
        self.assertContains(response, 'Attendance')
        self.assertContains(response, 'Account')
        self.assertNotContains(response, 'Admin')

        # should see all
        TestUtils.authenticate_staff(self)
        response = go_to_settings(self)
        self.assertContains(response, 'Accessibility')
        self.assertContains(response, 'Attendance')
        self.assertContains(response, 'Account')
        self.assertContains(response, 'Admin')


class ColourBlindSettingsTests(TestCase):
    def test_colourblind_options_set_value(self):
        student = TestUtils.authenticate_student(self)
        self.assertEqual(len(Settings.objects.all()), 0)

        # set colourblind false, settings should be created for user with false set
        set_colourblind_options(self, False)
        self.assertEqual(len(Settings.objects.all()), 1)
        user_settings = Settings.objects.get(user=student)
        self.assertFalse(user_settings.colourblind_opts_on)

        # set colourblind true, settings should be set to true for user's colourblind settings
        set_colourblind_options(self, True)
        self.assertEqual(len(Settings.objects.all()), 1)
        user_settings = Settings.objects.get(user=student)
        self.assertTrue(user_settings.colourblind_opts_on)

    def test_pass_fail_colours_returned(self):
        student = TestUtils.authenticate_student(self)
        request = HttpRequest()
        request.user = student

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
        TestUtils.authenticate_staff(self)

        test_colourblind_usage(self, go_to_module, self)
        test_colourblind_usage(self, go_to_course, self)
        test_colourblind_usage(self, go_to_lecturer, self)
        test_colourblind_usage(self, go_to_student, self)
        test_colourblind_usage(self, go_to_lecture, self)


def set_colourblind_options(self, set_value):
    value = "on" if set_value else ""
    return self.client.post(reverse('tool:settings'), {
        "colourblind-opts": value,
        "accessibility-submit": "Save"
    })


def test_colourblind_usage(self, method, arg):
    set_colourblind_options(self, False)
    test_colourblind_response_colours(self, method(arg), False)
    set_colourblind_options(self, True)
    test_colourblind_response_colours(self, method(arg), True)


def test_colourblind_response_colours(self, response, colourblind_colours_expected):
    if colourblind_colours_expected:
        self.assertContains(response, Colours.ORANGE.value)
        self.assertContains(response, Colours.BLUE.value)
        self.assertNotContains(response, Colours.RED.value)
        self.assertNotContains(response, Colours.GREEN.value)
    else:
        self.assertContains(response, Colours.RED.value)
        self.assertContains(response, Colours.GREEN.value)
        self.assertNotContains(response, Colours.ORANGE.value)
        self.assertNotContains(response, Colours.BLUE.value)


class AttendanceRangeSettingsTests(TestCase):
    def test_attendance_range_invalid_values(self):
        student = TestUtils.authenticate_student(self)
        self.assertEqual(len(Settings.objects.all()), 0)
        # should be saved as defaults as invalid values aren't set
        test_set_attendance_range(self, student, 35, '', 85, 25, 50, 75,
                                  'Attendance ranges must have a value')

        test_set_attendance_range(self, student, 1, 2, 'c', 25, 50, 75,
                                  'Attendance ranges must be whole numbers')

        test_set_attendance_range(self, student, -10, 65, 85, 25, 50, 75,
                                  'Attendance range 1 must be greater than 0')

        test_set_attendance_range(self, student, 55, 35, 10, 25, 50, 75,
                                  'Attendance range 2 must be greater than range 1')

        test_set_attendance_range(self, student, 45, 85, 65, 25, 50, 75,
                                  'Attendance range 3 must be greater than range 2')

        test_set_attendance_range(self, student, 45, 65, 105, 25, 50, 75,
                                  'Attendance range 3 must be less than 100')

    def test_attendance_range_valid_values(self):
        student = TestUtils.authenticate_student(self)
        self.assertEqual(len(Settings.objects.all()), 0)
        test_set_attendance_range(self, student, 45, 65, 85, 45, 65, 85, '')

    def test_attendance_range_usages(self):
        setup_data()
        TestUtils.authenticate_staff(self)

        # default settings
        test_attendance_range_usage(self, go_to_module, self, True, False, True, True)
        test_attendance_range_usage(self, go_to_course, self, True, False, True, True)
        test_attendance_range_usage(self, go_to_lecturer, self, True, False, True, True)
        test_attendance_range_usage(self, go_to_student, self, True, False, True, True)

        # modified range settings
        set_attendance_range_settings(self, 20, 75, 85)
        test_attendance_range_usage(self, go_to_module, self, True, True, False, True)
        test_attendance_range_usage(self, go_to_course, self, True, True, False, True)
        test_attendance_range_usage(self, go_to_lecturer, self, True, True, False, True)
        test_attendance_range_usage(self, go_to_student, self, True, True, False, True)


def set_attendance_range_settings(self, range_1, range_2, range_3):
    return self.client.post(reverse('tool:settings'), {
        "attendance-range-1": range_1,
        "attendance-range-2": range_2,
        "attendance-range-3": range_3,
        "attendance-submit": "Save"
    }, follow=True)


def test_set_attendance_range(self, user,
                              range_1, range_2, range_3,
                              expected_range_1, expected_range_2, expected_range_3,
                              expected_error_msg):
    response = set_attendance_range_settings(self, range_1, range_2, range_3)
    self.assertEqual(len(Settings.objects.all()), 1)
    user_settings = Settings.objects.get(user=user)

    self.assertEqual(user_settings.attendance_range_1_cap, expected_range_1)
    self.assertEqual(user_settings.attendance_range_2_cap, expected_range_2)
    self.assertEqual(user_settings.attendance_range_3_cap, expected_range_3)

    if expected_error_msg:
        self.assertContains(response, expected_error_msg)


def test_attendance_range_usage(self, method, arg,
                                range_1_expected, range_2_expected,
                                range_3_expected, range_4_expected):
    set_colourblind_options(self, False)
    test_attendance_range_response_colours(self, method(arg), False,
                                           range_1_expected, range_2_expected,
                                           range_3_expected, range_4_expected)
    set_colourblind_options(self, True)
    test_attendance_range_response_colours(self, method(arg), True,
                                           range_1_expected, range_2_expected,
                                           range_3_expected, range_4_expected)


def test_attendance_range_response_colours(self, response, colourblind_colours_expected,
                                           range_1_expected, range_2_expected,
                                           range_3_expected, range_4_expected):
    if colourblind_colours_expected:
        if range_1_expected:
            self.assertContains(response, Colours.ORANGE.value)
        if range_2_expected:
            self.assertContains(response, Colours.YELLOW.value)
        if range_3_expected:
            self.assertContains(response, Colours.BLUE_LIGHT.value)
        if range_4_expected:
            self.assertContains(response, Colours.BLUE.value)

        self.assertNotContains(response, Colours.RED.value)
        self.assertNotContains(response, Colours.ORANGE_LIGHT.value)
        self.assertNotContains(response, Colours.GREEN_LIGHT.value)
        self.assertNotContains(response, Colours.GREEN.value)
    else:
        if range_1_expected:
            self.assertContains(response, Colours.RED.value)
        if range_2_expected:
            self.assertContains(response, Colours.ORANGE_LIGHT.value)
        if range_3_expected:
            self.assertContains(response, Colours.GREEN_LIGHT.value)
        if range_4_expected:
            self.assertContains(response, Colours.GREEN.value)

        self.assertNotContains(response, Colours.ORANGE.value)
        self.assertNotContains(response, Colours.YELLOW.value)
        self.assertNotContains(response, Colours.BLUE_LIGHT.value)
        self.assertNotContains(response, Colours.BLUE.value)


def go_to_settings(self):
    return self.client.get(reverse('tool:settings'))


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
    student = TestUtils.create_student('authteststudent')
    staff = TestUtils.create_staff('authteststaff')
    module = TestUtils.create_module('COM101', 'COM101-crn')
    course = TestUtils.create_course('Course Code')
    module.students.add(student)
    staff.modules.add(module)
    staff.courses.add(course)
    course.modules.add(module)
    lec1 = TestUtils.create_lecture(module, 'id1')
    lec2 = TestUtils.create_lecture(module, 'id2')
    TestUtils.create_attendance(student, lec1, True)
    TestUtils.create_attendance(student, lec2, False)
