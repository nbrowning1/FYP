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
  
"""
class Choice(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE)
  choice_text = models.CharField(max_length=200)
  votes = models.IntegerField(default=0)
  
  def __str__(self):
    return self.choice_text
"""