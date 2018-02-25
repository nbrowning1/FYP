from .models import Student, Staff, Module, Lecture, StudentAttendance
import datetime
import types

ATTENDANCE_VALS_START_COL = 3


# one row, the column headers for attendance which give session id & date
class AttendanceSessionRow:
    def __init__(self, data):
        self.error_message = ''
        self.sessions = []
        # skip first column: Device ID
        for i in range(ATTENDANCE_VALS_START_COL, len(data)):
            if not data[i]:
                self.error_message = 'Unexpected empty session data at column ' + str(i + 1)
                return

            session_data_parts = data[i].splitlines()
            if len(session_data_parts) != 2:
                self.error_message = 'Expected newline to separate date and session id for: ' + data[
                    i] + ' at column ' + str(i + 1)
                return

            date = str(session_data_parts[0]).strip()
            session_id = str(session_data_parts[1]).strip()

            if not date:
                self.error_message = 'Unexpected empty date at column ' + str(i + 1)
                return
            if not session_id:
                self.error_message = 'Unexpected empty session id at column ' + str(i + 1)
                return

            try:
                parsed_date = datetime.datetime.strptime(date, '%d/%m/%Y').date()
            except ValueError:
                self.error_message = 'Incorrect date format: ' + date + ', should be DD/MM/YYYY' + ' at column ' + str(
                    i + 1)
                return

            session = types.SimpleNamespace()
            session.date = parsed_date
            session.session_id = session_id
            self.sessions.append(session)

    def get_error_message(self):
        return self.error_message


class AttendanceRow:
    def __init__(self, attendance_session_row, data):
        self.error_message = ''
        self.student_id = data[0].strip()
        self.attendances = []

        num_attendance_vals = len(data) - ATTENDANCE_VALS_START_COL
        # could be less than 0 if less than ATTENDANCE_VALS_START_COL columns
        if num_attendance_vals < 0:
            num_attendance_vals = 0
        if len(attendance_session_row.sessions) != num_attendance_vals:
            self.error_message = 'Number of data columns doesn\'t match number of sessions. Expected ' + str(
                len(attendance_session_row.sessions)) + ' but found ' + str(num_attendance_vals)
            return

        # student validation
        # try finding by device ID first
        try:
            self.student = Student.objects.get(device_id=self.student_id)
        except Student.DoesNotExist:
            # then try to find by student code
            try:
                self.student = Student.objects.get(user__username=self.student_id)
            except Student.DoesNotExist:
                if self.error_message:
                    self.error_message += ', '
                self.error_message += 'Unrecognised student: ' + self.student_id

        for i in range(ATTENDANCE_VALS_START_COL, len(data)):
            attended_val = str(data[i]).strip()
            # attended validation - âœ” = tick, âœ˜ = x... ?
            if not (attended_val.lower() in ['y', 'n', '1', '0', '✔', '✘', 'âœ”', 'âœ˜']):
                if self.error_message:
                    self.error_message += ', '
                self.error_message += 'Unrecognised attendance value for ' + self.student_id + ': ' + attended_val + ' at column ' + \
                                      str(i + 1)
            else:
                attendance = types.SimpleNamespace()
                attendance.session = attendance_session_row.sessions[i - ATTENDANCE_VALS_START_COL]
                attendance.attended = True if attended_val.lower() in ['y', '1', '✔', 'âœ”'] else False
                self.attendances.append(attendance)

    def get_error_message(self):
        return self.error_message
