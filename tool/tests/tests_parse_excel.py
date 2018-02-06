import os
import types

from django.test import TestCase
from xlrd import open_workbook


class ExcelParserTests(TestCase):
    def test_parse_xls(self):
        rows = get_rows('Attendance_Test_xls.xls')
        for row in rows:
            attendance_vals_str = ",".join(row.attendance_vals)
            print("Device ID: " + row.device_id + ": " + attendance_vals_str)

    def test_parse_xlsx(self):
        rows = get_rows('Attendance_Test_xlsx.xlsx')
        for row in rows:
            attendance_vals_str = ",".join(row.attendance_vals)
            print("Device ID: " + row.device_id + ": " + attendance_vals_str)


def get_rows(filename):
    workbook = open_workbook(get_resource(filename))
    sheet = workbook.sheet_by_index(0)
    ret_val = []
    for row_index in range(sheet.nrows):
        row = types.SimpleNamespace()
        row.device_id = sheet.cell(row_index, 0).value
        row.attendance_vals = []
        for col_index in range(3, sheet.ncols):
            row.attendance_vals.append(sheet.cell(row_index, col_index).value)
        ret_val.append(row)
    return ret_val


def get_resource(filename):
    this_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(this_dir, 'resources', filename)
