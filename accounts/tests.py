from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsTests(TestCase):
    def test_register_and_login(self):
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'alice',
            'email': 'alice@example.com',
            'password1': 'complexpassword123',
            'password2': 'complexpassword123',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username='alice').exists())
