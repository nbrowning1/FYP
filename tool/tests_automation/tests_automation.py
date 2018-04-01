import os
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.wait import WebDriverWait

from tool.models import StudentAttendance
from tool.tests.utils import TestUtils

DRIVER_WAIT_IN_S = 10

STUDENT_USERNAME = 'B00112233'
STAFF_USERNAME = 'e00112233'
TEST_PASSWORD = '12345'

LOGIN_USERNAME_ID = 'id_username'
LOGIN_PASSWORD_ID = 'id_password'

HOME_BUTTON_XPATH = ".//*[text()='Home']"
PAGE_INDICATOR_XPATH = ".//h2[text()='{}']"
USER_DROPDOWN_ID = "user-dropdown"
INDEX_PAGE_INDICATOR_XPATH = PAGE_INDICATOR_XPATH.format('Home')
CONTAINER_BUTTON_XPATH = ".//*[@class='link-container']//a[text()='{}']"
INDEX_MODULES_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Modules')
INDEX_COURSES_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Courses')
INDEX_LECTURERS_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Lecturers')
INDEX_STUDENTS_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Students')
INDEX_LECTURES_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Lectures')
ATTENDANCE_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Attendance')
INDEX_MODULES_CONTAINER_ID = 'modules-container'
INDEX_COURSES_CONTAINER_ID = 'courses-container'
INDEX_LECTURERS_CONTAINER_ID = 'lecturers-container'
INDEX_STUDENTS_CONTAINER_ID = 'students-container'
INDEX_LECTURES_CONTAINER_ID = 'lectures-container'
INDEX_CONTAINER_TABLE_ROWS_XPATH = ".//*[@id='{}']//tbody//tr"
INDEX_MODULES_TABLE_ROWS_XPATH = INDEX_CONTAINER_TABLE_ROWS_XPATH.format('modules-tbl')
INDEX_COURSES_TABLE_ROWS_XPATH = INDEX_CONTAINER_TABLE_ROWS_XPATH.format('courses-tbl')
INDEX_LECTURERS_TABLE_ROWS_XPATH = INDEX_CONTAINER_TABLE_ROWS_XPATH.format('lecturers-tbl')
INDEX_STUDENTS_TABLE_ROWS_XPATH = INDEX_CONTAINER_TABLE_ROWS_XPATH.format('students-tbl')
INDEX_LECTURES_TABLE_ROWS_XPATH = INDEX_CONTAINER_TABLE_ROWS_XPATH.format('lectures-tbl')
ATTENDANCE_TABLE_ROWS_XPATH = ".//*[@id='attendance-container']//table//tr"

FEEDBACK_TAB_XPATH = ".//*[@data-toggle='tab' and text()='Feedback']"
NO_FEEDBACK_TEXT_XPATH = ".//*[text()='No feedback is available.']"
GIVE_FEEDBACK_BTN_XPATH = ".//*[text()='Give Feedback']"
FEEDBACK_ROW_CLASS = "feedback-row"
FEEDBACK_FORM_ID = "feedback-submit"
FEEDBACK_GENERAL_ID = "id_feedback_general"
FEEDBACK_POSITIVE_ID = "id_feedback_positive"
FEEDBACK_CONSTRUCTIVE_ID = "id_feedback_constructive"
FEEDBACK_OTHER_ID = "id_feedback_other"
FEEDBACK_ANONYMOUS_ID = "id_anonymous"

SETTINGS_COLOURBLIND_CHECKBOX_NAME = "colourblind-opts"
SETTINGS_ACCESSIBILITY_SUBMIT_BTN_NAME = "accessibility-submit"
SETTINGS_ATTENDANCE_RANGE1_ID = "attendance-range-1"
SETTINGS_ATTENDANCE_RANGE2_ID = "attendance-range-2"
SETTINGS_ATTENDANCE_RANGE3_ID = "attendance-range-3"
SETTINGS_ATTENDANCE_SUBMIT_BTN_NAME = "attendance-submit"

