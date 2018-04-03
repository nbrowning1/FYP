import datetime
from enum import Enum

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template

from tool.models import *

"""
Used to send emails to users to report on attendances.
"""


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

        parser.add_argument('--test-date',
                            action='store',
                            dest='test-date',
                            help='For testing purposes - specify the date (in DD/MM/YYYY format) for when this command is called, where default is today')

    def handle(self, *args, **options):
        users = []
        if options['all-users']:
            users = EncryptedUser.objects.all()
        elif options['students']:
            users = Student.objects.all()
        elif options['staff']:
            users = Staff.objects.all()
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

        to_date = None
        if options['test-date']:
            to_date = datetime.datetime.strptime(options['test-date'], "%Y-%m-%d").date()

        # Uses SMTP server specified in settings.py
        # Get and open one connection for all emails
        connection = get_connection()
        connection.open()

        for user in users:
            if not isinstance(user, EncryptedUser):
                # unpack user from model object
                user = user.user
            email_attendance_report(self, user, time_period, connection, test_only, to_date)

        # cleaning up opened connection
        connection.close()


def email_attendance_report(self, user, time_period, connection, test_only, to_date):
    user_type_found = False

    # Try student first
    try:
        student = Student.objects.get(user=user)
        email_details = get_student_attendance_report(self, student, time_period, to_date)
        email_details.is_student = True
        user_type_found = True
    except Student.DoesNotExist:
        pass

    if not user_type_found:
        # Fall back to staff
        try:
            lecturer = Staff.objects.get(user=user)
            email_details = get_staff_attendance_report(self, lecturer, time_period, to_date)
            email_details.is_student = False
            user_type_found = True
        except Staff.DoesNotExist:
            pass

    if not user_type_found:
        self.stdout.write(self.style.NOTICE('Couldn\'t determine user type for: ' + user.username + '. Skipping'))
        return

    # If no attendance data for email, don't send it
    if not email_details.modules:
        if test_only:
            self.stdout.write('Email not sent to {} <{}>'.format(str(user.username), user.email))
        return

    email_details.email = user.email
    email_details.username = user.username
    send_email(self, email_details, connection, test_only)


def get_student_attendance_report(self, student, time_period, to_date):
    modules = Module.objects.filter(students__in=[student])
    return get_email_details(self, time_period, modules, to_date, student)


def get_staff_attendance_report(self, lecturer, time_period, to_date):
    modules = lecturer.modules.all()
    return get_email_details(self, time_period, modules, to_date, None)


def get_email_details(self, time_period, modules, to_date_override, student):
    to_date = datetime.date.today() if to_date_override == None else to_date_override
    from_date = get_from_date(self, to_date, time_period)

    email_details = types.SimpleNamespace()
    email_details.from_date = from_date
    email_details.to_date = to_date
    email_details.modules = []

    for module in modules:
        module_data = types.SimpleNamespace()
        module_data.module_code = module.module_code
        module_data.module_crn = module.module_crn
        module_data.module_data = module.get_data(from_date, to_date, student)
        module_data.warning_students_data = []
        for student_attendance in module_data.module_data.student_attendances:
            if student_attendance.percent_attended < 50:
                module_data.warning_students_data.append(student_attendance)

        email_details.modules.append(module_data)

    return email_details


def get_from_date(self, today, time_period):
    if time_period == TimePeriod.WEEKLY:
        # Start of week
        return today - datetime.timedelta(days=today.weekday())
    elif time_period == TimePeriod.MONTHLY:
        # Start of month
        return datetime.date(today.year, today.month, 1)
    else:
        raise CommandError('Unrecognised time period')


def send_email(self, email_details, connection, test_only):
    plaintext = get_template('emails/attendance_report.txt')

    email_subject = 'Attendance report'

    from_email = settings.EMAIL_FROM
    to_email = email_details.email

    context_dict = {
        'from_date': email_details.from_date,
        'to_date': email_details.to_date,
        'modules': email_details.modules,
        'is_student': email_details.is_student
    }

    text_content = plaintext.render(context_dict)

    email = EmailMultiAlternatives(email_subject, text_content, from_email, [to_email], connection=connection)

    if not test_only:
        email.send()
    else:
        self.stdout.write('Email sent to {} <{}>'.format(str(email_details.username), to_email))
    return True


class TimePeriod(Enum):
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"
