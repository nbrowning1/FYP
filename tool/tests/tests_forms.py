from django.test import TestCase
from tool.forms.forms import *


class ModuleFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['module_code'], ['This field is required.'])
        self.assertEquals(form.errors['module_crn'], ['This field is required.'])

    def test_valid_form(self):
        data = {'module_code': 'COM101',
                'module_crn': 'COM101-crn'}
        form = ModuleForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_code(self):
        data = {'module_code': 'ABCDEF',
                'module_crn': 'module-crn'}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['module_code'], ['Must be a valid module code e.g. COM101'])

    def test_length_check(self):
        data = {'module_code': 'COM12000',
                'module_crn': '123456789012345678901234567890123456789012345678901'}
        form = ModuleForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 2)
        self.assertEquals(form.errors['module_code'],
                          ['Ensure this value has at most 7 characters (it has 8).'])
        self.assertEquals(form.errors['module_crn'],
                          ['Ensure this value has at most 50 characters (it has 51).'])


class ModuleFeedbackFormTests(TestCase):
    def test_empty_form(self):
        data = {}
        form = ModuleFeedbackForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)
        self.assertEquals(form.errors['feedback_general'], ['This field is required.'])
        self.assertEquals(form.errors['feedback_positive'], ['This field is required.'])
        self.assertEquals(form.errors['feedback_constructive'], ['This field is required.'])

    def test_valid_form(self):
        data = {'feedback_general': 'feedback',
                'feedback_positive': 'feedback',
                'feedback_constructive': 'feedback',
                'feedback_other': 'feedback'}
        form = ModuleFeedbackForm(data=data)
        self.assertTrue(form.is_valid())

    def test_length_check(self):
        data = {'feedback_general': 'feedback',
                'feedback_positive': 'feedback',
                'feedback_constructive': 'feedback',
                'feedback_other': 'askmntduadyulsllhsqtzgovbzfqsmtybchharlyvsnwgathszpxuizvjiadmdxuhnmjjzeqdbrromlxegxmpmugqerjscshooylkunskjahqakrgcsystepjrveasusiunxgxnidlzkaxdrstcxgwrfqrdzcjryedlosdlrnqaysoauzdotqukwibrdyueykxpwmbkotqsgiantktpphuubvtghzwrgzxuvhpyvbpknuiumflhdjnmgghegaucedwwzvdmnfswycpkcsobnubdogpmxvtnbryzdnlveurrxtdzlddyvkotxqspcbreouazzbiyqzbmktncgvzjnzzkzrzqlejluatnjgfrzctzistwvcubyfqzlqymuazhqpccuxkfafnwsyirqllywebmcmskpiiwhwgumunswlhhizirigshzwdbhocvurfokwvrtjvldnxsfjehmhqsdmdpridzqyofhzefmipghsndwwbzdhkeumnddmjdnfafbnazpktnbwzlkaqzeakcjlltjpwutbrgpjkdmzgbhijommeoledtkjqlfejqnutrqbbighujniiysauhffnpabucnxqkxhehiseyjdvgacsypvwgmudjdnmfandqjqkmmobmizxchjtscnfrtnxtpasnpdvuxxbdkpjpmwptuazdppvjjgteknhruwwwvsicvxfbofoxgrwtldkvuanqgpwvnaicdbkspoheahubzvcssfcsevsaqebgrukoxpdmiyhwdpxpnegyidnynlstbrezdnldbeypcrwlogzsmzmrwfshqamcfoicazjpixmmaejhsdopniwmtlghpysaswwauckzcshupjbglxivkerplfwffgdikpzxagbjdyvpmicwmfnkzwkmyflgclqqiaqrvxwlnjitgxxrxgdsaealtwvoyornbkfeepanbaiepibdldqhbhwqaftgcltsppsthmeugwomxfgyyataqA'}
        form = ModuleFeedbackForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)
        self.assertEquals(form.errors['feedback_other'],
                          ['Ensure this value has at most 1000 characters (it has 1001).'])
