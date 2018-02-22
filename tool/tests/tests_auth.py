from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse


class AuthTests(TestCase):
    def test_login_valid_credentials(self):
        User.objects.create_superuser('john', 'test@mail.com', 'johnpassword')
        test_login(self, 'john', 'johnpassword', True)

    def test_login_invalid_credentials(self):
        User.objects.create_superuser('john', 'test@mail.com', 'johnpassword')
        test_login(self, 'john', 'wrongpassword', False)

    def test_login_nonexistent_user(self):
        test_login(self, 'nouser', 'nopassword', False)

    def test_password_reset_recognised_email(self):
        User.objects.create_user('john', 'test@mail.com', 'johnpassword')
        test_password_reset(self, 'test@mail.com', True)

    def test_password_reset_unrecognised_email(self):
        User.objects.create_user('john', 'test@mail.com', 'johnpassword')
        test_password_reset(self, 'different@mail.com', False)


def test_login(self, username, password, success_expected):
    response = self.client.post(reverse('tool:login'), {'username': username, 'password': password})
    if success_expected:
        self.assertEqual(response.status_code, 302)
    else:
        self.assertEqual(response.status_code, 200)

    response = self.client.get(reverse('tool:index'))
    if success_expected:
        # should be able to see index now
        self.assertEqual(response.status_code, 200)
    else:
        # or be redirected to login
        self.assertEqual(response.status_code, 302)


def test_password_reset(self, email_address, email_expected):
    # post the response with our email address
    response = self.client.post(reverse('tool:password_reset'), {'email': email_address})
    self.assertEqual(response.status_code, 302)

    # check sent email
    if email_expected:
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Password reset on testserver')

        # get the token and userid from the response
        token = response.context[0]['token']
        uid = response.context[0]['uid']
        # Now we can use the token to get the password change form
        response = self.client.get(reverse('tool:password_reset_confirm', kwargs={'token': token, 'uidb64': uid}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['tool/auth/password_reset_confirm.html'])

        # post to the same url with our new password:
        response = self.client.post(reverse('tool:password_reset_confirm',
                                            kwargs={'token': token, 'uidb64': uid}),
                                    {'new_password1': 'pass', 'new_password2': 'pass'})
        self.assertEqual(response.status_code, 302)
    else:
        self.assertEqual(len(mail.outbox), 0)
