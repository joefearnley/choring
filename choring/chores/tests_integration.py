from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import Chore


class IntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='intuser', email='int@example.com', password='pass')

        self.weekly = Chore.objects.create(
            title='Integration Weekly',
            start_date=date.today(),
            recurrence=Chore.RECURRENCE_WEEKLY,
            active=True,
            assigned_to=self.user,
        )
        self.once = Chore.objects.create(
            title='Integration One-off',
            due_date=date.today(),
            recurrence=Chore.RECURRENCE_NONE,
            active=True,
        )

    def test_root_serves_spa_and_app_removed(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Choring — This Week')

        r2 = self.client.get('/app/')
        self.assertEqual(r2.status_code, 404)

    def test_api_chores_week(self):
        r = self.client.get('/api/chores/week/')
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIsInstance(data, list)
        titles = {d['title'] for d in data}
        self.assertTrue('Integration Weekly' in titles or 'Integration One-off' in titles)
