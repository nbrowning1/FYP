import datetime

from django.test import TestCase
from django.urls import reverse

from ..models import *


class ViewsTests(TestCase):
    def test_unauthenticated(self):
        setup_data()
        response = go_to_module_feedback(self, 1)
        self.assertRedirects(response, '/tool/login/?next=/tool/modules/1/feedback/', status_code=302)

    def test_nonexistent_module(self):
        setup_data()
        authenticate_student(self)
        response = go_to_module_feedback(self, 10)
        self.assertEqual(response.status_code, 404)

    def test_staff(self):
        setup_data()
        authenticate_staff(self)
        response = go_to_module_feedback(self, 1)
        # staff shouldn't be able to access module feedback giving page
        self.assertEqual(response.status_code, 404)

    def test_student(self):
        setup_data()
        authenticate_student(self)
        response = go_to_module_feedback(self, 1)
        self.assertEqual(response.status_code, 200)

    def test_student_unlinked_module(self):
        setup_data()
        authenticate_student(self)
        response = go_to_module_feedback(self, 2)
        self.assertEqual(response.status_code, 404)

    def test_valid_data(self):
        self.assertEqual(len(get_feedbacks()), 0)

        # WITH 'other' feedback, anonymous
        response = setup_and_submit_feedback(self, 'Test General', 'Test Positive', 'Test Constructive', 'Test Other',
                                             'anonymous')
        # should redirect back to the module page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/tool/modules/1')
        self.assertEqual(len(get_feedbacks()), 1)
        feedback = get_feedbacks()[0]
        self.assertEqual(feedback.student.user.username, 'authteststudent')
        self.assertEqual(feedback.module.module_code, 'COM101')
        self.assertEqual(feedback.feedback_general, 'Test General')
        self.assertEqual(feedback.feedback_positive, 'Test Positive')
        self.assertEqual(feedback.feedback_constructive, 'Test Constructive')
        self.assertEqual(feedback.feedback_other, 'Test Other')
        self.assertEqual(feedback.anonymous, True)
        self.assertEqual(feedback.date, datetime.date.today())

        # WITHOUT 'other' feedback, not anonymous
        response = setup_and_submit_feedback(self, 'Test General', 'Test Positive', 'Test Constructive', '',
                                             '')
        # should redirect back to the module page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/tool/modules/1')
        self.assertEqual(len(get_feedbacks()), 2)
        feedback = get_feedbacks()[1]
        self.assertEqual(feedback.student.user.username, 'authteststudent')
        self.assertEqual(feedback.module.module_code, 'COM101')
        self.assertEqual(feedback.feedback_general, 'Test General')
        self.assertEqual(feedback.feedback_positive, 'Test Positive')
        self.assertEqual(feedback.feedback_constructive, 'Test Constructive')
        self.assertEqual(feedback.feedback_other, '')
        self.assertEqual(feedback.anonymous, False)
        self.assertEqual(feedback.date, datetime.date.today())

    def test_empty_data(self):
        self.assertEqual(len(get_feedbacks()), 0)

        # full empty data
        response = setup_and_submit_feedback(self, '', '', '', '', '')
        # should stay on feedback page, not save anything
        self.assertEqual(response.request['PATH_INFO'], '/tool/modules/1/feedback/')
        self.assertEqual(len(get_feedbacks()), 0)
        self.assertContains(response, 'Please fill in all form fields')

        # partial empty data
        response = setup_and_submit_feedback(self, 'Test General', '', 'Test Constructive', 'Test Other',
                                             'anonymous')
        self.assertEqual(response.request['PATH_INFO'], '/tool/modules/1/feedback/')
        self.assertEqual(len(get_feedbacks()), 0)
        self.assertContains(response, 'Please fill in all form fields')

    def test_too_long_data(self):
        self.assertEqual(len(get_feedbacks()), 0)

        response = setup_and_submit_feedback(self, 'a', 'b', 'c',
                                             'askmntduadyulsllhsqtzgovbzfqsmtybchharlyvsnwgathszpxuizvjiadmdxuhnmjjzeqdbrromlxegxmpmugqerjscshooylkunskjahqakrgcsystepjrveasusiunxgxnidlzkaxdrstcxgwrfqrdzcjryedlosdlrnqaysoauzdotqukwibrdyueykxpwmbkotqsgiantktpphuubvtghzwrgzxuvhpyvbpknuiumflhdjnmgghegaucedwwzvdmnfswycpkcsobnubdogpmxvtnbryzdnlveurrxtdzlddyvkotxqspcbreouazzbiyqzbmktncgvzjnzzkzrzqlejluatnjgfrzctzistwvcubyfqzlqymuazhqpccuxkfafnwsyirqllywebmcmskpiiwhwgumunswlhhizirigshzwdbhocvurfokwvrtjvldnxsfjehmhqsdmdpridzqyofhzefmipghsndwwbzdhkeumnddmjdnfafbnazpktnbwzlkaqzeakcjlltjpwutbrgpjkdmzgbhijommeoledtkjqlfejqnutrqbbighujniiysauhffnpabucnxqkxhehiseyjdvgacsypvwgmudjdnmfandqjqkmmobmizxchjtscnfrtnxtpasnpdvuxxbdkpjpmwptuazdppvjjgteknhruwwwvsicvxfbofoxgrwtldkvuanqgpwvnaicdbkspoheahubzvcssfcsevsaqebgrukoxpdmiyhwdpxpnegyidnynlstbrezdnldbeypcrwlogzsmzmrwfshqamcfoicazjpixmmaejhsdopniwmtlghpysaswwauckzcshupjbglxivkerplfwffgdikpzxagbjdyvpmicwmfnkzwkmyflgclqqiaqrvxwlnjitgxxrxgdsaealtwvoyornbkfeepanbaiepibdldqhbhwqaftgcltsppsthmeugwomxfgyyataqA',
                                             'anonymous')
        # should stay on feedback page, not save anything
        self.assertEqual(response.request['PATH_INFO'], '/tool/modules/1/feedback/')
        self.assertEqual(len(get_feedbacks()), 0)
        self.assertContains(response, 'Feedback should be between 1 and 1000 characters')


