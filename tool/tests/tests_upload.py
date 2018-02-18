import os

from django.test import TestCase
from django.urls import reverse

from .utils import TestUtils
from ..models import *


class UploadTests(TestCase):
    def test_upload_valid_data_csv(self):
        test_upload_valid_data(self, 'upload_test_valid.csv')

    def test_upload_valid_data_xls(self):
        test_upload_valid_data(self, 'Attendance_Test_xls.xls')

    def test_upload_valid_data_xlsx(self):
        test_upload_valid_data(self, 'Attendance_Test_xlsx.xlsx')

    def test_sequential_upload_replaces(self):
        TestUtils.authenticate_admin(self)
        create_db_props()
        test_upload(self, 'upload_test_valid.csv', 'code_EEE312 crn_EEE312-1', None)
        validate_valid_data(self, False)

        # upload same data, nothing should change in DB
        test_upload(self, 'upload_test_valid.csv', 'code_EEE312 crn_EEE312-1', None)
        validate_valid_data(self, False)

        # upload slightly altered data, should replace attendances that changed
        test_upload(self, 'upload_test_valid_replacement.csv', 'code_EEE312 crn_EEE312-1', None)
        validate_valid_data(self, True)

    def test_upload_unrecognised_module(self):
        TestUtils.authenticate_admin(self)
        # uploading valid data but without full DB setup
        test_upload(self, 'upload_test_valid.csv', 'code_EEE312 crn_EEE312-1',
                    'Unrecognised module for upload #1. Please select a module from the list.')

    def test_upload_unrecognised_student(self):
        TestUtils.authenticate_admin(self)
        TestUtils.create_staff('e00123456')
        TestUtils.create_staff('e00987654')
        TestUtils.create_module('EEE312', 'EEE312-1')
        # uploading valid data but without full DB setup
        test_upload(self, 'upload_test_valid.csv', 'code_EEE312 crn_EEE312-1',
                    'Error processing file upload_test_valid.csv: Error with inputs: [[Unrecognised student: 10519C]] at line 5')

    def test_upload_invalid_attendance_data(self):
        TestUtils.authenticate_admin(self)
        create_db_props()
        test_upload(self, 'upload_test_invalid.csv', 'code_EEE312 crn_EEE312-1',
                    'Error processing file upload_test_invalid.csv: Error with inputs: [[Unrecognised attendance value for 10519C: yes at column 4, Unrecognised attendance value for 10519C: no at column 7]] at line 5')

    def test_upload_incorrect_file_extension(self):
        TestUtils.authenticate_admin(self)
        create_db_props()
        test_upload(self, 'upload_test_wrong_ext.txt', 'code_EEE312 crn_EEE312-1',
                    'Invalid file type for upload #1. Only csv, xls, xlsx files are accepted.')

    def test_upload_no_file(self):
        TestUtils.authenticate_admin(self)
        create_db_props()
        test_upload(self, None, 'code_EEE312 crn_EEE312-1', 'No file uploaded. Please upload a .csv file.')

    def test_upload_multiple_files(self):
        TestUtils.authenticate_admin(self)
        create_db_props()
        test_multiple_upload(self, ['upload_test_valid.csv', 'upload_test_valid_2.csv'],
                             ['code_EEE312 crn_EEE312-1', 'code_COM999 crn_COM999-1'],
                             None)
        validate_multiple_data(self)

    # tests valid and invalid file, and tests that valid file was still uploaded
    def test_upload_multiple_files_invalid(self):
        TestUtils.authenticate_admin(self)
        create_db_props()
        self.assertEqual(len(StudentAttendance.objects.all()), 0)
        test_multiple_upload(self, ['upload_test_valid.csv', 'upload_test_invalid.csv'],
                             ['code_EEE312 crn_EEE312-1', 'code_COM999 crn_COM999-1'],
                             'Error processing file upload_test_invalid.csv: Error with inputs: [[Unrecognised attendance value for 10519C: yes at column 4, Unrecognised attendance value for 10519C: no at column 7]] at line 5')
        # make sure the valid file was still uploaded
        self.assertEqual(len(StudentAttendance.objects.all()), 12)

    def test_upload_usertype_permissions(self):
        create_db_props()

        self.assertEqual(get_module_student_count('EEE312'), 0)

        # student - forbidden
        TestUtils.authenticate_student(self)
        test_usertype_upload(self, 403)
        self.assertEqual(get_module_student_count('EEE312'), 0)

        # staff - forbidden
        TestUtils.authenticate_staff(self)
        test_usertype_upload(self, 403)
        self.assertEqual(get_module_student_count('EEE312'), 0)

        # admin is the only allowed user type - should be the only one to successfully upload
        TestUtils.authenticate_admin(self)
        test_usertype_upload(self, 200)
        self.assertEqual(get_module_student_count('EEE312'), 2)

    def test_unauthenticated_upload(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))

        res_path = os.path.join(this_dir, 'resources', 'upload_test_valid.csv')
        with open(res_path) as fp:
            response = self.client.post(reverse('tool:upload'), {'upload-data-0': fp}, follow=True)

        self.assertRedirects(response, '/tool/login/?next=/tool/upload/', status_code=302)


