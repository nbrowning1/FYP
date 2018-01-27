import datetime
import types
from collections import OrderedDict
from enum import Enum

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template

from tool.models import *


class Command(BaseCommand):
    help = 'Emails attendance reports to users'

    def add_arguments(self, parser):
        parser.add_argument('--students',
                            action='store_true',
                            dest='students',
                            help='Report attendance to students')

        parser.add_argument('--staff',
                            action='store_true',
                            dest='staff',
                            help='Report attendance to staff')

        parser.add_argument('--admins',
                            action='store_true',
                            dest='admins',
                            help='Report attendance to admins')

        parser.add_argument('--all-users',
                            action='store_true',
                            dest='all-users',
                            help='Report attendance to all users')

        parser.add_argument('--weekly-report',
                            action='store_true',
                            dest='weekly-report',
                            help='Report attendance from start of week (Monday) to today')

        parser.add_argument('--monthly-report',
                            action='store_true',
                            dest='monthly-report',
                            help='Report attendance from start of month to today')

        parser.add_argument('--test-only',
                            action='store_true',
                            dest='test-only',
                            help='For testing purposes - won\'t actually send emails')

    def handle(self, *args, **options):
        users = []
        if options['all-users']:
            users = User.objects.all()
        elif options['students']:
            users = Student.objects.all()
        elif options['staff']:
            users = Staff.objects.all()
        elif options['admins']:
            users = User.objects.filter(is_staff=True)
        else:
            self.stdout.write(self.style.NOTICE('No users argument supplied. Use --help to get command options'))
            return

        time_period = None
        if options['weekly-report']:
            time_period = TimePeriod.WEEKLY
        elif options['monthly-report']:
            time_period = TimePeriod.MONTHLY
        else:
            self.stdout.write(self.style.NOTICE('No time period argument supplied. Use --help to get command options'))
            return

        test_only = False
        if options['test-only']:
            test_only = True
            self.stdout.write('TEST MODE, No emails will actually be sent.')

        # uses SMTP server specified in settings.py
        # get and open one connection for all emails
        connection = get_connection()
        connection.open()

        for user in users:
            email_attendance_report(self, user, time_period, connection, test_only)

        # cleaning up opened connection
        connection.close()


def email_attendance_report(self, user, time_period, connection, test_only):
    # should check whether user is actually active before processing on them
    # (won't send email if they don't have updates but cuts down on work done)

    context_dict = OrderedDict()

    # try student first
    try:
        student = Student.objects.get(user=user)
        context_dict = get_student_attendance_report(self, student, time_period)
    except Student.DoesNotExist:
        pass

    # fall back to staff
    try:
        lecturer = Staff.objects.get(user=user)
        context_dict = get_staff_attendance_report(self, lecturer, time_period)
    except Staff.DoesNotExist:
        pass

    # finally check if admin user
    if user.is_staff:
        context_dict = get_admin_attendance_report(self, user, time_period)
    else:
        self.stdout.write(self.style.NOTICE('Couldn\'t determine user type for: ' + user.username + '. Skipping'))

    context_dict.email = user.email
    context_dict.username = user.username
    send_email(self, context_dict, connection, test_only)


def get_student_attendance_report(self, student, time_period):
    print("Student")


def get_staff_attendance_report(self, lecturer, time_period):
    print("Staff")


def get_admin_attendance_report(self, user, time_period):
    # for admins, get everything
    modules = Module.objects.all()
    return get_report_data(self, time_period, modules)


def get_report_data(self, time_period, modules):
    today = datetime.date.today()
    from_date = get_from_date(self, today, time_period)

    report_data = OrderedDict()
    report_data.modules = []

    for module in modules:
        module_data = types.SimpleNamespace()
        module_data.module_code = module.module_code
        module_data.lectures = Lecture.objects.filter(module=module, date__range=[from_date, today])

        report_data.modules.append(module_data)

    return report_data


def get_from_date(self, today, time_period):
    if time_period == TimePeriod.WEEKLY:
        # start of week
        return today - datetime.timedelta(days=today.weekday())
    elif time_period == TimePeriod.MONTHLY:
        # start of month
        return datetime.date(today.year, today.month, 1)
    else:
        raise CommandError('Unrecognised time period')


def send_email(self, context_dict, connection, test_only):

    plaintext = get_template('emails/attendance_report.txt')
    html = get_template('emails/attendance_report.html')

    email_subject = 'Attendance report'

    from_email = settings.EMAIL_FROM
    to_email = context_dict.email

    text_content = plaintext.render(context_dict)
    html_content = html.render(context_dict)

    email = EmailMultiAlternatives(email_subject, text_content, from_email, [to_email], connection=connection)
    email.attach_alternative(html_content, "text/html")

    if not test_only:
        email.send()
    else:
        self.stdout.write('Email sent to {} <{}>'.format(str(context_dict.username), to_email))
    return True


class TimePeriod(Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
