from django.test import TestCase

from ..data_rows import AttendanceSessionRow, AttendanceRow
from ..models import *


class AttendanceSessionRowTest(TestCase):
    def test_valid_row(self):
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
                                     '31/01/2017\nSecond Session ID'])
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
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
                                     '31/01/2017 - Second Session ID'])
        self.assertEqual(data.get_error_message(),
                         'Expected newline to separate date and session id for: 31/01/2017 - Second Session ID at column 5')

    def test_row_invalid_date_format(self):
        # wrong formatting
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
                                     '31-01-2017\nSecond Session ID'])
        self.assertEqual(data.get_error_message(),
                         'Incorrect date format: 31-01-2017, should be DD/MM/YYYY at column 5')

        # totally incorrect
        data = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID', 'abc\nSecond Session ID'])
        self.assertEqual(data.get_error_message(), 'Incorrect date format: abc, should be DD/MM/YYYY at column 5')

    def test_row_empty(self):
        # fully empty
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID', ''])
        self.assertEqual(data.get_error_message(), 'Unexpected empty session data at column 5')

        # no date
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '\nFirst Session ID'])
        self.assertEqual(data.get_error_message(), 'Unexpected empty date at column 4')

        # empty date
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '     \nFirst Session ID'])
        self.assertEqual(data.get_error_message(), 'Unexpected empty date at column 4')

        # no session id
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\n'])
        self.assertEqual(data.get_error_message(),
                         'Expected newline to separate date and session id for: 01/01/2017\n at column 4')

        # empty session id
        data = AttendanceSessionRow(['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\n     '])
        self.assertEqual(data.get_error_message(), 'Unexpected empty session id at column 4')


class AttendanceRowTests(TestCase):
    def test_valid_row(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
             '31/01/2017\nSecond Session ID'])
        setup_test_student()
        data = setup_input_data_attendance(attendance_session_row, 'DeviceID', '', '', 'Y', 'N')

        self.assertEqual(data.get_error_message(), '')

        attendances = data.attendances
        self.assertEqual(len(attendances), 2)
        self.assertEqual(attendances[0].session.session_id, 'First Session ID')
        self.assertEqual(attendances[0].attended, True)
        self.assertEqual(attendances[1].session.session_id, 'Second Session ID')
        self.assertEqual(attendances[1].attended, False)

    def test_student_by_username_and_device_id(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
             '31/01/2017\nSecond Session ID'])
        setup_test_student()

        # device ID should find student
        data = setup_input_data_attendance(attendance_session_row, 'DeviceID', '', '', 'Y', 'N')
        self.assertEqual(data.get_error_message(), '')

        # student code / username should also find student
        data = setup_input_data_attendance(attendance_session_row, 'B00112233', '', '', 'Y', 'N')
        self.assertEqual(data.get_error_message(), '')

    def test_invalid_student_message(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
             '31/01/2017\nSecond Session ID'])
        setup_test_student()
        data = setup_input_data_attendance(attendance_session_row, 'DeviceID2', '', '', 'Y', 'N')

        self.assertEqual(data.get_error_message(), 'Unrecognised student: DeviceID2')

    def test_invalid_multiple(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
             '31/01/2017\nSecond Session ID'])
        setup_test_student()
        data = setup_input_data_attendance(attendance_session_row, 'DeviceID2', '', '', 'Y', 'donkey')

        self.assertEqual(data.get_error_message(),
                         'Unrecognised student: DeviceID2, Unrecognised attendance value for DeviceID2: donkey at column 5')

    def test_it_trims_spaces(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID',
             '31/01/2017\nSecond Session ID'])
        setup_test_student()
        data = setup_input_data_attendance(attendance_session_row, '  DeviceID ', '', '', 'Y ', ' N')

        self.assertEqual(data.get_error_message(), '')

        attendances = data.attendances
        self.assertEqual(len(attendances), 2)
        self.assertEqual(attendances[0].session.session_id, 'First Session ID')
        self.assertEqual(attendances[0].attended, True)
        self.assertEqual(attendances[1].session.session_id, 'Second Session ID')
        self.assertEqual(attendances[1].attended, False)

    def test_incorrect_column_count(self):
        attendance_session_row = AttendanceSessionRow(
            ['Device ID(s)', 'Last Name', 'First Name', '01/01/2017\nFirst Session ID'])
        setup_test_student()

        # too many
        data = setup_input_data_attendance(attendance_session_row, 'DeviceID', '', '', 'Y', 'N')
        self.assertEqual(data.get_error_message(),
                         'Number of data columns doesn\'t match number of sessions. Expected 1 but found 2')

        # too few
        data = setup_input_data_attendance(attendance_session_row, 'DeviceID')
        self.assertEqual(data.get_error_message(),
                         'Number of data columns doesn\'t match number of sessions. Expected 1 but found 0')


def setup_test_db():
    setup_test_student()

    staff_user = EncryptedUser.objects.create_user(username='S00112233', email='test@email.com',
                                                   password='CorrectHorseBatteryStaple')
    lecturer = Staff(user=staff_user)
    lecturer.save()

    module = Module(module_code='COM101')
    module.save()


def setup_test_student():
    student_user = EncryptedUser.objects.create_user(username='B00112233', email='test@email.com',
                                                     password='CorrectHorseBatteryStaple')
    course = Course(course_code='Course Code')
    course.save()
    student = Student(user=student_user, device_id='DeviceID', course=course)
    student.save()


def setup_input_data_attendance(attendance_session_row, *attendances):
    return AttendanceRow(attendance_session_row, attendances)