MODULE_COURSE_SETTINGS_TABLE_ROWS_XPATH = ".//*[@id='{}']//tbody//tr"
MODULE_SETTINGS_TABLE_ROWS_XPATH = MODULE_COURSE_SETTINGS_TABLE_ROWS_XPATH.format("modules-container")
COURSE_SETTINGS_TABLE_ROWS_XPATH = MODULE_COURSE_SETTINGS_TABLE_ROWS_XPATH.format("courses-container")

UPLOAD_ATTENDANCE_FORM_ID = "attendance-upload-form"
UPLOAD_ROW_XPATH = ".//*[@class='container upload-row' and not(@id='placeholder')]"
UPLOAD_ADD_ROW_ID = "add-upload-row"
UPLOAD_DELETE_ROW_CLASS = "delete-upload-row"
UPLOAD_INPUT_CLASS = "file-upload"
UPLOAD_MODULE_SELECT_CLASS = "chosen-single"
UPLOAD_MODULE_SELECT_ITEM_XPATH = ".//*[@class='active-result' and text()='{}']"
UPLOAD_RESULTS_ID = "upload-results"


class AutomationTests(StaticLiveServerTestCase):
    driver = None
    waiter = None

    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        self.waiter = WebDriverWait(self.driver, DRIVER_WAIT_IN_S)
        self.driver.implicitly_wait(DRIVER_WAIT_IN_S)

    def tearDown(self):
        self.driver.quit()

    def test_app_student(self):
        setup_data()
        soft_failures = []

        try:
            test_login(self, STUDENT_USERNAME)
            soft_failures.append(test_index_page_student(self))
            go_to_module(self, 'COM101')
            soft_failures.append(test_module_view_attendance(self, 'COM101'))
            self.driver.find_element_by_xpath(FEEDBACK_TAB_XPATH).click()
            soft_failures.append(test_module_view_feedback_student(self))
            go_to_index(self)
            open_containers_student(self)
            go_to_lecture(self, 'mod1 lec1')
            soft_failures.append(test_lecture_view(self, 'Dec. 1, 2017 - mod1 lec1'))
            go_to_settings(self)
            soft_failures.append(test_settings(self))
            logout(self)
        except Exception as e:
            soft_failures.append('Something went wrong: ' + str(e))

        output_failures(soft_failures)

    def test_app_staff(self):
        setup_data()
        soft_failures = []

        try:
            test_login(self, STAFF_USERNAME)
            self.driver.find_element_by_xpath(".//*[@id='content']//*[@class='settings']").click()
            soft_failures.append(test_module_course_settings(self))
            soft_failures.append(test_index_page_staff(self))
            # module
            go_to_module(self, 'COM101')
            soft_failures.append(test_module_view_attendance(self, 'COM101'))
            self.driver.find_element_by_xpath(FEEDBACK_TAB_XPATH).click()
            soft_failures.append(test_module_view_feedback_staff(self))
            # course
            go_to_index(self)
            open_containers_staff(self)
            go_to_course(self, 'Course Code')
            soft_failures.append(test_course_view(self, 'Course Code'))
            # staff
            go_to_index(self)
            open_containers_staff(self)
            go_to_lecturer(self, STAFF_USERNAME)
            soft_failures.append(test_lecturer_view(self, STAFF_USERNAME))
            # student
            go_to_index(self)
            open_containers_staff(self)
            go_to_student(self, STUDENT_USERNAME)
            soft_failures.append(test_student_view(self, STUDENT_USERNAME))
            # lecture
            go_to_index(self)
            open_containers_staff(self)
            go_to_lecture(self, 'mod1 lec1')
            soft_failures.append(test_lecture_view(self, 'Dec. 1, 2017 - mod1 lec1'))
            # upload
            go_to_index(self)
            soft_failures.append(test_upload(self))
            go_to_settings(self)
            soft_failures.append(test_settings(self))
            logout(self)
        except Exception as e:
            soft_failures.append('Something went wrong: ' + str(e))

        output_failures(soft_failures)


