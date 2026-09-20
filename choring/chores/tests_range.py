from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta

from .models import Chore


class ChoresRangeAPITest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='ruser', email='r@example.com', password='pass')

        today = date.today()

        # overdue single-occurrence chore
        self.overdue = Chore.objects.create(
            title='Overdue Task',
            due_date=today - timedelta(days=3),
            recurrence=Chore.RECURRENCE_NONE,
            active=True,
            assigned_to=self.user,
        )

        # weekly recurring chore started two weeks ago
        self.weekly = Chore.objects.create(
            title='Weekly Task',
            start_date=today - timedelta(days=14),
            recurrence=Chore.RECURRENCE_WEEKLY,
            active=True,
            assigned_to=self.user,
        )

    def test_range_api_returns_expected_occurrences(self):
        # default range is today-28 .. today+28
        resp = self.client.get('/api/chores/range/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsInstance(data, list)

        # find the overdue occurrence
        overdue_iso = (date.today() - timedelta(days=3)).isoformat()
        found_overdue = any(item['title'] == self.overdue.title and item['date'] == overdue_iso for item in data)
        self.assertTrue(found_overdue, 'Overdue occurrence not present in range results')

        # compute expected weekly occurrences between defaults
        start = date.today() - timedelta(days=28)
        end = date.today() + timedelta(days=28)
        expected_dates = []
        base = self.weekly.start_date
        current = base
        while current < start:
            current = current + timedelta(days=7)
        while current <= end:
            expected_dates.append(current.isoformat())
            current = current + timedelta(days=7)

        # assert each expected weekly occurrence is present
        for d in expected_dates:
            found = any(item['title'] == self.weekly.title and item['date'] == d for item in data)
            self.assertTrue(found, f'Expected weekly occurrence on {d} not found')

    def test_complete_occurrence_marks_completed(self):
        # pick one weekly occurrence date
        start = date.today() - timedelta(days=28)
        end = date.today() + timedelta(days=28)
        # compute first upcoming occurrence
        base = self.weekly.start_date
        current = base
        while current < start:
            current = current + timedelta(days=7)
        target = current

        # complete it via API
        resp = self.client.post('/api/chores/complete/', {'chore_id': self.weekly.pk, 'date': target.isoformat()})
        self.assertEqual(resp.status_code, 200)

        # ensure range API no longer returns completed occurrence
        resp2 = self.client.get('/api/chores/range/')
        self.assertEqual(resp2.status_code, 200)
        data2 = resp2.json()
        found = any(item['title'] == self.weekly.title and item['date'] == target.isoformat() for item in data2)
        self.assertFalse(found, 'Completed occurrence should not be returned in range API')

    def test_recurrence_normalization_in_api(self):
        """Ensure chores with recurrence 'none' are returned as empty string, others preserved."""
        resp = self.client.get('/api/chores/range/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        # overdue (one-off) chore should have recurrence as empty string
        overdue_iso = (date.today() - timedelta(days=3)).isoformat()
        overdue_item = next((it for it in data if it['title'] == self.overdue.title and it['date'] == overdue_iso), None)
        self.assertIsNotNone(overdue_item, 'Overdue occurrence not present')
        self.assertEqual(overdue_item.get('recurrence', None), '')

        # weekly occurrences should preserve 'weekly'
        weekly_item = next((it for it in data if it['title'] == self.weekly.title), None)
        self.assertIsNotNone(weekly_item, 'Weekly occurrence not present')
        self.assertEqual(weekly_item.get('recurrence', None), self.weekly.recurrence)
