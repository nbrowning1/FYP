from xlrd import open_workbook

from .data_rows import *
from .models import *


class DataSaver:
    """Helper to allow saving attendance data from different formats."""

    @staticmethod
    def save_uploaded_data_csv(file_reader, module):
        """Save attendance data from CSV to DB.

        :param file_reader: CSV reader for file containing attendance data
        :param module: module to store attendance data for
        :return: saved data if successful, otherwise error object
        """
        return save_uploaded_data(file_reader, module)

    @staticmethod
    def save_uploaded_data_excel(file_contents, module):
        """Save attendance data from Excel file to DB.

        :param file_contents: file contents for xls/xlsx file containing attendance data
        :param module: module to store attendance data for
        :return: saved data if successful, otherwise error object
        """

        # Open excel workbook and get first sheet to target data
        workbook = open_workbook(file_contents=file_contents)
        sheet = workbook.sheet_by_index(0)

        # Build list of lists to represent the data from spreadsheet (cell data per row)
        rows = []
        for counter in range(sheet.nrows):
            row = []
            for col_index in range(sheet.ncols):
                row.append(sheet.cell(counter, col_index).value)
            rows.append(row)

        return save_uploaded_data(rows, module)


def save_uploaded_data(rows_enumerable, module):
    """Save attendance data into DB.

    :param rows_enumerable: data for attendance as a list of lists (cell data per row)
    :param module: module to save attendance for
    :return: saved data if successful, otherwise error object
    """

    uploaded_list = []
    courses = []

    attendance_session_data = None
    found_attendance = False

    for counter, row in enumerate(rows_enumerable):
        # Empty rows that can appear because of spreadsheet use - just move to next row
        if not ''.join(row).strip():
            continue

        # If we've found attendance data, translate data to AttendanceRow, return error if failure to parse
        # Otherwise keep looking for session data to translate to AttendanceSessionRow
        if found_attendance:
            attendance_data = AttendanceRow(attendance_session_data, row)
            error_msg = attendance_data.get_error_message()
            if error_msg:
                error_occurred_msg = 'Error with inputs: [[%s]] at line %s' % (error_msg, counter)
                return error_response(error_occurred_msg)
            else:
                uploaded_list.append(attendance_data)
        else:
            # Look for indicator for attendance column headers so we can fetch session data
            if row[0].strip() != 'Device ID(s)':
                continue
            else:
                found_attendance = True
                attendance_session_data = AttendanceSessionRow(row)
                error_msg = attendance_session_data.get_error_message()
                if error_msg:
                    return error_response(error_msg)
                continue

    for uploaded_data in uploaded_list:
        uploaded_student = uploaded_data.student
        courses.append(uploaded_student.course)

        # Associate student with module if not already associated
        if not any(uploaded_student.user.username == saved_stu.user.username for saved_stu in
                   module.students.all()):
            module.students.add(uploaded_student)

        for attendance_data in uploaded_data.attendances:
            session = attendance_data.session

            # Find lecture that already exists with this criteria...
            lecture = Lecture.objects.filter(module=module,
                                             session_id=session.session_id,
                                             date=session.date).first()
            # ... and create new lecture if not found
            if not lecture:
                new_lecture = Lecture(module=module, session_id=session.session_id, date=session.date)
                new_lecture.save()
                lecture = new_lecture

            # Create new attendance or update existing
            attended = attendance_data.attended
            stud_attendance = StudentAttendance.objects.filter(student=uploaded_student,
                                                               lecture=lecture).first()
            if stud_attendance:
                stud_attendance.attended = attended
                stud_attendance.save()
            else:
                new_attendance = StudentAttendance(student=uploaded_student,
                                                   lecture=lecture,
                                                   attended=attended)
                new_attendance.save()

    # Remove duplicate courses
    courses = list(set(courses))
    # Link module with any new courses that are linked with students
    for course in courses:
        if module not in course.modules.all():
            course.modules.add(module)

    uploaded_data = types.SimpleNamespace()
    uploaded_data.module = module
    uploaded_data.attendances = uploaded_list
    uploaded_data.courses = courses
    return uploaded_data


def error_response(msg):
    response = types.SimpleNamespace()
    response.error = msg
    return response