def output_failures(failures):
    filtered = []
    for failure in failures:
        if failure:
            filtered.append(failure)

    if len(filtered) > 0:
        raise Exception("Test issues: " + ", ".join(filtered))


def is_visible(self, by, locator):
    try:
        self.waiter.until(expect.visibility_of_element_located((by, locator)))
        return True
    except TimeoutException:
        return False


def setup_data():
    student = TestUtils.create_student(STUDENT_USERNAME)
    TestUtils.create_staff(STAFF_USERNAME)
    course = TestUtils.create_course('Course Code')
    module_1 = TestUtils.create_module('COM101', 'COM101-crn')
    module_2 = TestUtils.create_module('COM999', 'COM999-crn')
    module_3 = TestUtils.create_module('EEE101', 'EEE101-crn')
    module_1_lecture_1 = TestUtils.create_lecture(module_1, 'mod1 lec1')
    module_1_lecture_2 = TestUtils.create_lecture(module_1, 'mod1 lec2')
    module_2_lecture_1 = TestUtils.create_lecture(module_2, 'mod2 lec1')
    course.modules.add(module_1)
    course.modules.add(module_2)

    module_1.students.add(student)
    module_2.students.add(student)

    # add student attendance
    TestUtils.create_attendance(student, module_1_lecture_1, False)
    TestUtils.create_attendance(student, module_1_lecture_2, True)
    TestUtils.create_attendance(student, module_2_lecture_1, True)


def test_login(self, username):
    try:
        # hit the app
        self.driver.get(self.live_server_url + '/tool')
        # handle login page
        self.driver.find_element_by_id(LOGIN_USERNAME_ID).send_keys(username)
        self.driver.find_element_by_id(LOGIN_PASSWORD_ID).send_keys(TEST_PASSWORD)
        self.driver.find_element_by_tag_name('form').submit()
        # check that we've reached index page
        self.assertTrue(is_visible(self, By.XPATH, INDEX_PAGE_INDICATOR_XPATH))
    except Exception as e:
        raise Exception('Failure to handle login page: ' + str(e))


def test_index_page_student(self):
    try:
        # open containers
        open_containers_student(self)
        # check that they become visible
        self.assertTrue(is_visible(self, By.ID, INDEX_MODULES_CONTAINER_ID))
        self.assertTrue(is_visible(self, By.ID, INDEX_LECTURES_CONTAINER_ID))
        # assert expected number of rows
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_MODULES_TABLE_ROWS_XPATH)), 2)
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_LECTURES_TABLE_ROWS_XPATH)), 3)
    except Exception as e:
        return 'Issues occurred validating index page: ' + str(e)


def test_index_page_staff(self):
    try:
        # open containers
        open_containers_staff(self)
        # check that they become visible
        self.assertTrue(is_visible(self, By.ID, INDEX_MODULES_CONTAINER_ID))
        self.assertTrue(is_visible(self, By.ID, INDEX_COURSES_CONTAINER_ID))
        self.assertTrue(is_visible(self, By.ID, INDEX_LECTURERS_CONTAINER_ID))
        self.assertTrue(is_visible(self, By.ID, INDEX_STUDENTS_CONTAINER_ID))
        self.assertTrue(is_visible(self, By.ID, INDEX_LECTURES_CONTAINER_ID))
        # assert expected number of rows
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_MODULES_TABLE_ROWS_XPATH)), 3)
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_COURSES_TABLE_ROWS_XPATH)), 1)
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_LECTURERS_TABLE_ROWS_XPATH)), 1)
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_STUDENTS_TABLE_ROWS_XPATH)), 1)
        self.assertEqual(len(self.driver.find_elements_by_xpath(INDEX_LECTURES_TABLE_ROWS_XPATH)), 3)
    except Exception as e:
        return 'Issues occurred validating index page: ' + str(e)


