import datetime

from ..models import *


class TestUtils:
    @staticmethod
    def authenticate_admin(self):
        user = User.objects.create_superuser(username='test', password='12345', email='test@mail.com')
        self.client.login(username='test', password='12345')
        return user

    @staticmethod
    def authenticate_student(self):
        user = TestUtils.create_student('teststudent').user
        self.client.login(username='teststudent', password='12345')
        return user

    @staticmethod
    def authenticate_staff(self):
        user = TestUtils.create_staff('teststaff').user
        self.client.login(username='teststaff', password='12345')
        return user

    @staticmethod
    def create_course(course_code):
        try:
            course = Course.objects.get(course_code=course_code)
            return course
        except Course.DoesNotExist:
            course = Course(course_code=course_code)
            course.save()
            return course

    @staticmethod
    def create_module(module_code, crn):
        try:
            return Module.objects.get(module_code=module_code, module_crn=crn)
        except Module.DoesNotExist:
            module = Module(module_code=module_code, module_crn=crn)
            module.save()
            return module

    @staticmethod
    def create_student(username):
        try:
            return Student.objects.get(user__username=username)
        except Student.DoesNotExist:
            user = User.objects.create_user(username=username, password='12345')
            course = TestUtils.create_course('Course Code')
            student = Student(user=user, course=course)
            student.save()
            return student

    @staticmethod
    def create_staff(username):
        try:
            return Staff.objects.get(user__username=username)
        except Staff.DoesNotExist:
            user = User.objects.create_user(username=username, password='12345')
            staff = Staff(user=user)
            staff.save()
            return staff

    @staticmethod
    def create_lecture(module, session_id):
        lecture = Lecture(module=module, session_id=session_id, date=datetime.date(2017, 12, 1))
        lecture.save()
        return lecture

    @staticmethod
    def create_attendance(student, lecture, attended):
        attendance = StudentAttendance(student=student, lecture=lecture, attended=attended)
        attendance.save()
        return attendance

    @staticmethod
    def create_feedback(student, module, feedback, anonymous):
        feedback = ModuleFeedback(student=student, module=module,
                                  feedback_general=feedback, feedback_positive=feedback,
                                  feedback_constructive=feedback, feedback_other=feedback,
                                  date="2017-10-10", anonymous=anonymous)
        feedback.save()
        return feedback
