import types

from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    device_id = models.CharField(
        validators=[RegexValidator(regex='^[A-Za-z0-9]{6}$', message='Must be a valid device ID e.g. 10101C')],
        max_length=6)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    def __str__(self):
        return 'Student: ' + self.user.username


class Module(models.Model):
    students = models.ManyToManyField(Student)
    module_code = models.CharField(
        validators=[RegexValidator(regex='^[A-Z]{3,4}[0-9]{3}$', message='Must be a valid module code e.g. COM101')],
        max_length=7)
    module_crn = models.CharField(max_length=50)

    """
    Returns object with properties:
    'attendance': Overall module attendance,
    'lecture_attendances[]':
        'lecture': Lecture object,
        'attendance': Attendance % for lecture
    """
    def get_data(self, from_date=None, to_date=None, student=None):
        attendance_overall = 0
        if from_date and to_date:
            lectures = Lecture.objects.filter(module=self, date__range=[from_date, to_date])
        else:
            lectures = Lecture.objects.filter(module=self)

        lecture_attendances = []
        for lecture in lectures:
            if student:
                attendances = StudentAttendance.objects.filter(lecture=lecture, student=student) \
                    .order_by('lecture__date')
            else:
                attendances = StudentAttendance.objects.filter(lecture=lecture) \
                    .order_by('lecture__date')

            if not attendances:
                continue

            total_attendance = 0
            for attendance in attendances:
                if attendance.attended:
                    total_attendance += 1

            attended_percent = (total_attendance / len(attendances)) * 100 \
                if (len(attendances) > 0) else 0
            attendance_overall += attended_percent

            lecture_attendance = types.SimpleNamespace()
            lecture_attendance.lecture = lecture
            lecture_attendance.attendance = attended_percent
            lecture_attendances.append(lecture_attendance)

        if len(lecture_attendances) > 0:
            attendance_overall = attendance_overall / len(lecture_attendances)

        data = types.SimpleNamespace()
        data.lecture_attendances = lecture_attendances
        data.attendance = attendance_overall

        return data

    def __str__(self):
        return 'Module: ' + str(self.module_code)


class Course(models.Model):
    course_code = models.CharField(max_length=100)
    modules = models.ManyToManyField(Module)

    def __str__(self):
        return 'Course: ' + str(self.course_code)


class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    modules = models.ManyToManyField(Module)
    courses = models.ManyToManyField(Course)

    def __str__(self):
        return 'Staff: ' + self.user.username


class Lecture(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=250)
    date = models.DateField()

    def __str__(self):
        return 'Lecture for module: %s session id: %s date: %s' % (self.module, self.session_id, self.date)


class StudentAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    attended = models.BooleanField()

    def __str__(self):
        return 'Student attendance for %s for %s attended: %s' % (self.student, self.lecture, self.attended)


class ModuleFeedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    feedback_general = models.CharField(max_length=1000)
    feedback_positive = models.CharField(max_length=1000)
    feedback_constructive = models.CharField(max_length=1000)
    feedback_other = models.CharField(max_length=1000)
    date = models.DateField()
    anonymous = models.BooleanField()

    def __str__(self):
        return 'Module feedback for %s by student %s' % (self.module, self.student)