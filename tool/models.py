from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class Course(models.Model):
    course_code = models.CharField(max_length=100)

    def __str__(self):
        return 'Course: ' + str(self.course_code)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    device_id = models.CharField(
        validators=[RegexValidator(regex='^[A-Za-z0-9]{6}$', message='Must be a valid device ID e.g. 10101C')],
        max_length=6)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return 'Student: ' + self.user.username


class Module(models.Model):
    students = models.ManyToManyField(Student)
    courses = models.ManyToManyField(Course)
    module_code = models.CharField(
        validators=[RegexValidator(regex='^[A-Z]{3,4}[0-9]{3}$', message='Must be a valid module code e.g. COM101')],
        max_length=7)
    module_crn = models.CharField(max_length=50)

    def __str__(self):
        return 'Module: ' + str(self.module_code)


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