def test_module_view_attendance(self, module_code):
    try:
        # check we're on correct module page
        self.assertTrue(is_visible(self, By.XPATH, PAGE_INDICATOR_XPATH.format(module_code)))
        # open attendances
        self.driver.find_element_by_xpath(ATTENDANCE_CONTAINER_BTN_XPATH).click()
        # get attendance rows (removing first 2 because of double-headers
        self.assertTrue(is_visible(self, By.XPATH, ATTENDANCE_TABLE_ROWS_XPATH))
        # short sleep to allow the table to open
        time.sleep(1)
        attendance_rows = self.driver.find_elements_by_xpath(ATTENDANCE_TABLE_ROWS_XPATH)[2:]
        # should be 1 row and 4 cells - student code, 2 attendances and summary
        self.assertEqual(len(attendance_rows), 1)
        row_cells = attendance_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(row_cells), 4)
        # validate summary % cell
        self.assertEqual(row_cells[3].text, '50.00%')
    except Exception as e:
        return 'Issues occurred validating module view attendance: ' + str(e)


def test_module_view_feedback_student(self):
    try:
        # validate no feedback
        self.assertTrue(is_visible(self, By.XPATH, NO_FEEDBACK_TEXT_XPATH))
        # go to give feedback
        self.assertTrue(is_visible(self, By.XPATH, GIVE_FEEDBACK_BTN_XPATH))
        self.driver.find_element_by_xpath(GIVE_FEEDBACK_BTN_XPATH).click()
        # wait for feedback form
        self.assertTrue(is_visible(self, By.ID, FEEDBACK_FORM_ID))
        # fill out feedback
        self.driver.find_element_by_id(FEEDBACK_GENERAL_ID).send_keys('general')
        self.driver.find_element_by_id(FEEDBACK_POSITIVE_ID).send_keys('positive')
        self.driver.find_element_by_id(FEEDBACK_CONSTRUCTIVE_ID).send_keys('constructive')
        self.driver.find_element_by_id(FEEDBACK_OTHER_ID).send_keys('other')
        self.driver.find_element_by_id(FEEDBACK_ANONYMOUS_ID).click()
        self.driver.find_element_by_id(FEEDBACK_FORM_ID).submit()
        # should redirect back to module
        self.assertTrue(is_visible(self, By.XPATH, FEEDBACK_TAB_XPATH))
        self.driver.find_element_by_xpath(FEEDBACK_TAB_XPATH).click()
        self.assertEqual(len(self.driver.find_elements_by_class_name(FEEDBACK_ROW_CLASS)), 1)
    except Exception as e:
        return 'Issues occurred validating module view feedback: ' + str(e)


def test_module_view_feedback_staff(self):
    try:
        # validate no feedback
        self.assertTrue(is_visible(self, By.XPATH, NO_FEEDBACK_TEXT_XPATH))
        # add feedback via DB and check again
        student = TestUtils.create_student(STUDENT_USERNAME)
        module = TestUtils.create_module('COM101', 'COM101-crn')
        # should appear on page in this order because of dates
        TestUtils.create_feedback(student, module, 'feedback-text', True, "2017-12-20")
        TestUtils.create_feedback(student, module, 'feedback-text', False, "2017-12-10")
        # refresh and navigate to feedback tab again
        self.driver.refresh()
        self.driver.find_element_by_xpath(FEEDBACK_TAB_XPATH).click()
        feedbacks = self.driver.find_elements_by_class_name(FEEDBACK_ROW_CLASS)
        self.assertEqual(len(feedbacks), 2)
        # check order of feedbacks and anonymity
        self.assertEqual(feedbacks[0].find_element_by_class_name('feedback-user').text, 'Anonymous')
        self.assertEqual(feedbacks[0].find_element_by_class_name('feedback-date').text, 'Dec. 20, 2017')
        self.assertEqual(feedbacks[1].find_element_by_class_name('feedback-user').text, STUDENT_USERNAME)
        self.assertEqual(feedbacks[1].find_element_by_class_name('feedback-date').text, 'Dec. 10, 2017')
    except Exception as e:
        return 'Issues occurred validating module view feedback: ' + str(e)


