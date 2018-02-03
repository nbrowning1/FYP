import datetime
from io import StringIO

from django.core import mail
from django.core.management import call_command
from django.test import TestCase

from ..models import *


class EmailAttendanceReportTest(TestCase):
    def test_admin_weekly_report(self):
        setup_test_data_weekly()
        self.assertEqual(len(mail.outbox), 0)
        call_command('email_attendances', '--admins', '--weekly')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Attendance report')
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], 'user1@mail.com')
        print(mail.outbox[0].body)

        # should only see module containing lectures for this week (COM202)
        self.assertNotIn('COM101', mail.outbox[0].body)
        self.assertIn('COM202 - COM202-1: 75.0% Attendance', mail.outbox[0].body)

        # should only see lectures for that module in this week
        self.assertNotIn('id1', mail.outbox[0].body)
        self.assertNotIn('id2', mail.outbox[0].body)
        today_str = get_django_template_format_date(get_today_date())
        self.assertIn('id3 -- {}: 50.0% Attendance'.format(today_str), mail.outbox[0].body)
        self.assertIn('id4 -- {}: 100.0% Attendance'.format(today_str), mail.outbox[0].body)

    def test_admin_monthly_report(self):
        setup_test_data_monthly()
        self.assertEqual(len(mail.outbox), 0)
        call_command('email_attendances', '--admins', '--monthly', '--test-date=2018-01-31')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Attendance report')
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], 'user1@mail.com')
        print(mail.outbox[0].body)

        self.assertIn('COM101 - COM101-1: 100.0% Attendance', mail.outbox[0].body)
        self.assertIn('COM202 - COM202-1: 50.0% Attendance', mail.outbox[0].body)

        first_date_str = get_django_template_format_date(get_monthly_first_date())
        second_date_str = get_django_template_format_date(get_monthly_second_date())
        self.assertIn('id1 -- {}: 100.0% Attendance'.format(first_date_str), mail.outbox[0].body)
        self.assertIn('id2 -- {}: 0.0% Attendance'.format(first_date_str), mail.outbox[0].body)
        self.assertIn('id3 -- {}: 50.0% Attendance'.format(second_date_str), mail.outbox[0].body)
        self.assertIn('id4 -- {}: 100.0% Attendance'.format(second_date_str), mail.outbox[0].body)

    def test_staff_report(self):
        setup_test_data_weekly()
        self.assertEqual(len(mail.outbox), 0)
        call_command('email_attendances', '--staff', '--weekly')
        # 2 emails because 2 lecturers
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'Attendance report')
        self.assertEqual(mail.outbox[1].subject, 'Attendance report')
        # sent to both lecturers
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], 'teststaff1@mail.com')
        self.assertEqual(len(mail.outbox[1].to), 1)
        self.assertEqual(mail.outbox[1].to[0], 'teststaff2@mail.com')
        print(mail.outbox[0].body)
        print(mail.outbox[1].body)

        # lecturer should see modules linked to them, and lectures for time range
        lecturer1_email_body = mail.outbox[0].body
        self.assertNotIn('id1', lecturer1_email_body)
        self.assertNotIn('id2', lecturer1_email_body)
        today_str = get_django_template_format_date(get_today_date())
        self.assertIn('id3 -- {}: 50.0% Attendance'.format(today_str), lecturer1_email_body)
        self.assertIn('id4 -- {}: 100.0% Attendance'.format(today_str), lecturer1_email_body)
        self.assertNotIn('COM101', lecturer1_email_body)
        self.assertIn('COM202 - COM202-1: 75.0% Attendance', lecturer1_email_body)

        # should see nothing - lecturer has no modules / courses linked
        lecturer2_email_body = mail.outbox[1].body
        self.assertNotIn('id1', lecturer2_email_body)
        self.assertNotIn('id2', lecturer2_email_body)
        self.assertNotIn('id3', lecturer2_email_body)
        self.assertNotIn('id4', lecturer2_email_body)
        self.assertNotIn('COM101', lecturer2_email_body)
        self.assertNotIn('COM202', lecturer2_email_body)
        self.assertIn('No attendances to report.', lecturer2_email_body)

    def test_student_report(self):
        setup_test_data_weekly()
        self.assertEqual(len(mail.outbox), 0)
        call_command('email_attendances', '--students', '--weekly')
        # 2 emails because 2 students
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].subject, 'Attendance report')
        self.assertEqual(mail.outbox[1].subject, 'Attendance report')
        # sent to both lecturers
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(mail.outbox[0].to[0], 'teststudent1@mail.com')
        self.assertEqual(len(mail.outbox[1].to), 1)
        self.assertEqual(mail.outbox[1].to[0], 'teststudent2@mail.com')
        print(mail.outbox[0].body)
        print(mail.outbox[1].body)

        student1_email_body = mail.outbox[0].body
        self.assertNotIn('id1', student1_email_body)
        self.assertNotIn('id2', student1_email_body)
        self.assertNotIn('id3', student1_email_body)
        self.assertNotIn('id4', student1_email_body)
        self.assertNotIn('COM101', student1_email_body)
        self.assertIn('COM202 - COM202-1: 100.0% Attendance', student1_email_body)

        student2_email_body = mail.outbox[1].body
        self.assertNotIn('id1', student2_email_body)
        self.assertNotIn('id2', student2_email_body)
        self.assertNotIn('id3', student2_email_body)
        self.assertNotIn('id4', student2_email_body)
        self.assertNotIn('COM101', student2_email_body)
        self.assertIn('COM202 - COM202-1: 50.0% Attendance', student2_email_body)

    def test_all_report(self):
        setup_test_data_weekly()
        self.assertEqual(len(mail.outbox), 0)
        call_command('email_attendances', '--all-users', '--weekly')
        # everybody - 1 admin, 2 staff, 2 students
        self.assertEqual(len(mail.outbox), 5)
        # sent to both lecturers
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(len(mail.outbox[1].to), 1)
        self.assertEqual(len(mail.outbox[2].to), 1)
        self.assertEqual(len(mail.outbox[3].to), 1)
        self.assertEqual(len(mail.outbox[4].to), 1)

    def test_test_only(self):
        setup_test_data_weekly()
        self.assertEqual(len(mail.outbox), 0)
        out = StringIO()
        call_command('email_attendances', '--all-users', '--weekly', '--test-only', stdout=out)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn('TEST MODE, No emails will actually be sent.', out.getvalue())
        self.assertIn('Email sent to user1 <user1@mail.com>', out.getvalue())
        self.assertIn('Email sent to teststudent1 <teststudent1@mail.com>', out.getvalue())
        self.assertIn('Email sent to teststudent2 <teststudent2@mail.com>', out.getvalue())
        self.assertIn('Email sent to teststaff1 <teststaff1@mail.com>', out.getvalue())
        self.assertIn('Email sent to teststaff2 <teststaff2@mail.com>', out.getvalue())


