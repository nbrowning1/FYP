import os

from django.test import TestCase
from django.urls import reverse

from .utils import *


class DownloadTests(TestCase):
    def test_download(self):
        TestUtils.authenticate_staff(self)
        response = test_download(self)

        self.assertEquals(response.get('Content-Disposition'), "inline; filename=upload_example.xlsx")

    def test_download_nonexistent_file(self):
        TestUtils.authenticate_staff(self)
        response = self.client.get(reverse('tool:download', kwargs={'path': 'no-exist'}), follow=True)
        self.assertEquals(response.status_code, 404)

    def test_download_usertype_permissions(self):
        # student - forbidden
        TestUtils.authenticate_student(self)
        self.assertEquals(test_download(self).status_code, 403)

        # staff is the only allowed user type - should be the only one to successfully download
        TestUtils.authenticate_staff(self)
        self.assertEquals(test_download(self).status_code, 200)

    def test_unauthenticated_upload(self):
        response = test_download(self)
        self.assertContains(response, "Please login to see this page.")


def test_download(self):
    path = os.path.join(os.path.dirname(__file__), '..', 'download_resources', 'upload_example.xlsx')
    return self.client.get(reverse('tool:download', kwargs={'path': path}), follow=True)