def test_course_view(self, course_code):
    try:
        # check we're on correct course page
        self.assertTrue(is_visible(self, By.XPATH, PAGE_INDICATOR_XPATH.format(course_code)))
        # open attendances
        self.driver.find_element_by_xpath(ATTENDANCE_CONTAINER_BTN_XPATH).click()
        # get attendance rows
        self.assertTrue(is_visible(self, By.XPATH, ATTENDANCE_TABLE_ROWS_XPATH))
        # short sleep to allow the table to open
        time.sleep(1)
        attendance_rows = self.driver.find_elements_by_xpath(ATTENDANCE_TABLE_ROWS_XPATH)[1:]
        # should be 2 rows and 2 cells
        self.assertEqual(len(attendance_rows), 2)
        row_cells = attendance_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(row_cells), 2)
    except Exception as e:
        return 'Issues occurred validating course view: ' + str(e)


def test_lecturer_view(self, staff_code):
    try:
        # check we're on correct course page
        self.assertTrue(is_visible(self, By.XPATH, PAGE_INDICATOR_XPATH.format(staff_code)))
        # open attendances
        self.driver.find_element_by_xpath(ATTENDANCE_CONTAINER_BTN_XPATH).click()
        # get attendance rows
        self.assertTrue(is_visible(self, By.XPATH, ATTENDANCE_TABLE_ROWS_XPATH))
        # short sleep to allow the table to open
        time.sleep(1)
        attendance_rows = self.driver.find_elements_by_xpath(ATTENDANCE_TABLE_ROWS_XPATH)[1:]
        # should be 3 rows and 2 cells
        self.assertEqual(len(attendance_rows), 3)
        row_cells = attendance_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(row_cells), 2)
    except Exception as e:
        return 'Issues occurred validating lecturer view: ' + str(e)


def test_student_view(self, student_code):
    try:
        # check we're on correct course page
        self.assertTrue(is_visible(self, By.XPATH, PAGE_INDICATOR_XPATH.format(student_code)))
        # open attendances
        module_accordion_panels = self.driver.find_elements_by_class_name('panel-title')
        for panel in module_accordion_panels:
            panel.click()
        # short sleep to allow the table to open
        time.sleep(1)
        accordion_panels = self.driver.find_elements_by_class_name('panel-body')

        # first panel should have 4 cells - student, 2 lectures and summary
        first_module_panel = accordion_panels[0]
        attendance_rows = first_module_panel.find_elements_by_xpath(".//table//tr")[2:]
        self.assertEqual(len(attendance_rows), 1)
        row_cells = attendance_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(row_cells), 4)

        # second panel should have 3 cells - student, only 1 lecture and summary
        second_module_panel = accordion_panels[1]
        attendance_rows = second_module_panel.find_elements_by_xpath(".//table//tr")[2:]
        self.assertEqual(len(attendance_rows), 1)
        row_cells = attendance_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(row_cells), 3)
    except Exception as e:
        return 'Issues occurred validating student view: ' + str(e)


def test_lecture_view(self, title_text):
    try:
        # check we're on correct lecture page
        self.assertTrue(is_visible(self, By.XPATH, PAGE_INDICATOR_XPATH.format(title_text)))
        # open attendances
        self.driver.find_element_by_xpath(ATTENDANCE_CONTAINER_BTN_XPATH).click()
        # get attendance rows
        self.assertTrue(is_visible(self, By.XPATH, ATTENDANCE_TABLE_ROWS_XPATH))
        # short sleep to allow the table to open
        time.sleep(1)
        attendance_rows = self.driver.find_elements_by_xpath(ATTENDANCE_TABLE_ROWS_XPATH)[1:]
        # should be 1 row and 2 cells
        self.assertEqual(len(attendance_rows), 1)
        row_cells = attendance_rows[0].find_elements_by_tag_name('td')
        self.assertEqual(len(row_cells), 2)
    except Exception as e:
        return 'Issues occurred validating lecture view: ' + str(e)


