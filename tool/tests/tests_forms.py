from django.test import TestCase

from tool.forms.forms import *


class ModuleFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['module_code'], ['This field is required.'])
        self.assertEquals(form.errors['module_crn'], ['This field is required.'])

    def test_valid_form(self):
        data = {'module_code': 'COM101',
                'module_crn': 'COM101-crn'}
        form = ModuleForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_code(self):
        data = {'module_code': 'ABCDEF',
                'module_crn': 'module-crn'}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['module_code'], ['Must be a valid module code e.g. COM101'])

    def test_length_check(self):
        data = {'module_code': 'COM12000',
                'module_crn': '123456789012345678901234567890123456789012345678901'}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['module_code'],
                          ['Ensure this value has at most 7 characters (it has 8).'])
        self.assertEquals(form.errors['module_crn'],
                          ['Ensure this value has at most 50 characters (it has 51).'])

    def test_existing_module(self):
        module = Module(module_code='COM101', module_crn='COM101-crn')
        module.save()

        data = {'module_code': 'com101',
                'module_crn': 'com101-crn'}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.non_field_errors()), 1)
        self.assertEquals(form.errors['__all__'], ['Module with this Module code and Module crn already exists.'])


class CourseFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = CourseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['course_code'], ['This field is required.'])

    def test_valid_form(self):
        data = {'course_code': 'Some Course Code'}
        form = CourseForm(data=data)
        self.assertTrue(form.is_valid())

    def test_length_check(self):
        data = {'course_code':
                    '12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901'}
        form = CourseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['course_code'],
                          ['Ensure this value has at most 100 characters (it has 101).'])

    def test_existing_course(self):
        course = Course(course_code='SOME COURSE CODE')
        course.save()

        data = {'course_code': 'some course code'}
        form = CourseForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.non_field_errors()), 1)
        self.assertEquals(form.errors['__all__'], ['Course with this Course code already exists.'])


class UserFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = StudentUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 4)
        self.assertEquals(form.errors['username'], ['This field is required.'])
        self.assertEquals(form.errors['first_name'], ['This field is required.'])
        self.assertEquals(form.errors['last_name'], ['This field is required.'])
        self.assertEquals(form.errors['email'], ['This field is required.'])

    def test_valid_student_form(self):
        data = {'username': 'B00112233',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'test@email.com'}
        form = StudentUserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_student_form(self):
        data = {'username': 'E00112233',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'test@email'}
        form = StudentUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['username'], ['Must be a valid student code e.g. B00112233'])
        self.assertEquals(form.errors['email'], ['Enter a valid email address.'])

    def test_valid_staff_form(self):
        data = {'username': 'E00112233',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'test@email.com'}
        form = StaffUserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_staff_form(self):
        data = {'username': 'B00112233',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'test@email'}
        form = StaffUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['username'], ['Must be a valid staff code e.g. E00112233'])
        self.assertEquals(form.errors['email'], ['Enter a valid email address.'])

    def test_existing_user(self):
        user = EncryptedUser(username='B00112233', first_name='First Name', last_name='Last Name', email='test@email.com')
        user.save()

        # existing username
        data = {'username': 'B00112233',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'test@email.com'}
        form = StudentUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.non_field_errors()), 1)
        self.assertEquals(form.errors['__all__'], ['User with this Username already exists.'])

        # existing email
        data = {'username': 'B00112234',
                'first_name': 'First Name',
                'last_name': 'Last Name',
                'email': 'test@email.com'}
        form = StudentUserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.non_field_errors()), 1)
        self.assertEquals(form.errors['__all__'], ['User with this Email address already exists.'])


class StudentFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = StudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['device_id'], ['This field is required.'])
        self.assertEquals(form.errors['course'], ['This field is required.'])

    def test_valid_form(self):
        course = Course(course_code='Course code')
        course.save()

        data = {'device_id': '10101B',
                'course': course.id}
        form = StudentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        course = Course(course_code='Course code')
        course.save()

        # length check
        data = {'device_id': '010101B',
                'course': course.id}
        form = StudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['device_id'],
                          ['Ensure this value has at most 6 characters (it has 7).'])

        # pattern check
        data = {'device_id': '1-1-1-',
                'course': course.id}
        form = StudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['device_id'],
                          ['Must be a valid device ID e.g. 10101C'])

    def test_existing_student(self):
        course = Course(course_code='Course code')
        course.save()
        user = EncryptedUser(username='B00112233', first_name='First Name', last_name='Last Name', email='test@email.com')
        user.save()
        student = Student(user=user, device_id='10101B', course=course)
        student.save()

        data = {'device_id': '10101B',
                'course': course.id}
        form = StudentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.non_field_errors()), 1)
        self.assertEquals(form.errors['__all__'], ['Student with this Device ID already exists.'])


class ModuleFeedbackFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = ModuleFeedbackForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)
        self.assertEquals(form.errors['feedback_general'], ['This field is required.'])
        self.assertEquals(form.errors['feedback_positive'], ['This field is required.'])
        self.assertEquals(form.errors['feedback_constructive'], ['This field is required.'])

    def test_valid_form(self):
        data = {'feedback_general': 'feedback',
                'feedback_positive': 'feedback',
                'feedback_constructive': 'feedback',
                'feedback_other': 'feedback'}
        form = ModuleFeedbackForm(data=data)
        self.assertTrue(form.is_valid())

    def test_length_check(self):
        data = {'feedback_general': 'feedback',
                'feedback_positive': 'feedback',
                'feedback_constructive': 'feedback',
                'feedback_other': 'askmntduadyulsllhsqtzgovbzfqsmtybchharlyvsnwgathszpxuizvjiadmdxuhnmjjzeqdbrromlxegxmpmugqerjscshooylkunskjahqakrgcsystepjrveasusiunxgxnidlzkaxdrstcxgwrfqrdzcjryedlosdlrnqaysoauzdotqukwibrdyueykxpwmbkotqsgiantktpphuubvtghzwrgzxuvhpyvbpknuiumflhdjnmgghegaucedwwzvdmnfswycpkcsobnubdogpmxvtnbryzdnlveurrxtdzlddyvkotxqspcbreouazzbiyqzbmktncgvzjnzzkzrzqlejluatnjgfrzctzistwvcubyfqzlqymuazhqpccuxkfafnwsyirqllywebmcmskpiiwhwgumunswlhhizirigshzwdbhocvurfokwvrtjvldnxsfjehmhqsdmdpridzqyofhzefmipghsndwwbzdhkeumnddmjdnfafbnazpktnbwzlkaqzeakcjlltjpwutbrgpjkdmzgbhijommeoledtkjqlfejqnutrqbbighujniiysauhffnpabucnxqkxhehiseyjdvgacsypvwgmudjdnmfandqjqkmmobmizxchjtscnfrtnxtpasnpdvuxxbdkpjpmwptuazdppvjjgteknhruwwwvsicvxfbofoxgrwtldkvuanqgpwvnaicdbkspoheahubzvcssfcsevsaqebgrukoxpdmiyhwdpxpnegyidnynlstbrezdnldbeypcrwlogzsmzmrwfshqamcfoicazjpixmmaejhsdopniwmtlghpysaswwauckzcshupjbglxivkerplfwffgdikpzxagbjdyvpmicwmfnkzwkmyflgclqqiaqrvxwlnjitgxxrxgdsaealtwvoyornbkfeepanbaiepibdldqhbhwqaftgcltsppsthmeugwomxfgyyataqA'}
        form = ModuleFeedbackForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['feedback_other'],
                          ['Ensure this value has at most 1000 characters (it has 1001).'])
