import csv
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from tool.models import *
from tool.upload_data_save import DataSaver

class Command(BaseCommand):
    help = 'Initialises test data in the app for development purposes'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--load-all',
            action='store_true',
            dest='load-all',
            help='Loads everything - recommended for a fresh start',
        )

        parser.add_argument(
            '--load-students',
            action='store_true',
            dest='load-students',
            help='Loads students - allows only to reload students if changes are made to load data',
        )

        parser.add_argument(
            '--load-staff',
            action='store_true',
            dest='load-staff',
            help='Loads staff - allows only to reload staff if changes are made to load data',
        )

        parser.add_argument(
            '--load-modules',
            action='store_true',
            dest='load-modules',
            help='Loads modules - allows only to reload modules if changes are made to load data',
        )

        parser.add_argument(
            '--load-modules-courses',
            action='store_true',
            dest='load-modules-courses',
            help='Links modules to courses - allows to only reload this data',
        )

        parser.add_argument(
            '--load-modules-students',
            action='store_true',
            dest='load-modules-students',
            help='Links modules to students - allows to only reload this data',
        )

        parser.add_argument(
            '--load-modules-staff',
            action='store_true',
            dest='load-modules-staff',
            help='Links modules to staff - allows to only reload this data',
        )

        parser.add_argument(
            '--load-lectures',
            action='store_true',
            dest='load-lectures',
            help='Loads lectures - allows only to reload modules if changes are made to load data',
        )

        parser.add_argument(
            '--load-attendances',
            action='store_true',
            dest='load-attendances',
            help='Loads attendances - allows only to reload modules if changes are made to load data',
        )

    def handle(self, *args, **options):
        if options['load-all']:
            load_students(self)
            load_staff(self)
            load_modules(self)
            load_modules_to_courses(self)
            load_students_to_modules(self)
            load_staff_to_modules(self)
            load_lectures(self)
            load_attendances(self)
        else:
            args_supplied = False
            if options['load-students']:
                load_students(self)
                args_supplied = True
            if options['load-staff']:
                load_staff(self)
                args_supplied = True
            if options['load-modules']:
                load_modules(self)
                args_supplied = True
            if options['load-modules-courses']:
                load_modules_to_courses(self)
                args_supplied = True
            if options['load-modules-students']:
                load_students_to_modules(self)
                args_supplied = True
            if options['load-modules-staff']:
                load_staff_to_modules(self)
                args_supplied = True
            if options['load-lectures']:
                load_lectures(self)
                args_supplied = True
            if options['load-attendances']:
                load_attendances(self)
                args_supplied = True

            if not args_supplied:
                self.stdout.write(self.style.NOTICE('No load argument supplied. Use --help to get load options'))


