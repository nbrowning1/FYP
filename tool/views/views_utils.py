from enum import Enum

from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import *


class UserType(Enum):
    ADMIN_TYPE = "ADMIN"
    STAFF_TYPE = "STAFF"
    STUDENT_TYPE = "STUDENT"


VALID_TYPES = [UserType.ADMIN_TYPE, UserType.STAFF_TYPE, UserType.STUDENT_TYPE]


class ViewsUtils():
    def get_user_type(request):
        if request.user.is_staff:
            return UserType.ADMIN_TYPE
        else:
            try:
                Staff.objects.get(user=request.user)
                return UserType.STAFF_TYPE
            except Staff.DoesNotExist:
                pass

            try:
                Student.objects.get(user=request.user)
                return UserType.STUDENT_TYPE
            except Student.DoesNotExist:
                pass

        return None

    def check_valid_user(user_type, request):
        if not user_type in VALID_TYPES:
            logout_and_redirect_login(request)


def logout_and_redirect_login(request):
    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
