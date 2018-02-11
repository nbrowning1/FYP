from django.test import TestCase
from tool.forms.forms import *


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
        self.assertEquals(form.errors['feedback_other'], ['Ensure this value has at most 1000 characters (it has 1001).'])