def load_students(self):
    self.stdout.write(self.style.NOTICE('Loading students...'))

    reader = open_file('Student_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_course_code = row[1]
        data_device_id = row[5]
        data_username = row[6]
        self.stdout.write(self.style.SUCCESS("Loading... " + data_username))
        try:
            Student.objects.get(user__username=data_username)
            # delete if already exists so new data can act as overwrite if data needs changed
            user = User.objects.get(username=data_username)
            user.delete()
        except Student.DoesNotExist:
            pass

        # create course if not already created
        try:
            course = Course.objects.get(course_code=data_course_code)
        except Course.DoesNotExist:
            course = Course(course_code=data_course_code)
            course.save()

        user = User.objects.create_user(username=data_username, password='Django123')
        student = Student(user=user, device_id=data_device_id, course=course)
        student.save()

    self.stdout.write(self.style.SUCCESS('Loaded students'))


def load_staff(self):
    self.stdout.write(self.style.NOTICE('Loading staff...'))

    reader = open_file('Staff_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_username = row[3]
        self.stdout.write(self.style.SUCCESS("Loading... " + data_username))
        try:
            Staff.objects.get(user__username=data_username)
            # delete if already exists so new data can act as overwrite if data needs changed
            user = User.objects.get(username=data_username)
            user.delete()
        except Staff.DoesNotExist:
            pass
        user = User.objects.create_user(username=data_username, password='Django123')
        staff = Staff(user=user)
        staff.save()

    self.stdout.write(self.style.SUCCESS('Loaded staff'))


def load_modules(self):
    self.stdout.write(self.style.NOTICE('Loading modules...'))

    reader = open_file('Module_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_module_id = row[0]
        data_module_crn = row[1]
        self.stdout.write(self.style.SUCCESS("Loading... " + data_module_id))
        try:
            module = Module.objects.get(module_code=data_module_id, module_crn=data_module_crn)
            # delete if already exists so new data can act as overwrite if data needs changed
            module.delete()
        except Module.DoesNotExist:
            pass

        module = Module(module_code=data_module_id, module_crn=data_module_crn)
        module.save()

    self.stdout.write(self.style.SUCCESS('Loaded modules'))


def load_modules_to_courses(self):
    self.stdout.write(self.style.NOTICE('Linking modules to courses...'))

    reader = open_file('Course_Modules_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_course_code = row[0]

        try:
            course = Course.objects.get(course_code=data_course_code)
        except Course.DoesNotExist:
            raise CommandError('Course "%s" does not exist' % data_course_code)

        data_module_code = row[1]
        try:
            module = Module.objects.get(module_code=data_module_code)
        except Module.DoesNotExist:
            raise CommandError('Module "%s" does not exist' % data_module_code)

        if module not in course.modules.all():
            self.stdout.write(self.style.SUCCESS("Linking " + module.module_code + " to " + course.course_code))
            course.modules.add(module)

    self.stdout.write(self.style.SUCCESS('Linked modules to courses'))


def load_students_to_modules(self):
    self.stdout.write(self.style.NOTICE('Linking students to modules...'))

    reader = open_file('Student_Modules_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_module_id = row[0]

        try:
            module = Module.objects.get(module_code=data_module_id)
        except Module.DoesNotExist:
            raise CommandError('Module "%s" does not exist' % data_module_id)

        data_student_id = row[1]
        try:
            student = Student.objects.get(user__username=data_student_id)
        except Student.DoesNotExist:
            raise CommandError('Student "%s" does not exist' % data_student_id)

        if Module.objects.filter(students__id__exact=student.id).count() == 0:
            self.stdout.write(self.style.SUCCESS("Linking " + student.user.username + " to " + module.module_code))
            module.students.add(student)

    self.stdout.write(self.style.SUCCESS('Linked students to modules'))


def load_staff_to_modules(self):
    self.stdout.write(self.style.NOTICE('Linking staff to modules...'))

    reader = open_file('Staff_Modules_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_module_id = row[0]

        try:
            module = Module.objects.get(module_code=data_module_id)
        except Module.DoesNotExist:
            raise CommandError('Module "%s" does not exist' % data_module_id)

        data_staff_id = row[1]
        try:
            lecturer = Staff.objects.get(user__username=data_staff_id)
        except Staff.DoesNotExist:
            raise CommandError('Staff "%s" does not exist' % data_staff_id)

        if module not in lecturer.modules.all():
            self.stdout.write(self.style.SUCCESS("Linking " + lecturer.user.username + " to " + module.module_code))
            lecturer.modules.add(module)

    self.stdout.write(self.style.SUCCESS('Linked staff to modules'))


def load_lectures(self):
    self.stdout.write(self.style.NOTICE('Loading lectures...'))

    reader = open_file('Lecture_Load_Data.csv')

    for counter, row in enumerate(reader):
        if counter == 0:
            continue

        data_module_id = row[0]

        try:
            module = Module.objects.get(module_code=data_module_id)
        except Module.DoesNotExist:
            raise CommandError('Module "%s" does not exist' % data_module_id)

        data_lecture_date = row[1]
        data_lecture_sessionid = row[2]
        try:
            lecture = Lecture.objects.get(module=module, session_id=data_lecture_sessionid)
            lecture.delete()
        except Lecture.DoesNotExist:
            pass

        self.stdout.write(self.style.SUCCESS("Loading lecture " + data_lecture_sessionid + " for " + module.module_code))
        lecture = Lecture(module=module, date=data_lecture_date, session_id=data_lecture_sessionid)
        lecture.save()

    self.stdout.write(self.style.SUCCESS('Loaded lectures'))

def load_attendances(self):
    self.stdout.write(self.style.NOTICE('Loading attendances...'))

    attendance_data_modules = []
    attendance_data_modules.append(Module.objects.get(module_code="COM332"))
    attendance_data_modules.append(Module.objects.get(module_code="COM367"))
    attendance_data_modules.append(Module.objects.get(module_code="EEE289"))
    attendance_data_modules.append(Module.objects.get(module_code="EEE123"))
    attendance_data_modules.append(Module.objects.get(module_code="BIO645"))
    attendance_data_modules.append(Module.objects.get(module_code="BIO922"))
    attendance_data_modules.append(Module.objects.get(module_code="ENG122"))

    attendance_file_names = []
    attendance_file_names.append('Attendance_Load_Data_Module1.csv')
    attendance_file_names.append('Attendance_Load_Data_Module2.csv')
    attendance_file_names.append('Attendance_Load_Data_Module3.csv')
    attendance_file_names.append('Attendance_Load_Data_Module4.xlsx')
    attendance_file_names.append('Attendance_Load_Data_Module5.xlsx')
    attendance_file_names.append('Attendance_Load_Data_Module6.xls')
    attendance_file_names.append('Attendance_Load_Data_Module7.xls')

    for i, filename in enumerate(attendance_file_names):
        if filename.endswith("csv"):
            reader = open_file(filename)
            response = DataSaver().save_uploaded_data_csv(reader, attendance_data_modules[i-1])
        else:
            file_contents = open_xls_file(filename).read()
            response = DataSaver().save_uploaded_data_excel(file_contents, attendance_data_modules[i-1])

        if hasattr(response, 'error'):
            raise CommandError(response.error)
        else:
            self.stdout.write(self.style.SUCCESS('Loaded attendance for module file ' + filename))

    self.stdout.write(self.style.SUCCESS('Loaded attendances'))

def open_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), '../../test_data/' + filename)
    file = open(filepath)
    return csv.reader(file)

def open_xls_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), '../../test_data/' + filename)
    file = open(filepath, "rb")
    return file
