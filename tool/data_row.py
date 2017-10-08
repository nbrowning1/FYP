from .models import Student, Staff, Module, Lecture, StudentAttendance

# TODO: more validation e.g. format
class DataRow:
  def __init__(self, data):
    self.module = data[0].strip()
    self.lecturers = [lec.strip() for lec in data[1].split(";")]
    self.semester = data[2]
    self.week = data[3]
    self.student = data[4].strip()
    self.attended = str(data[5]).strip()
    
  def get_error_message(self):
    error_message = ''

    # module validation
    try:
      valid_module = Module.objects.get(module_code=self.module)
    except Module.DoesNotExist:
      error_message += 'Unrecognised module: ' + self.module

    # lecturers validation
    for lecturer in self.lecturers:
      try:
        valid_lecturer = Staff.objects.get(user__username=lecturer)
      except Staff.DoesNotExist:
        if error_message:
          error_message += ', '

        error_message += 'Unrecognised lecturer: ' + lecturer

    # semester validation
    try:
      if not (1 <= int(self.semester) <= 3):
        if error_message:
          error_message += ', '

        error_message += 'Semester %s out of range' % self.semester
    except ValueError:
      if error_message:
        error_message += ', '

      error_message += 'Invalid semester value %s' % self.semester

    # week validation
    try:
      if not (1 <= int(self.week) <= 12):
        if error_message:
          error_message += ', '

        error_message += 'Week %s out of range' % self.week
    except ValueError:
      if error_message:
        error_message += ', '

      error_message += 'Invalid week value %s' % self.week

    # student validation
    try:
      valid_student = Student.objects.get(user__username=self.student)
    except Student.DoesNotExist:
      if error_message:
        error_message += ', '

      error_message += 'Unrecognised student: ' + self.student

    # attended validation
    if not (self.attended.lower() in ['y', 'n', '1', '0']):
      if error_message:
        error_message += ', '

      error_message += 'Unrecognised attendance value: ' + self.attended
      
    return error_message
