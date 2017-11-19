from .models import Student, Staff, Module, Lecture, StudentAttendance
import datetime
import types

# TODO: remove unrecogised restriction?
class ModuleRow:
  def __init__(self, data):
    self.module = data[0].strip()
    
  def get_error_message(self):
    error_message = ''

    try:
      valid_module = Module.objects.get(module_code=self.module)
    except Module.DoesNotExist:
      error_message += 'Unrecognised module: ' + self.module
      
    return error_message
  
class StaffRow:
  def __init__(self, data):
    self.lecturer = data[0].strip()
  
  def get_error_message(self):
    error_message = ''
    
    try:
      valid_lecturer = Staff.objects.get(user__username=self.lecturer)
    except Staff.DoesNotExist:
      error_message += 'Unrecognised lecturer: ' + self.lecturer

    return error_message
  
# one row, the column headers for attendance which give session id & date
class AttendanceSessionRow:
  def __init__(self, data):
    self.error_message = ''
    self.sessions = []
    # skip first column: Device ID
    for i in range(1, len(data)):
      if not data[i]:
        self.error_message = 'Unexpected empty session data at column ' + str(i)
        return
      
      session_data_parts = data[i].splitlines()
      if len(session_data_parts) != 2:
        self.error_message = 'Expected newline to separate date and session id for: ' + data[i] + ' at column ' + str(i)
        return
      
      date = str(session_data_parts[0]).strip()
      session_id = str(session_data_parts[1]).strip()
      
      if not date:
        self.error_message = 'Unexpected empty date at column ' + str(i)
        return
      if not session_id:
        self.error_message = 'Unexpected empty session id at column ' + str(i)
        return
      
      try:
        parsed_date = datetime.datetime.strptime(date, '%d/%m/%Y').date()
      except ValueError:
        self.error_message = 'Incorrect date format: ' + date + ', should be DD/MM/YYYY' + ' at column ' + str(i)
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
    self.student_device_id = data[0].strip()
    self.attendances = []
    
    # -1 because first column isn't a session
    if len(attendance_session_row.sessions) != (len(data) - 1):
      self.error_message = 'Number of data columns doesn\'t match number of sessions. Expected ' + str(len(attendance_session_row.sessions)) + ' but found ' + str(len(data) - 1)
      return
    
    # student validation
    try:
      self.student = Student.objects.get(device_id=self.student_device_id)
    except Student.DoesNotExist:
      if self.error_message:
        self.error_message += ', '
      self.error_message += 'Unrecognised student: ' + self.student_device_id
    
    for i in range(1, len(data)):
      attended_val = str(data[i]).strip()
      # attended validation - âœ” = tick, âœ˜ = x... ?
      if not (attended_val.lower() in ['y', 'n', '1', '0', '✔', '✘', 'âœ”', 'âœ˜']):
        if self.error_message:
          self.error_message += ', '
        self.error_message += 'Unrecognised attendance value for ' + self.student_device_id + ': ' + attended_val + ' at column ' + str(i)
      else:
        attendance = types.SimpleNamespace()
        attendance.session = attendance_session_row.sessions[i - 1]
        attendance.attended = True if attended_val.lower() in ['y', '1', '✔', 'âœ”'] else False
        self.attendances.append(attendance)
  
  def get_error_message(self):
    return self.error_message
