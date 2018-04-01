from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.wait import WebDriverWait
import time

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
INDEX_LECTURES_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Lectures')
ATTENDANCE_CONTAINER_BTN_XPATH = CONTAINER_BUTTON_XPATH.format('Attendance')
INDEX_MODULES_CONTAINER_ID = 'modules-container'
INDEX_LECTURES_CONTAINER_ID = 'lectures-container'
INDEX_CONTAINER_TABLE_ROWS_XPATH = ".//*[@id='{}']//tbody//tr"
INDEX_MODULES_TABLE_ROWS_XPATH = INDEX_CONTAINER_TABLE_ROWS_XPATH.format('modules-tbl')
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


class AutomationTests(StaticLiveServerTestCase):
    driver = None
    waiter = None

    """
    test_app_staff
        - login
        - validate index
        - check each single entity view
        - upload
        - validate settings
        - create entities
        - logout

    test_auth
        - wrong password
        - password reset
        - login
        - change password
        - logout
        - login new password
    """

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

        test_login(self)
        soft_failures.append(test_index_page_student(self))
        go_to_module(self, 'COM101')
        soft_failures.append(test_module_view_attendance(self, 'COM101'))
        self.driver.find_element_by_xpath(FEEDBACK_TAB_XPATH).click()
        soft_failures.append(test_module_view_feedback(self))
        go_to_index(self)
        open_containers_student(self)
        go_to_lecture(self, 'mod1 lec1')
        soft_failures.append(test_lecture_view(self, 'Dec. 1, 2017 - mod1 lec1'))
        go_to_settings(self)
        soft_failures.append(test_settings(self))
        # logout
        logout(self)
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
    module_1 = TestUtils.create_module('COM101', 'COM101-crn')
    module_2 = TestUtils.create_module('COM999', 'COM999-crn')
    module_3 = TestUtils.create_module('EEE101', 'EEE101-crn')
    module_1_lecture_1 = TestUtils.create_lecture(module_1, 'mod1 lec1')
    module_1_lecture_2 = TestUtils.create_lecture(module_1, 'mod1 lec2')
    module_2_lecture_1 = TestUtils.create_lecture(module_2, 'mod2 lec1')

    module_1.students.add(student)
    module_2.students.add(student)

    # add student attendance
    TestUtils.create_attendance(student, module_1_lecture_1, False)
    TestUtils.create_attendance(student, module_1_lecture_2, True)
    TestUtils.create_attendance(student, module_2_lecture_1, True)


def test_login(self):
    try:
        # hit the app
        self.driver.get(self.live_server_url + '/tool')
        # handle login page
        self.driver.find_element_by_id(LOGIN_USERNAME_ID).send_keys(STUDENT_USERNAME)
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


def test_module_view_feedback(self):
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


def go_to_module(self, module_code):
    table = self.driver.find_element_by_id(INDEX_MODULES_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + module_code + "']").click()


def go_to_lecture(self, session_id):
    table = self.driver.find_element_by_id(INDEX_LECTURES_CONTAINER_ID)
    table.find_element_by_xpath(".//a[text()='" + session_id + "']").click()


def go_to_index(self):
    self.driver.find_element_by_xpath(HOME_BUTTON_XPATH).click()


def go_to_settings(self):
    self.driver.find_element_by_id(USER_DROPDOWN_ID).click()
    self.driver.find_element_by_xpath(".//a[contains(text(), 'Settings')]").click()


def go_to_logout(self):
    self.driver.find_element_by_id(USER_DROPDOWN_ID).click()
    self.driver.find_element_by_xpath(".//a[contains(text(), 'Log out')]").click()
