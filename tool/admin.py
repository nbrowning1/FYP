from django.contrib import admin

from .models import Student, Staff, Module, Lecture, StudentAttendance

admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Module)
admin.site.register(Lecture)
admin.site.register(StudentAttendance)
