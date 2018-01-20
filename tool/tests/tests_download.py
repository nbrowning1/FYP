import os

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from ..models import Student, Staff


class DownloadTests(TestCase):
    def test_download(self):
        authenticate_admin(self)
        response = test_download(self)

        self.assertEquals(response.get('Content-Disposition'), "inline; filename=upload_example.csv")

    def test_download_nonexistent_file(self):
        authenticate_admin(self)
        response = self.client.get(reverse('tool:download', kwargs={'path': 'no-exist'}), follow=True)
        self.assertEquals(response.status_code, 404)

    def test_download_usertype_permissions(self):
        # student - forbidden
        authenticate_student(self)
        self.assertEquals(test_download(self).status_code, 403)

        # staff - forbidden
        authenticate_staff(self)
        self.assertEquals(test_download(self).status_code, 403)

        # admin is the only allowed user type - should be the only one to successfully download
        authenticate_admin(self)
        self.assertEquals(test_download(self).status_code, 200)

    def test_unauthenticated_upload(self):
        response = test_download(self)
        self.assertContains(response, "Please login to see this page.")


def test_download(self):
    path = os.path.join(os.path.dirname(__file__), '..', 'download_resources', 'upload_example.csv')
    return self.client.get(reverse('tool:download', kwargs={'path': path}), follow=True)


def authenticate_admin(self):
    user = User.objects.create_superuser(username='test', password='12345', email='test@mail.com')
    self.client.login(username='test', password='12345')
    return user


def authenticate_student(self):
    user = create_student('teststudent', 'test').user
    self.client.login(username='teststudent', password='12345')
    return user


def authenticate_staff(self):
    user = create_staff('teststaff').user
    self.client.login(username='teststaff', password='12345')
    return user


def create_student(username, device_id):
    user = User.objects.create_user(username=username, password='12345')
    student = Student(user=user, device_id=device_id)
    student.save()
    return student


def create_staff(username):
    user = User.objects.create_user(username=username, password='12345')
    staff = Staff(user=user)
    staff.save()
    return staff