def test_settings(self):
    try:
        self.assertTrue(is_visible(self, By.XPATH, PAGE_INDICATOR_XPATH.format('Settings')))
        # validate initial settings
        self.assertFalse(self.driver.find_element_by_name(SETTINGS_COLOURBLIND_CHECKBOX_NAME).is_selected())
        self.assertEqual(self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE1_ID).get_attribute('value'), '25')
        self.assertEqual(self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE2_ID).get_attribute('value'), '50')
        self.assertEqual(self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE3_ID).get_attribute('value'), '75')
        # save new accessibility settings
        self.driver.find_element_by_name(SETTINGS_COLOURBLIND_CHECKBOX_NAME).click()
        self.driver.find_element_by_name(SETTINGS_ACCESSIBILITY_SUBMIT_BTN_NAME).click()
        # save new attendance range settings
        self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE1_ID).clear()
        self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE2_ID).clear()
        self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE3_ID).clear()
        self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE1_ID).send_keys(50)
        self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE2_ID).send_keys(75)
        self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE3_ID).send_keys(90)
        self.driver.find_element_by_name(SETTINGS_ATTENDANCE_SUBMIT_BTN_NAME).click()
        # go back to home then settings to validate new settings
        go_to_index(self)
        go_to_settings(self)
        # validate new settings
        self.assertTrue(self.driver.find_element_by_name(SETTINGS_COLOURBLIND_CHECKBOX_NAME).is_selected())
        self.assertEqual(self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE1_ID).get_attribute('value'), '50')
        self.assertEqual(self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE2_ID).get_attribute('value'), '75')
        self.assertEqual(self.driver.find_element_by_id(SETTINGS_ATTENDANCE_RANGE3_ID).get_attribute('value'), '90')
    except Exception as e:
        return 'Issues occurred validating lecture view: ' + str(e)


def test_module_course_settings(self):
    try:
        open_containers_module_course_settings(self)
        # assert expected number of modules and courses
        module_rows = self.driver.find_elements_by_xpath(MODULE_SETTINGS_TABLE_ROWS_XPATH)
        course_rows = self.driver.find_elements_by_xpath(COURSE_SETTINGS_TABLE_ROWS_XPATH)
        self.assertEquals(len(module_rows), 3)
        self.assertEquals(len(course_rows), 1)
        # set everything to checked
        for row in module_rows:
            row.find_element_by_name('modules[]').click()
        for row in course_rows:
            row.find_element_by_name('courses[]').click()
        # submit changes
        self.driver.find_element_by_tag_name('form').submit()
        # check that we navigate back to index page
        self.assertTrue(is_visible(self, By.XPATH, INDEX_PAGE_INDICATOR_XPATH))
    except Exception as e:
        return 'Issues occurred validating module/course settings: ' + str(e)


def test_upload(self):
    try:
        self.driver.find_element_by_xpath(".//a[text()='Upload']").click()
        # assert no upload containers
        self.assertEqual(len(self.driver.find_elements_by_xpath(UPLOAD_ROW_XPATH)), 1)
        # add some upload containers
        add_button = self.driver.find_element_by_id(UPLOAD_ADD_ROW_ID)
        add_button.click()
        add_button.click()
        upload_rows = self.driver.find_elements_by_xpath(UPLOAD_ROW_XPATH)
        self.assertEqual(len(upload_rows), 3)
        # remove two from middle
        upload_rows[0].find_element_by_class_name(UPLOAD_DELETE_ROW_CLASS).click()
        upload_rows = self.driver.find_elements_by_xpath(UPLOAD_ROW_XPATH)
        upload_rows[0].find_element_by_class_name(UPLOAD_DELETE_ROW_CLASS).click()
        upload_rows = self.driver.find_elements_by_xpath(UPLOAD_ROW_XPATH)
        self.assertEqual(len(upload_rows), 1)
        # add upload data
        upload_file(self, upload_rows[0].find_element_by_class_name(UPLOAD_INPUT_CLASS))
        # validate number of attendances before upload
        self.assertEqual(len(StudentAttendance.objects.all()), 3)
        set_module(upload_rows[0], 'COM999 - COM999-crn')
        self.driver.find_element_by_id(UPLOAD_ATTENDANCE_FORM_ID).submit()
        time.sleep(5)
        # validate that new 6 attendances added
        self.assertEqual(len(StudentAttendance.objects.all()), 9)
        # assert single upload shown on page
        upload_results_container = self.driver.find_element_by_id(UPLOAD_RESULTS_ID)
        upload_titles = upload_results_container.find_elements_by_class_name('upload-title')
        self.assertEqual(len(upload_titles), 1)
    except Exception as e:
        return 'Issues occurred with upload: ' + str(e)


