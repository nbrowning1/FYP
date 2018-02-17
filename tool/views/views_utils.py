from enum import Enum

from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import *


class UserType(Enum):
    ADMIN_TYPE = "ADMIN"
    STAFF_TYPE = "STAFF"
    STUDENT_TYPE = "STUDENT"


class Colours(Enum):
    # 2-tone colours
    GREEN = '#27ae60'
    RED = '#e74c3c'
    BLUE = '#2980b9'
    ORANGE = '#d35400'

    # additional 4-tone colours
    GREEN_LIGHT = '#A3CB38'
    ORANGE_LIGHT = '#f39c12'
    BLUE_LIGHT = '#74b9ff'
    YELLOW = '#f1c40f'


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

    # return array of 2 colours - [ fail_colour, pass_colour ] e.g. red, green
    def get_pass_fail_colours_2_tone(self, request):
        if self.colourblind_options_on(request):
            return [Colours.ORANGE.value, Colours.BLUE.value]
        else:
            return [Colours.RED.value, Colours.GREEN.value]

    # return array of 4 colours - [ fail_colour, fail_mid_colour, pass_mid_colour, pass_colour]
    # usually for attendance ranges
    def get_pass_fail_colours_4_tone(self, request):
        if self.colourblind_options_on(request):
            return [Colours.ORANGE.value, Colours.YELLOW.value, Colours.BLUE_LIGHT.value, Colours.BLUE.value]
        else:
            return [Colours.RED.value, Colours.ORANGE_LIGHT.value, Colours.GREEN_LIGHT.value, Colours.GREEN.value]

    def colourblind_options_on(self, request):
        try:
            settings = Settings.objects.get(user=request.user)
            return settings.colourblind_opts_on
        except Settings.DoesNotExist:
            return False

    # return array of 3 attendance ranges e.g. [25, 50, 75]
    def get_attendance_ranges(self, request):
        try:
            settings = Settings.objects.get(user=request.user)
            val1 = settings.attendance_range_1_cap
            val2 = settings.attendance_range_2_cap
            val3 = settings.attendance_range_3_cap
            return [val1, val2, val3]
        except Settings.DoesNotExist:
            return [25, 50, 75]


def logout_and_redirect_login(request):
    logout(request)
    return HttpResponseRedirect(reverse('tool:login'))
