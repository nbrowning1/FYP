import datetime

from django.test import TestCase

from django.contrib.auth.models import User
from ..models import Student, Staff, Module, Lecture, StudentAttendance

from ..data_rows import ModuleRow, StaffRow, AttendanceSessionRow, AttendanceRow


class ModuleRowTests(TestCase):
    def test_valid_row(self):
        setup_test_db('B00112233', 'S00112233', 'COM101')
        data = setup_input_data_module('COM101')
        self.assertEqual(data.get_error_message(), '')
        self.assertEqual(data.module, 'COM101')

    def test_invalid_module(self):
        setup_test_db('B00112233', 'S00112233', 'COM101')
        data = setup_input_data_module('COM999')
        self.assertEqual(data.get_error_message(), 'Unrecognised module: COM999')


class StaffRowTests(TestCase):
    def test_valid_row(self):
        setup_test_db('B00112233', 'S00112233', 'COM101')
        data = setup_input_data_staff('S00112233')
        self.assertEqual(data.get_error_message(), '')
        self.assertEqual(data.lecturer, 'S00112233')

    def test_invalid_module(self):
        setup_test_db('B00112233', 'S00112233', 'COM101')
        data = setup_input_data_staff('S00998877')
        self.assertEqual(data.get_error_message(), 'Unrecognised lecturer: S00998877')


class AttendanceSessionRowTest(TestCase):
    def test_valid_row(self):
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\nFirst Session ID', '31/01/2017\nSecond Session ID'])
        self.assertEqual(data.get_error_message(), '')

        self.assertEqual(len(data.sessions), 2)

        firstSession = data.sessions[0]
        secondSession = data.sessions[1]

        self.assertEqual(firstSession.date.day, 1)
        self.assertEqual(firstSession.date.month, 1)
        self.assertEqual(firstSession.date.year, 2017)
        self.assertEqual(firstSession.session_id, 'First Session ID')

        self.assertEqual(secondSession.date.day, 31)
        self.assertEqual(secondSession.date.month, 1)
        self.assertEqual(secondSession.date.year, 2017)
        self.assertEqual(secondSession.session_id, 'Second Session ID')

    def test_row_invalid_session_format(self):
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\nFirst Session ID', '31/01/2017 - Second Session ID'])
        self.assertEqual(data.get_error_message(),
                         'Expected newline to separate date and session id for: 31/01/2017 - Second Session ID at column 2')

    def test_row_invalid_date_format(self):
        # wrong formatting
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\nFirst Session ID', '31-01-2017\nSecond Session ID'])
        self.assertEqual(data.get_error_message(),
                         'Incorrect date format: 31-01-2017, should be DD/MM/YYYY at column 2')

        # totally incorrect
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\nFirst Session ID', 'abc\nSecond Session ID'])
        self.assertEqual(data.get_error_message(), 'Incorrect date format: abc, should be DD/MM/YYYY at column 2')

    def test_row_empty(self):
        # fully empty
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\nFirst Session ID', ''])
        self.assertEqual(data.get_error_message(), 'Unexpected empty session data at column 2')

        # no date
        data = AttendanceSessionRow(['Device ID(s)', '\nFirst Session ID'])
        self.assertEqual(data.get_error_message(), 'Unexpected empty date at column 1')

        # empty date
        data = AttendanceSessionRow(['Device ID(s)', '     \nFirst Session ID'])
        self.assertEqual(data.get_error_message(), 'Unexpected empty date at column 1')

        # no session id
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\n'])
        self.assertEqual(data.get_error_message(),
                         'Expected newline to separate date and session id for: 01/01/2017\n at column 1')

        # empty session id
        data = AttendanceSessionRow(['Device ID(s)', '01/01/2017\n     '])
        self.assertEqual(data.get_error_message(), 'Unexpected empty session id at column 1')


class AttendanceRowTests(TestCase):
    def test_valid_row(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', '01/01/2017\nFirst Session ID', '31/01/2017\nSecond Session ID'])
        setup_test_student('B00112233')
        data = setup_input_data_attendance(attendance_session_row, 'B00112233', 'Y', 'N')

        self.assertEqual(data.get_error_message(), '')

        attendances = data.attendances
        self.assertEqual(len(attendances), 2)
        self.assertEqual(attendances[0].session.session_id, 'First Session ID')
        self.assertEqual(attendances[0].attended, True)
        self.assertEqual(attendances[1].session.session_id, 'Second Session ID')
        self.assertEqual(attendances[1].attended, False)

    def test_invalid_student_message(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', '01/01/2017\nFirst Session ID', '31/01/2017\nSecond Session ID'])
        setup_test_student('B00112233')
        data = setup_input_data_attendance(attendance_session_row, 'B00000000', 'Y', 'N')

        self.assertEqual(data.get_error_message(), 'Unrecognised student: B00000000')

    def test_invalid_multiple(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', '01/01/2017\nFirst Session ID', '31/01/2017\nSecond Session ID'])
        setup_test_student('B00112233')
        data = setup_input_data_attendance(attendance_session_row, 'B00000000', 'Y', 'donkey')

        self.assertEqual(data.get_error_message(),
                         'Unrecognised student: B00000000, Unrecognised attendance value for B00000000: donkey at column 2')

    def test_it_trims_spaces(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', '01/01/2017\nFirst Session ID', '31/01/2017\nSecond Session ID'])
        setup_test_student('B00112233')
        data = setup_input_data_attendance(attendance_session_row, '  B00112233 ', 'Y ', ' N')

        self.assertEqual(data.get_error_message(), '')

        attendances = data.attendances
        self.assertEqual(len(attendances), 2)
        self.assertEqual(attendances[0].session.session_id, 'First Session ID')
        self.assertEqual(attendances[0].attended, True)
        self.assertEqual(attendances[1].session.session_id, 'Second Session ID')
        self.assertEqual(attendances[1].attended, False)

    def test_incorrect_column_count(self):
        attendance_session_row = AttendanceSessionRow(['Device ID(s)', '01/01/2017\nFirst Session ID'])
        setup_test_student('B00112233')

        # too many
        data = setup_input_data_attendance(attendance_session_row, 'B00112233', 'Y', 'N')
        self.assertEqual(data.get_error_message(),
                         'Number of data columns doesn\'t match number of sessions. Expected 1 but found 2')

        # too few
        data = setup_input_data_attendance(attendance_session_row, 'B00112233')
        self.assertEqual(data.get_error_message(),
                         'Number of data columns doesn\'t match number of sessions. Expected 1 but found 0')


def setup_test_db(student_code, staff_code, module_code):
    student_user = User.objects.create_user(username=student_code, email='test@email.com',
                                            password='CorrectHorseBatteryStaple')
    student = Student(user=student_user)
    student.save()

    staff_user = User.objects.create_user(username=staff_code, email='test@email.com',
                                          password='CorrectHorseBatteryStaple')
    lecturer = Staff(user=staff_user)
    lecturer.save()

    module = Module(module_code=module_code)
    module.save()


def setup_test_student(device_id):
    student_user = User.objects.create_user(username='test', email='test@email.com',
                                            password='CorrectHorseBatteryStaple')
    student = Student(user=student_user, device_id=device_id)
    student.save()


def setup_input_data_module(module_code):
    return ModuleRow([module_code])


def setup_input_data_staff(staff_code):
    return StaffRow([staff_code])


def setup_input_data_attendance(attendance_session_row, *attendances):
    return AttendanceRow(attendance_session_row, attendances)
