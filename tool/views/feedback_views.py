import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect

from .views_utils import *
from ..models import *


@login_required
def module_feedback(request, module_id):
    user_type = ViewsUtils.get_user_type(request)
    ViewsUtils.check_valid_user(user_type, request)

    if user_type == UserType.STUDENT_TYPE:
        student = Student.objects.get(user__username=request.user.username)
    else:
        raise Http404("Not authorised to give feedback for this module")

    try:
        module = Module.objects.get(id=module_id)
        # restrict access if student isn't linked to module
        if user_type == UserType.STUDENT_TYPE and not student in module.students.all():
            raise Http404("Not authorised to view this module")
    except Module.DoesNotExist:
        raise Http404("Module does not exist")

    if request.method == 'POST':
        feedback_general = request.POST.get("general-feedback")
        feedback_positive = request.POST.get("positive-feedback")
        feedback_constructive = request.POST.get("constructive-feedback")
        feedback_other = request.POST.get("other-feedback")
        anonymous = request.POST.get("anonymous")

        if not (feedback_general and feedback_positive and feedback_constructive and feedback_other and anonymous):
            return render_with_error(request, module, 'Please fill in all form fields')
        else:
            feedback_texts = [feedback_general, feedback_positive, feedback_constructive, feedback_other]
            error_msg = validate_feedback_texts(feedback_texts, anonymous)
            if (error_msg):
                return render_with_error(request, module, error_msg)
            save_feedback(student, module, feedback_general, feedback_positive, feedback_constructive, feedback_other,
                          anonymous)
            return redirect(reverse('tool:module', kwargs={'module_id': module_id}), Permanent=True)
    else:
        return render(request, 'tool/module_feedback.html', {
            'module': module
        })


def validate_feedback_texts(feedback_texts, anonymous):
    for feedback_text in feedback_texts:
        if not is_feedback_text_valid(feedback_text):
            return 'Feedback should be between 1 and 1000 characters'

    if not (anonymous == "anonymous" or anonymous == "not-anonymous"):
        return 'Invalid value for anonymous selection'

    return None


def is_feedback_text_valid(text):
    return 0 < len(text) <= 1000


def save_feedback(student, module, feedback_general, feedback_positive, feedback_constructive, feedback_other,
                  anonymous):
    date = datetime.date.today()
    if anonymous == "not-anonymous":
        anonymous_val = False
    else:
        anonymous_val = True

    feedback = ModuleFeedback(student=student, module=module,
                              feedback_general=feedback_general, feedback_positive=feedback_positive,
                              feedback_constructive=feedback_constructive, feedback_other=feedback_other,
                              date=date, anonymous=anonymous_val)
    feedback.save()


def render_with_error(request, module, error_msg):
    return render(request, 'tool/module_feedback.html', {
        'module': module,
        'error_msg': error_msg
    })
