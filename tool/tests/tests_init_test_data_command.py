from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from ..models import *


class InitTestDataTest(TestCase):
    def test_minimal_data_loaded(self):
        self.assertEqual(len(EncryptedUser.objects.all()), 0)
        self.assertEqual(len(Student.objects.all()), 0)
        self.assertEqual(len(Staff.objects.all()), 0)
        self.assertEqual(len(Module.objects.all()), 0)
        self.assertEqual(len(Lecture.objects.all()), 0)
        self.assertEqual(len(StudentAttendance.objects.all()), 0)
        self.assertEqual(len(ModuleFeedback.objects.all()), 0)

        call_command('init_test_data', '--load-minimal')
        self.assertEqual(len(EncryptedUser.objects.all()), 1)
        self.assertEqual(len(Student.objects.all()), 0)
        self.assertEqual(len(Staff.objects.all()), 1)
        self.assertEqual(len(Module.objects.all()), 0)
        self.assertEqual(len(Lecture.objects.all()), 0)
        self.assertEqual(len(StudentAttendance.objects.all()), 0)
        self.assertEqual(len(ModuleFeedback.objects.all()), 0)
        staff_user = Staff.objects.get(user__username='admin')
        self.assertTrue(staff_user.user.has_usable_password())

        # calling command again should only overwrite data, not add anything
        call_command('init_test_data', '--load-minimal')
        self.assertEqual(len(EncryptedUser.objects.all()), 1)
        self.assertEqual(len(Student.objects.all()), 0)
        self.assertEqual(len(Staff.objects.all()), 1)
        self.assertEqual(len(Module.objects.all()), 0)
        self.assertEqual(len(Lecture.objects.all()), 0)
        self.assertEqual(len(StudentAttendance.objects.all()), 0)
        self.assertEqual(len(ModuleFeedback.objects.all()), 0)
        staff_user = Staff.objects.get(user__username='admin')
        self.assertTrue(staff_user.user.has_usable_password())

    # testing ALL data is loaded from fresh DB, and subsequent load doesnt add anything
    def test_all_data_loaded(self):
        self.assertEqual(len(EncryptedUser.objects.all()), 0)
        self.assertEqual(len(Student.objects.all()), 0)
        self.assertEqual(len(Staff.objects.all()), 0)
        self.assertEqual(len(Module.objects.all()), 0)
        self.assertEqual(len(Lecture.objects.all()), 0)
        self.assertEqual(len(StudentAttendance.objects.all()), 0)
        self.assertEqual(len(ModuleFeedback.objects.all()), 0)

        call_command('init_test_data', '--load-all')
        self.assertEqual(len(EncryptedUser.objects.all()), 235)
        self.assertEqual(len(Student.objects.all()), 216)
        self.assertEqual(len(Staff.objects.all()), 19)
        self.assertEqual(len(Module.objects.all()), 7)
        self.assertEqual(len(Lecture.objects.all()), 88)
        self.assertEqual(len(StudentAttendance.objects.all()), 1296)
        self.assertEqual(len(ModuleFeedback.objects.all()), 13)

        # calling command again should only overwrite data, not add anything
        call_command('init_test_data', '--load-all')
        self.assertEqual(len(EncryptedUser.objects.all()), 235)
        self.assertEqual(len(Student.objects.all()), 216)
        self.assertEqual(len(Staff.objects.all()), 19)
        self.assertEqual(len(Module.objects.all()), 7)
        self.assertEqual(len(Lecture.objects.all()), 88)
        self.assertEqual(len(StudentAttendance.objects.all()), 1296)
        self.assertEqual(len(ModuleFeedback.objects.all()), 13)

    # testing a command to only load specific data, e.g. students, works
    def test_single_datatype_reload(self):
        self.assertEqual(len(EncryptedUser.objects.all()), 0)
        self.assertEqual(len(Student.objects.all()), 0)
        self.assertEqual(len(Staff.objects.all()), 0)
        self.assertEqual(len(Module.objects.all()), 0)
        self.assertEqual(len(Lecture.objects.all()), 0)
        self.assertEqual(len(StudentAttendance.objects.all()), 0)

        call_command('init_test_data', '--load-students')
        self.assertEqual(len(EncryptedUser.objects.all()), 216)
        self.assertEqual(len(Student.objects.all()), 216)
        self.assertEqual(len(Staff.objects.all()), 0)
        self.assertEqual(len(Module.objects.all()), 0)
        self.assertEqual(len(Lecture.objects.all()), 0)
        self.assertEqual(len(StudentAttendance.objects.all()), 0)

    def test_no_args_provided(self):
        out = StringIO()
        call_command('init_test_data', stdout=out)
        self.assertIn('No load argument supplied. Use --help to get load options', out.getvalue())
