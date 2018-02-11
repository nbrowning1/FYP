from django.forms import ModelForm
from django import forms

from tool.models import *

ANONTMOUS_CHOICES = (('1', 'Submit feedback under my name'),
                     ('2', 'Submit feedback anonymously'))

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
            'feedback_general': forms.Textarea( attrs={'class': 'feedback-form-answer'}),
            'feedback_positive': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'feedback_constructive': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'feedback_other': forms.Textarea(attrs={'class': 'feedback-form-answer'}),
            'anonymous': forms.CheckboxInput(attrs={'class': 'feedback-form-answer'})
        }