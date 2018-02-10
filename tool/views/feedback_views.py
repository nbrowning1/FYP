import os
import types
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect

from .views_utils import *
from ..models import *


@login_required
def module_feedback(request):
    return render(request, 'tool/module_feedback.html')