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
        if 'module_code' in cleaned_data and 'module_crn' in cleaned_data:
            module_code = cleaned_data['module_code']
            module_crn = cleaned_data['module_crn']
            if Module.objects.filter(
                    module_code__iexact=module_code, module_crn__iexact=module_crn
            ).count() > 0:
                raise ValidationError("Module with this Module code and Module crn already exists.")


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
