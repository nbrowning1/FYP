from .data_rows import *
from .models import *


class DataSaver:
    def __init__(self, file_reader):
        self.file_reader = file_reader

    def save_uploaded_data(self, module):
        uploaded_list = []
        courses = []

        # grabbing attendance data
        attendance_session_data = None
        found_attendance = False
        for counter, row in enumerate(self.file_reader):
            # empty rows that can appear because of spreadsheet use
            if not ''.join(row).strip():
                continue

            if found_attendance:
                attendance_data = AttendanceRow(attendance_session_data, row)
                error_msg = attendance_data.get_error_message()
                if error_msg:
                    error_occurred_msg = 'Error with inputs: [[%s]] at line %s' % (error_msg, counter)
                    return error_response(error_occurred_msg)
                else:
                    uploaded_list.append(attendance_data)

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

            # associate student with module if not already associated
            if not any(uploaded_student.user.username == saved_stu.user.username for saved_stu in
                       module.students.all()):
                module.students.add(uploaded_student)

            for attendance_data in uploaded_data.attendances:
                session = attendance_data.session
                # TODO: extract outside so calls only performed once for lectures
                # create lectures if not already created
                lecture = Lecture.objects.filter(module=module,
                                                 session_id=session.session_id,
                                                 date=session.date).first()
                if not lecture:
                    new_lecture = Lecture(module=module, session_id=session.session_id, date=session.date)
                    new_lecture.save()
                    lecture = new_lecture

                # create attendance or update existing
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

        # remove duplicates
        courses = list(set(courses))
        # link module with any new courses from students
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