def test_upload_valid_data(self, resource_path):
    TestUtils.authenticate_admin(self)
    create_db_props()

    # initial check that module is not linked to student
    self.assertEqual(get_module_student_count('EEE312'), 0)
    # and that course has no linked modules
    self.assertEqual(len(get_course_modules('Course Code')), 0)

    test_upload(self, resource_path, 'code_EEE312 crn_EEE312-1', None)

    # post-upload check to assert that upload process linked module with students
    linked_module = Module.objects.get(module_code='EEE312')
    self.assertEqual(len(linked_module.students.all()), 2)
    self.assertEqual(linked_module.students.all()[0].user.username, 'B00123456')
    self.assertEqual(linked_module.students.all()[1].user.username, 'B00987654')

    # module should now be linked to course that students are part of
    course_modules = get_course_modules('Course Code')
    self.assertEqual(len(course_modules), 1)
    self.assertEqual(course_modules[0], linked_module)

    validate_valid_data(self, False)

    # TODO: assert upload confirmation page


def test_upload(self, file_path, module_str, expected_error_msg):
    response = self.client.get(reverse('tool:index'))
    self.assertEqual(response.status_code, 200)
    if expected_error_msg:
        self.assertNotContains(response, expected_error_msg)

    this_dir = os.path.dirname(os.path.abspath(__file__))
    # if no path specified, post without any upload data
    if file_path:
        res_path = os.path.join(this_dir, 'resources', file_path)
        with open(res_path, "rb") as fp:
            response = self.client.post(reverse('tool:upload'), {'upload-data-0': fp, 'module-0': module_str},
                                        follow=True)
    else:
        response = self.client.post(reverse('tool:upload'), follow=True)

    self.assertEqual(response.status_code, 200)

    # if no error message expected, check for successfully making it to upload confirmation page
    if expected_error_msg:
        self.assertEqual(response.request['PATH_INFO'], '/tool/')
        self.assertContains(response, expected_error_msg)
    else:
        self.assertEqual(response.request['PATH_INFO'], '/tool/upload/')

    return response


def test_multiple_upload(self, file_paths, module_strs, expected_error_msg):
    response = self.client.get(reverse('tool:index'))
    self.assertEqual(response.status_code, 200)
    if expected_error_msg:
        self.assertNotContains(response, expected_error_msg)

    this_dir = os.path.dirname(os.path.abspath(__file__))

    post_data = {}
    for i, file_path in enumerate(file_paths):
        res_path = os.path.join(this_dir, 'resources', file_path)
        post_data["upload-data-" + str(i)] = (open(res_path))
    for i, module_str in enumerate(module_strs):
        post_data["module-" + str(i)] = module_str

    response = self.client.post(reverse('tool:upload'), post_data, follow=True)

    self.assertEqual(response.status_code, 200)

    # if no error message expected, check for successfully making it to upload confirmation page
    if expected_error_msg:
        self.assertEqual(response.request['PATH_INFO'], '/tool/')
        self.assertContains(response, expected_error_msg)
    else:
        self.assertEqual(response.request['PATH_INFO'], '/tool/upload/')

    return response


def test_usertype_upload(self, expected_status_code):
    response = self.client.get(reverse('tool:index'))
    self.assertEqual(response.status_code, 200)

    this_dir = os.path.dirname(os.path.abspath(__file__))

    res_path = os.path.join(this_dir, 'resources', 'upload_test_valid.csv')
    with open(res_path) as fp:
        response = self.client.post(reverse('tool:upload'),
                                    {'upload-data-0': fp, 'module-0': 'code_EEE312 crn_EEE312-1'},
                                    follow=True)

    self.assertEqual(response.status_code, expected_status_code)

    self.assertEqual(response.request['PATH_INFO'], '/tool/upload/')


def get_module_student_count(module_code):
    module = Module.objects.get(module_code=module_code)
    return len(module.students.all())


def get_course_modules(course_code):
    course = Course.objects.get(course_code=course_code)
    return course.modules.all()


