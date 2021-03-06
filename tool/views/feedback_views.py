import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from tool.forms.forms import ModuleFeedbackForm
from .views_utils import *
from ..models import *

"""
Views related to feedback.
These views should always have a @login_required decorator and a call to ViewsUtils.check_valid_user()
to ensure that the user type is recognised.
"""


@login_required
def module_feedback(request, module_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    # Only students should be allowed to give feedback for modules
    if user_type == UserType.STUDENT_TYPE:
        student = Student.objects.get(user__username=request.user.username)
    else:
        raise Http404("Not authorised to give feedback for this module")

    try:
        module = Module.objects.get(id=module_id)
        # Restrict access if student isn't linked to module
        if user_type == UserType.STUDENT_TYPE and not (student in module.students.all()):
            raise Http404("Not authorised to view this module")
    except Module.DoesNotExist:
        raise Http404("Module does not exist")

    if request.method == 'POST':
        feedback_general = request.POST.get("feedback_general")
        feedback_positive = request.POST.get("feedback_positive")
        feedback_constructive = request.POST.get("feedback_constructive")
        feedback_other = request.POST.get("feedback_other")
        anonymous = request.POST.get("anonymous")

        # On submit, perform validation if not already caught by client-side
        if not (feedback_general and feedback_positive and feedback_constructive):
            return render_with_error(request, module, 'Please fill in all form fields')
        else:
            feedback_texts = [feedback_general,
                              feedback_positive,
                              feedback_constructive,
                              feedback_other]
            error_msg = validate_feedback_texts(feedback_texts)
            if (error_msg):
                return render_with_error(request, module, error_msg)
            save_feedback(student, module, feedback_general, feedback_positive, feedback_constructive, feedback_other,
                          anonymous)
            return redirect(reverse('tool:module', kwargs={'module_id': module_id}), Permanent=True)
    else:
        form = ModuleFeedbackForm()
        return render(request, 'tool/feedback/module_feedback.html', {
            'module': module,
            'form': form
        })


def validate_feedback_texts(feedback_texts):
    for feedback_text in feedback_texts:
        if not len(feedback_text) <= 1000:
            return 'Feedback should be between 1 and 1000 characters'

    return None


def save_feedback(student, module, feedback_general, feedback_positive, feedback_constructive, feedback_other,
                  anonymous):
    # Get today's date to save with feedback submission
    date = datetime.date.today()
    if anonymous:
        anonymous_val = True
    else:
        anonymous_val = False

    feedback = ModuleFeedback(student=student, module=module,
                              feedback_general=feedback_general, feedback_positive=feedback_positive,
                              feedback_constructive=feedback_constructive, feedback_other=feedback_other,
                              date=date, anonymous=anonymous_val)
    feedback.save()


def render_with_error(request, module, error_msg):
    return render(request, 'tool/feedback/module_feedback.html', {
        'module': module,
        'error_msg': error_msg
    })
