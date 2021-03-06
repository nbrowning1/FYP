import types
from collections import OrderedDict

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from encrypted_model_fields.fields import EncryptedCharField, EncryptedEmailField


class EncryptedUser(AbstractUser):
    """Encrypted user override for Django's AbstractUser model, to wrap certain fields as encrypted."""

    # Field definitions are lifted directly from AbstractUser, and just wrapped in EncryptedFields
    first_name = EncryptedCharField(_('first name'), max_length=30, blank=True)
    last_name = EncryptedCharField(_('last name'), max_length=30, blank=True)
    email = EncryptedEmailField(_('email address'), blank=True)

    # Required because of encrypted email field - can't perform direct get() as usual so requires iteration
    @staticmethod
    def get_by_email(email):
        for user in EncryptedUser.objects.all():
            # Case-insensitive matching
            if email.lower() == user.email.lower():
                return user
        return None


class Student(models.Model):
    user = models.OneToOneField(EncryptedUser, on_delete=models.CASCADE)
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

    class Meta:
        unique_together = ('module_code', 'module_crn')

    def get_data(self, from_date=None, to_date=None, student=None):
        """Returns data object with properties:
        'attendance': Overall module attendance,
        'lecture_attendances[]':
            'lecture': Lecture object,
            'attendance': Attendance % for lecture
        'student_attendances[]':
            'student': Student object,
            'attendance': Attendance % for student

        :param from_date: a start date from which lectures should be gathered
        :param to_date: an end date up to which lectures should be gathered
        :param student: a particular student to gather the data for
        :return: a data object with information about attendance and lectures meeting these constraints
        """

        attendance_overall = 0

        # Get lectures in date range, or unbounded if dates unspecified
        if from_date and to_date:
            lectures = Lecture.objects.filter(module=self, date__range=[from_date, to_date])
        else:
            lectures = Lecture.objects.filter(module=self)

        lecture_attendances = []
        student_total_attendances = OrderedDict()
        for lecture in lectures:
            # Gather attendances relating only to specified student, or all attendances for lecture if unspecified
            if student:
                attendances = StudentAttendance.objects.filter(lecture=lecture, student=student) \
                    .order_by('lecture__date')
            else:
                attendances = StudentAttendance.objects.filter(lecture=lecture) \
                    .order_by('student', 'lecture__date')

            # Move to next lecture if no attendances meet these constraints
            if not attendances:
                continue

            total_attendance = 0

            # Build up the total attendances for each student and total overall
            for attendance in attendances:
                student_total_attendances.setdefault(attendance.student, 0)
                if attendance.attended:
                    total_attendance += 1
                    student_total_attendances[attendance.student] += 1

            # Get overall attendance % for lecture and append to overall for module so far
            attended_percent = (total_attendance / len(attendances)) * 100 \
                if (len(attendances) > 0) else 0
            attendance_overall += attended_percent

            lecture_attendance = types.SimpleNamespace()
            lecture_attendance.lecture = lecture
            lecture_attendance.percent_attended = attended_percent
            lecture_attendances.append(lecture_attendance)

        attendance_percent = 0
        student_attendances = []

        # Finally gather up the module attendance % and attendance % per student
        if len(lecture_attendances) > 0:
            attendance_percent = attendance_overall / len(lecture_attendances)
            for key, val in student_total_attendances.items():
                student_attendance = types.SimpleNamespace()
                student_attendance.student = key
                student_attendance.percent_attended = (val / len(lecture_attendances)) * 100
                student_attendances.append(student_attendance)

        data = types.SimpleNamespace()
        data.lecture_attendances = lecture_attendances
        data.percent_attended = attendance_percent
        data.student_attendances = student_attendances
        return data

    def __str__(self):
        return 'Module: ' + str(self.module_code)


class Course(models.Model):
    course_code = models.CharField(max_length=100)
    modules = models.ManyToManyField(Module)

    def __str__(self):
        return 'Course: ' + str(self.course_code)


class Staff(models.Model):
    user = models.OneToOneField(EncryptedUser, on_delete=models.CASCADE)
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
    feedback_other = models.CharField(max_length=1000, blank=True)
    date = models.DateField()
    anonymous = models.BooleanField()

    def __str__(self):
        return 'Module feedback for %s by student %s' % (self.module, self.student)


class Settings(models.Model):
    user = models.OneToOneField(EncryptedUser, on_delete=models.CASCADE)
    colourblind_opts_on = models.BooleanField(default=False)
    attendance_range_1_cap = models.IntegerField(default=25)
    attendance_range_2_cap = models.IntegerField(default=50)
    attendance_range_3_cap = models.IntegerField(default=75)

    def __str__(self):
        return 'Settings for user %s' % self.user.username
