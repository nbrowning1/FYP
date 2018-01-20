import csv
import io
import os
from collections import OrderedDict

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse

from .views_utils import *
from ..models import *
from ..upload_data_save import DataSaver


@login_required
def index(request):
    error_msg = request.session.pop('error_message', '')

    if request.user.is_staff:
        modules = Module.objects.all()
        lecturers = Staff.objects.all()
        students = Student.objects.all()
        lectures = Lecture.objects.all()
        user_type = UserType.ADMIN_TYPE.value
    else:
        is_valid_user = False

        # if lecturer exists, it's a lecturer
        try:
            lecturer = Staff.objects.get(user=request.user)

            modules = Module.objects.filter(lecturers__id__exact=lecturer.id)
            lecturers = []
            students = []
            for module in modules:
                for student in module.students.all():
                    students.append(student)
            students = list(OrderedDict.fromkeys(students))
            lectures = Lecture.objects.filter(module__in=modules)

            is_valid_user = True
            user_type = UserType.STAFF_TYPE.value
        except Staff.DoesNotExist:
            pass

        # otherwise try student
        try:
            student = Student.objects.get(user=request.user)

            modules = Module.objects.filter(students__id__exact=student.id)
            lecturers = []
            for module in modules:
                for lecturer in module.lecturers.all():
                    lecturers.append(lecturer)
            lecturers = list(OrderedDict.fromkeys(lecturers))
            students = []
            lectures = Lecture.objects.filter(module__in=modules)
            is_valid_user = True

            user_type = UserType.STUDENT_TYPE.value
        except Student.DoesNotExist:
            pass

        # if we made it this far, user is invalid - log user out
        if not is_valid_user:
            return logout_and_redirect_login(request)

    upload_example_filepath = os.path.join(os.path.dirname(__file__), '..', 'download_resources', 'upload_example.csv')

    return render(request, 'tool/index.html', {
        'error_message': error_msg,
        'modules': modules,
        'lecturers': lecturers,
        'students': students,
        'lectures': lectures,
        'user_type': user_type,
        'upload_example_filepath': upload_example_filepath
    })


@login_required
def upload(request):
    if not request.user.is_staff:
        raise PermissionDenied("Insufficient permissions")

    if request.method == 'POST' and request.FILES.get('upload-data', False):

        csv_files = request.FILES.getlist('upload-data')
        for csv_file in csv_files:
            if not (csv_file.name.lower().endswith('.csv')):
                # workaround to pass message through redirect
                request.session['error_message'] = "Invalid file type. Only csv files are accepted."
                return redirect(reverse('tool:index'), Permanent=True)

        saved_data = []
        for csv_file in csv_files:
            decoded_file = csv_file.read().decode('utf-8')
            file_str = io.StringIO(decoded_file)

            reader = csv.reader(file_str)
            uploaded_data = DataSaver(reader).save_uploaded_data()
            if hasattr(uploaded_data, 'error'):
                error_msg = 'Error processing file ' + csv_file.name + ': ' + uploaded_data.error
                return redirect_with_error(request, reverse('tool:index'), error_msg)
            saved_data.append(uploaded_data)

        return render(request, 'tool/upload.html', {
            'uploaded_data': saved_data,
        })
    else:
        # workaround to pass message through redirect
        request.session['error_message'] = "No file uploaded. Please upload a .csv file."
        return redirect(reverse('tool:index'), Permanent=True)


@login_required
def download(request, path):
    if not request.user.is_staff:
        raise PermissionDenied("Insufficient permissions")

    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="text/csv")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404


@login_required
def settings(request):
    return render(request, 'tool/settings.html')


# workaround to pass message through redirect
def redirect_with_error(request, redirect_url, error_msg):
    request.session['error_message'] = error_msg
    return redirect(redirect_url, Permanent=True)


def logout_and_redirect_login(request):
    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
