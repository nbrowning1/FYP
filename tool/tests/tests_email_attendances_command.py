import datetime

from django.core import mail
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from django.contrib.auth.models import User
from ..models import Student, Staff, Module, Lecture, StudentAttendance


class InitTestDataTest(TestCase):
    # testing ALL data is loaded from fresh DB, and subsequent load doesnt add anything
    def test_admin_email(self):
        setup_test_data()
        self.assertEqual(len(mail.outbox), 0)
        call_command('email_attendances', '--admins', '--weekly')
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Attendance report')
        print(mail.outbox[0].body)


def setup_test_data():
    User.objects.create_superuser(username='test', password='12345', email='test@mail.com')

    module1 = Module(module_code='COM101')
    module1.save()
    module2 = Module(module_code='COM202')
    module2.save()

    today = datetime.date.today()
    last_week_date = today - datetime.timedelta(weeks=1)
    yesterday_date = today - datetime.timedelta(days=1)
    lecture1 = Lecture(module=module1, session_id='id1', date=last_week_date)
    lecture1.save()
    lecture2 = Lecture(module=module2, session_id='id2', date=yesterday_date)
    lecture2.save()