def upload_file(self, file_input):
    # make input visible to selenium
    self.driver.execute_script("arguments[0].style.display='block'", file_input)
    time.sleep(1)
    this_dir = os.path.dirname(os.path.abspath(__file__))
    res_path = os.path.join(this_dir, 'upload.xlsx')
    file_input.send_keys(res_path)
    time.sleep(1)


def set_module(attendance_row, selection):
    attendance_row.find_element_by_class_name(UPLOAD_MODULE_SELECT_CLASS).click()
    attendance_row.find_element_by_xpath(UPLOAD_MODULE_SELECT_ITEM_XPATH.format(selection)).click()


def logout(self):
    try:
        go_to_logout(self)
        self.assertTrue(is_visible(self, By.ID, LOGIN_USERNAME_ID))
        self.assertTrue(is_visible(self, By.ID, LOGIN_PASSWORD_ID))
    except Exception as e:
        raise Exception('Failure to handle logout: ' + str(e))


def open_containers_student(self):
    self.driver.find_element_by_xpath(INDEX_MODULES_CONTAINER_BTN_XPATH).click()
    self.driver.find_element_by_xpath(INDEX_LECTURES_CONTAINER_BTN_XPATH).click()


def open_containers_staff(self):
    self.driver.find_element_by_xpath(INDEX_MODULES_CONTAINER_BTN_XPATH).click()
    self.driver.find_element_by_xpath(INDEX_COURSES_CONTAINER_BTN_XPATH).click()
    self.driver.find_element_by_xpath(INDEX_LECTURERS_CONTAINER_BTN_XPATH).click()
    self.driver.find_element_by_xpath(INDEX_STUDENTS_CONTAINER_BTN_XPATH).click()
    self.driver.find_element_by_xpath(INDEX_LECTURES_CONTAINER_BTN_XPATH).click()


def open_containers_module_course_settings(self):
    self.driver.find_element_by_xpath(INDEX_MODULES_CONTAINER_BTN_XPATH).click()
    self.driver.find_element_by_xpath(INDEX_COURSES_CONTAINER_BTN_XPATH).click()


def go_to_module(self, module_code):
    table = self.driver.find_element_by_id(INDEX_MODULES_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + module_code + "']").click()


def go_to_course(self, course_code):
    table = self.driver.find_element_by_id(INDEX_COURSES_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + course_code + "']").click()


def go_to_lecturer(self, staff_code):
    table = self.driver.find_element_by_id(INDEX_LECTURERS_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + staff_code + "']").click()


def go_to_student(self, student_code):
    table = self.driver.find_element_by_id(INDEX_STUDENTS_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + student_code + "']").click()


def go_to_lecture(self, session_id):
    table = self.driver.find_element_by_id(INDEX_LECTURES_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + session_id + "']").click()


def go_to_index(self):
    self.driver.find_element_by_xpath(HOME_BUTTON_XPATH).click()


def go_to_settings(self):
    self.driver.find_element_by_id(USER_DROPDOWN_ID).click()
    self.driver.find_element_by_xpath(".//a[contains(text(), 'Settings')]").click()


def go_to_logout(self):
    user_dropdown = self.driver.find_element_by_id(USER_DROPDOWN_ID)
    self.driver.execute_script("return arguments[0].scrollIntoView(true);", user_dropdown)
    user_dropdown.click()
    self.driver.find_element_by_xpath(".//a[contains(text(), 'Log out')]").click()