def get_django_template_format_date(date):
    # return date in format to mimic django's template format e.g. "Jan. 1, 2018"
    return date.strftime('%b. ' + str(date.day) + ', %Y')


def get_today_date():
    return datetime.date.today()


def get_last_week_date():
    return get_today_date() - datetime.timedelta(weeks=1) - datetime.timedelta(days=1)


def setup_test_data_weekly():
    setup_test_data(get_last_week_date(), get_today_date())


def get_monthly_first_date():
    return datetime.date(2018, 1, 1)


def get_monthly_second_date():
    return datetime.date(2018, 1, 25)


def setup_test_data_monthly():
    setup_test_data(get_monthly_first_date(), get_monthly_second_date())


def setup_test_data(first_date, second_date):
    User.objects.create_superuser(username='user1', password='12345', email='user1@mail.com')

    course = Course(course_code='Course Code')
    course.save()

    student1 = Student(user=User.objects.create_user(username='teststudent1', email='teststudent1@mail.com'),
                       device_id='devID1', course=course)
    student1.save()
    student2 = Student(user=User.objects.create_user(username='teststudent2', email='teststudent2@mail.com'),
                       device_id='devID2', course=course)
    student2.save()

    module1 = Module(module_code='COM101', module_crn='COM101-1')
    module1.save()
    module1.students.add(student1)
    module1.students.add(student2)
    module2 = Module(module_code='COM202', module_crn='COM202-1')
    module2.save()
    module2.students.add(student1)
    module2.students.add(student2)

    lecture1 = Lecture(module=module1, session_id='id1', date=first_date)
    lecture1.save()
    lecture2 = Lecture(module=module2, session_id='id2', date=first_date)
    lecture2.save()
    lecture3 = Lecture(module=module2, session_id='id3', date=second_date)
    lecture3.save()
    lecture4 = Lecture(module=module2, session_id='id4', date=second_date)
    lecture4.save()

    lecturer1 = Staff(user=User.objects.create_user(username='teststaff1', email='teststaff1@mail.com'))
    lecturer1.save()
    lecturer1.modules.add(module2)
    lecturer1.courses.add(course)
    lecturer2 = Staff(user=User.objects.create_user(username='teststaff2', email='teststaff2@mail.com'))
    lecturer2.save()

    # lecture1 = 100% attendance, lecture2 = 0%, lecture3 = 50%, lecture4 = 100%
    StudentAttendance(student=student1, lecture=lecture1, attended=True).save()
    StudentAttendance(student=student1, lecture=lecture2, attended=False).save()
    StudentAttendance(student=student1, lecture=lecture3, attended=True).save()
    StudentAttendance(student=student1, lecture=lecture4, attended=True).save()

    StudentAttendance(student=student2, lecture=lecture1, attended=True).save()
    StudentAttendance(student=student2, lecture=lecture2, attended=False).save()
    StudentAttendance(student=student2, lecture=lecture3, attended=False).save()
    StudentAttendance(student=student2, lecture=lecture4, attended=True).save()


    # shouldn't see any of these
