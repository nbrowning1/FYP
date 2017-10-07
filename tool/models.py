from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

#class Student(models.Model):
#  student_code = models.CharField(max_length=9)
#  
#  def __str__(self):
#    return self.student_code
  
#class Mark(models.Model):
#  student = models.ForeignKey(Student, on_delete=models.CASCADE)
#  mark = models.IntegerField()
#  date = models.DateField()
#  
#  def __str__(self):
#    return "%s -- %s -- %s" % (self.student.student_code, self.date, str(self.mark))
  
#class Student(models.Model):
#  user = models.OneToOneField(User, on_delete=models.CASCADE)
#  code = models.CharField(validators=[RegexValidator(regex='^B[0-9]{8}$', message='Must be a valid B number')], max_length=9)
#  
#  def __str__(self):
#    return self.code

class Student(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  
  def __str__(self):
    return 'Student: ' + self.user.username
  
class Staff(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  
  def __str__(self):
    return 'Staff: ' + self.user.username
  
class Module(models.Model):
  lecturers = models.ManyToManyField(Staff)
  module_code = models.CharField(validators=[RegexValidator(regex='^[A-Z]{3,4}[0-9]{3}$', message='Must be a valid module code e.g. COM101')], max_length=7)
  
  def __str__(self):
    return 'Module: ' + self.module_code
  
class Lecture(models.Model):
  module = models.ForeignKey(Module, on_delete=models.CASCADE)
  date = models.DateField()
  
  def __str__(self):
    return 'Lecture for module: %s on %s' % (self.module, self.date)
  
class StudentAttendance(models.Model):
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
  attended = models.BooleanField()

  def __str__(self):
    return 'Student attendance for %s for %s attended: %s' % (self.student, self.lecture, self.attended)
  
