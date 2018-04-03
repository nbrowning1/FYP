import datetime
import types

from .models import Student

ATTENDANCE_VALS_START_COL = 3


class AttendanceSessionRow:
    """Row for the column headers for attendance which give Session ID & Date."""

    def __init__(self, data):
        """
        :param data: comma-separated data for attendance sessions (lecture indicators)
        """

        self.error_message = ''
        self.sessions = []

        # Skip first few non-data columns (starting at ATTENDANCE_VALS_START_COL)
        for i in range(ATTENDANCE_VALS_START_COL, len(data)):
            # Validate not empty
            if not data[i]:
                self.error_message = 'Unexpected empty session data at column ' + str(i + 1)
                return

            # Separate on new lines to gather Date and Session ID data
            session_data_parts = data[i].splitlines()
            if len(session_data_parts) != 2:
                self.error_message = 'Expected newline to separate date and session id for: ' + data[
                    i] + ' at column ' + str(i + 1)
                return
            date = str(session_data_parts[0]).strip()
            session_id = str(session_data_parts[1]).strip()

            # Validate individual parts not empty
            if not date:
                self.error_message = 'Unexpected empty date at column ' + str(i + 1)
                return
            if not session_id:
                self.error_message = 'Unexpected empty session id at column ' + str(i + 1)
                return

            # Parse date string to date object, expecting DD/MM/YYYY format
            try:
                parsed_date = datetime.datetime.strptime(date, '%d/%m/%Y').date()
            except ValueError:
                self.error_message = 'Incorrect date format: ' + date + ', should be DD/MM/YYYY' + ' at column ' + str(
                    i + 1)
                return

            # Build session from data
            session = types.SimpleNamespace()
            session.date = parsed_date
            session.session_id = session_id
            self.sessions.append(session)

    def get_error_message(self):
        """Get error message from parsing the attendance session row if exists.
        Acts as indicator for parse failure without raising exception during parsing.

        :return: error message if present
        """
        return self.error_message


class AttendanceRow:
    """Row for actual attendance values, including student indicator (either Device ID or Student Code)."""

    def __init__(self, attendance_session_row, data):
        """
        :param attendance_session_row: an AttendanceSessionRow object corresponding to this attendance data,
                                        to be able to map attendances to the correct lecture they're for
        :param data: comma-separated data for student attendance data
        """
        self.error_message = ''
        self.student_id = data[0].strip()
        self.attendances = []

        # Validate number of attendance data values matches expected number of sessions
        num_attendance_vals = len(data) - ATTENDANCE_VALS_START_COL
        if num_attendance_vals < 0:
            num_attendance_vals = 0
        if len(attendance_session_row.sessions) != num_attendance_vals:
            self.error_message = 'Number of data columns doesn\'t match number of sessions. Expected ' + str(
                len(attendance_session_row.sessions)) + ' but found ' + str(num_attendance_vals)
            return

        # Validate student - try finding by device ID first
        try:
            self.student = Student.objects.get(device_id=self.student_id)
        except Student.DoesNotExist:
            # Fallback: try to find by student code
            try:
                self.student = Student.objects.get(user__username=self.student_id)
            except Student.DoesNotExist:
                if self.error_message:
                    self.error_message += ', '
                self.error_message += 'Unrecognised student: ' + self.student_id

        for i in range(ATTENDANCE_VALS_START_COL, len(data)):
            attended_val = str(data[i]).strip()
            # Attended validation - âœ” = tick, âœ˜ = x - can appear this way due to formatting in CSV
            if not (attended_val.lower() in ['y', 'n', '1', '0', '✔', '✘', 'âœ”', 'âœ˜']):
                if self.error_message:
                    self.error_message += ', '
                self.error_message += 'Unrecognised attendance value for ' + self.student_id + ': ' + attended_val + ' at column ' + \
                                      str(i + 1)
            else:
                # Validation passed - add whether attended based on attendance value
                attendance = types.SimpleNamespace()
                attendance.session = attendance_session_row.sessions[i - ATTENDANCE_VALS_START_COL]
                attendance.attended = True if attended_val.lower() in ['y', '1', '✔', 'âœ”'] else False
                self.attendances.append(attendance)

    def get_error_message(self):
        """Get error message from parsing the attendance session row if exists.
        Acts as indicator for parse failure without raising exception during parsing.

        :return: error message if present
        """
        return self.error_message