def create_db_props():
    create_student('B00123456', '10519C')
    create_student('B00987654', '10518B')
    TestUtils.create_staff('e00123456')
    TestUtils.create_staff('e00987654')
    TestUtils.create_staff('e00555555')
    TestUtils.create_staff('e00666666')
    TestUtils.create_module('EEE312', 'EEE312-1')
    TestUtils.create_module('COM999', 'COM999-1')


def create_student(username, device_id):
    user = User.objects.create_user(username=username, password='12345')
    course = TestUtils.create_course('Course Code')
    student = Student(user=user, device_id=device_id, course=course)
    student.save()
    return student


def validate_valid_data(self, expect_replaced):
    lectures = Lecture.objects.all()
    self.assertEqual(len(lectures), 6)
    # should all be linked to module
    self.assertEqual(lectures[0].module.module_code, 'EEE312')
    self.assertEqual(lectures[5].module.module_code, 'EEE312')
    self.assertEqual(lectures[0].session_id, '170925 1228')
    self.assertEqual(lectures[1].session_id, 'EEE122 170926 1138')
    self.assertEqual(lectures[2].session_id, 'EEE122 171002 1211')
    self.assertEqual(lectures[3].session_id, 'EEE122/3-10-2017 171003 1526')
    self.assertEqual(lectures[4].session_id, 'EEE122_Lecture 171003 1010')
    self.assertEqual(lectures[5].session_id, 'EEE122/171005 0949')

    attendances = StudentAttendance.objects.all()
    self.assertEqual(len(attendances), 12)
    # first 6 linked to first student..
    self.assertEqual(attendances[0].student.user.username, 'B00123456')
    self.assertEqual(attendances[5].student.user.username, 'B00123456')
    self.assertEqual(attendances[0].lecture.session_id, '170925 1228')
    self.assertEqual(attendances[5].lecture.session_id, 'EEE122/171005 0949')
    self.assertEqual(attendances[0].attended, True)
    self.assertEqual(attendances[1].attended, True)
    self.assertEqual(attendances[2].attended, True)
    self.assertEqual(attendances[3].attended, False)
    self.assertEqual(attendances[4].attended, True)
    if expect_replaced:
        self.assertEqual(attendances[5].attended, True)
    else:
        self.assertEqual(attendances[5].attended, False)

    # ..last 6 to second student
    self.assertEqual(attendances[6].student.user.username, 'B00987654')
    self.assertEqual(attendances[11].student.user.username, 'B00987654')
    self.assertEqual(attendances[6].lecture.session_id, '170925 1228')
    self.assertEqual(attendances[11].lecture.session_id, 'EEE122/171005 0949')
    if expect_replaced:
        self.assertEqual(attendances[6].attended, True)
    else:
        self.assertEqual(attendances[6].attended, False)
    self.assertEqual(attendances[7].attended, True)
    self.assertEqual(attendances[8].attended, True)
    self.assertEqual(attendances[9].attended, True)
    self.assertEqual(attendances[10].attended, True)
    self.assertEqual(attendances[11].attended, False)


def validate_multiple_data(self):
    lectures = Lecture.objects.all()
    self.assertEqual(len(lectures), 12)
    # should all be linked to respective modules
    self.assertEqual(lectures[0].module.module_code, 'EEE312')
    self.assertEqual(lectures[5].module.module_code, 'EEE312')
    self.assertEqual(lectures[0].session_id, '170925 1228')
    self.assertEqual(lectures[1].session_id, 'EEE122 170926 1138')
    self.assertEqual(lectures[2].session_id, 'EEE122 171002 1211')
    self.assertEqual(lectures[3].session_id, 'EEE122/3-10-2017 171003 1526')
    self.assertEqual(lectures[4].session_id, 'EEE122_Lecture 171003 1010')
    self.assertEqual(lectures[5].session_id, 'EEE122/171005 0949')

    self.assertEqual(lectures[6].module.module_code, 'COM999')
    self.assertEqual(lectures[11].module.module_code, 'COM999')
    self.assertEqual(lectures[6].session_id, '170925 1228')
    self.assertEqual(lectures[7].session_id, 'EEE122 170926 1138')
    self.assertEqual(lectures[8].session_id, 'EEE122 171002 1211')
    self.assertEqual(lectures[9].session_id, 'EEE122/3-10-2017 171003 1526')
    self.assertEqual(lectures[10].session_id, 'EEE122_Lecture 171003 1010')
    self.assertEqual(lectures[11].session_id, 'EEE122/171005 0949')

    attendances = StudentAttendance.objects.all()
    self.assertEqual(len(attendances), 24)
