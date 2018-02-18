import re
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from tool.models import *


class ModuleForm(ModelForm):
    class Meta:
        model = Module
        fields = ['module_code', 'module_crn']
        labels = {
            'module_code': 'Module Code',
            'module_crn': 'Module CRN',
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        if all(key in cleaned_data for key in ('module_code', 'module_crn')):
            module_code = cleaned_data['module_code']
            module_crn = cleaned_data['module_crn']
            if Module.objects.filter(
                    module_code__iexact=module_code, module_crn__iexact=module_crn
            ).count() > 0:
                raise ValidationError("Module with this Module code and Module crn already exists.")


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['course_code']
        labels = {
            'course_code': 'Course Code'
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'course_code' in cleaned_data:
            course_code = cleaned_data['course_code']
            if Course.objects.filter(
                    course_code__iexact=course_code
            ).count() > 0:
                raise ValidationError("Course with this Course code already exists.")


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Username / B00 code',
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email address'
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) > 9:
            raise ValidationError("Ensure this value has at most 9 characters (it has %s)." % str(len(username)))
        elif not re.match('B\d{8}', username):
            raise ValidationError('Must be a valid student code e.g. B00112233')
        return username

    def clean_first_name(self):
        return self.validate_not_empty('first_name')

    def clean_last_name(self):
        return self.validate_not_empty('last_name')

    def clean_email(self):
        return self.validate_not_empty('email')

    def validate_not_empty(self, field_key):
        data = self.cleaned_data[field_key]
        if not len(data) > 0:
            raise ValidationError('This field is required.')
        return data

    def clean(self):
        cleaned_data = self.cleaned_data
        if all(key in cleaned_data for key in ('username', 'email')):
            username = cleaned_data['username']
            email = cleaned_data['email']
            if User.objects.filter(username__iexact=username).count() > 0:
                raise ValidationError("User with this Username already exists.")
            elif User.objects.filter(email__iexact=email).count() > 0:
                raise ValidationError("User with this Email address already exists.")


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['device_id', 'course']
        labels = {
            'device_id': 'Device ID',
            'course': 'Course'
        }

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'device_id' in cleaned_data:
            device_id = cleaned_data['device_id']
            if Student.objects.filter(device_id__iexact=device_id).count() > 0:
                raise ValidationError("Student with this Device ID already exists.")


class ModuleFeedbackForm(ModelForm):
    class Meta:
        model = ModuleFeedback
        fields = ['feedback_general', 'feedback_positive', 'feedback_constructive', 'feedback_other', 'anonymous']
        labels = {
            'feedback_general': 'How have you found the module so far?',
            'feedback_positive': 'What is the module doing well?',
            'feedback_constructive': 'What would you change about the module to improve your experience?',
            'feedback_other': 'Additional comments',
            'anonymous': 'Submit feedback anonymously',
        }
        widgets = {
            'feedback_general': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'feedback_positive': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'feedback_constructive': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'feedback_other': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'anonymous': forms.CheckboxInput(attrs={'class': 'feedback-form-answer'})
        }