def setup_and_submit_feedback(self, fbg, fbp, fbc, fbo, anon):
    setup_data()
    authenticate_student(self)
    return self.client.post(get_module_feedback_url(1),
                            {'feedback_general': fbg,
                             'feedback_positive': fbp,
                             'feedback_constructive': fbc,
                             'feedback_other': fbo,
                             'anonymous': anon}, follow=True)


def authenticate_student(self):
    self.client.login(username='authteststudent', password='12345')


def authenticate_staff(self):
    self.client.login(username='authteststaff', password='12345')


def go_to_module_feedback(self, module_id):
    url = get_module_feedback_url(module_id)
    return self.client.get(url)


def get_module_feedback_url(module_id):
    return reverse('tool:module_feedback', kwargs={'module_id': module_id})


def get_feedbacks():
    return ModuleFeedback.objects.all()


def setup_data():
    student = create_or_get_student('authteststudent')
    staff = create_or_get_staff('authteststaff')
    module1 = create_module('COM101')
    module2 = create_module('COM102')
    module1.students.add(student)
    staff.modules.add(module1)
    staff.modules.add(module2)


def create_course(course_code):
    try:
        course = Course.objects.get(course_code=course_code)
        return course
    except Course.DoesNotExist:
        course = Course(course_code=course_code)
        course.save()
        return course


def create_or_get_student(username):
    try:
        return Student.objects.get(user__username=username)
    except Student.DoesNotExist:
        user = User.objects.create_user(username=username, password='12345')
        course = create_course('Course Code')
        student = Student(user=user, course=course)
        student.save()
        return student


def create_or_get_staff(username):
    try:
        return Staff.objects.get(user__username=username)
    except Staff.DoesNotExist:
        user = User.objects.create_user(username=username, password='12345')
        staff = Staff(user=user)
        staff.save()
        return staff


def create_module(module_code):
    module = Module(module_code=module_code)
    module.save()
    return module
