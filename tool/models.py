from django.db import models

class Student(models.Model):
  student_code = models.CharField(max_length=9)
  
  def __str__(self):
    return self.student_code
  
class Mark(models.Model):
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  mark = models.IntegerField()
  date = models.DateField()
  
  def __str__(self):
    return "%s -- %s -- %s" % (self.student.student_code, self.date, str(self.mark))