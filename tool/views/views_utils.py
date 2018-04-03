from enum import Enum

from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from ..models import *

"""
Utils classes and functions for common functionality required of views
"""


class UserType(Enum):
    """Recognised user types in the system."""

    STAFF_TYPE = "STAFF"
    STUDENT_TYPE = "STUDENT"


class Colours(Enum):
    """Colours to use around the app for charts/icons"""

    # 2-tone colours - for regular and colourblind mode
    GREEN = '#27ae60'
    RED = '#e74c3c'
    BLUE = '#2980b9'
    ORANGE = '#d35400'

    # Additional 4-tone colours - for regular and colourblind mode
    GREEN_LIGHT = '#A3CB38'
    ORANGE_LIGHT = '#f39c12'
    BLUE_LIGHT = '#74b9ff'
    YELLOW = '#f1c40f'


VALID_TYPES = [UserType.STAFF_TYPE, UserType.STUDENT_TYPE]


class ViewsUtils():
    def get_user_type(request):
        """Get user type from HTTP request.

        :return: UserType value if recognised, or None
        """

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
        """Check if supplied user type is recognised by the system.

        :param user_type: user type to validate on
        :param request: HTTP request to be used to redirect to login on validation failure
        """

        if not user_type in VALID_TYPES:
            logout_and_redirect_login(request)

    def get_pass_fail_colours_2_tone(self, request):
        """Return array of 2 colours - [ fail_colour, pass_colour ] e.g. red, green / orange, blue.

        :param request: HTTP request used to check colourblind settings on for authenticated user
        :return: list of 2 colours in format [ FAIL, PASS ]
        """

        if self.colourblind_options_on(request):
            return [Colours.ORANGE.value, Colours.BLUE.value]
        else:
            return [Colours.RED.value, Colours.GREEN.value]

    def get_pass_fail_colours_4_tone(self, request):
        """Return array of 4 colours - [ fail_colour, fail_mid_colour, pass_mid_colour, pass_colour].
        Usually used for attendance ranges which fall into 4 ranges.

        :param request: HTTP request used to check colourblind settings on for authenticated user
        :return: list of 4 colours in format [ FAIL, FAIL-MID, PASS-MID, PASS ]
        """

        if self.colourblind_options_on(request):
            return [Colours.ORANGE.value, Colours.YELLOW.value, Colours.BLUE_LIGHT.value, Colours.BLUE.value]
        else:
            return [Colours.RED.value, Colours.ORANGE_LIGHT.value, Colours.GREEN_LIGHT.value, Colours.GREEN.value]

    def colourblind_options_on(self, request):
        """Check whether the colourblind settings are enabled for current user.

        :param request: HTTP request to check currently-authenticated user for whether
                            their colourblind settings enabled
        :return: True if user's colourblind settings enabled, or False if disabled / settings don't exist for user
        """

        try:
            settings = Settings.objects.get(user=request.user)
            return settings.colourblind_opts_on
        except Settings.DoesNotExist:
            return False

    # Return array of 3 attendance ranges e.g. [25, 50, 75]
    def get_attendance_ranges(self, request):
        """Get list of attendance ranges from current user's settings.

        :param request: HTTP request to check currently-authenticated user for ranges
                            from their settings
        :return: list of 3 attendance ranges e.g. [25, 50, 75]
        """
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
