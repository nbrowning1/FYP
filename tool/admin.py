from django.contrib import admin

from .models import *

admin.site.register(EncryptedUser)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Module)
admin.site.register(Lecture)
admin.site.register(StudentAttendance)
admin.site.register(ModuleFeedback)
admin.site.register(Settings)
