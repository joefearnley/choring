from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Chore, ChoreOccurrence
from datetime import date, timedelta


class GenerateOccurrencesAdminTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.super = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass')
        self.client = Client()
        self.client.force_login(self.super)

        # create a simple weekly chore starting today
        self.chore_weekly = Chore.objects.create(
            title='Weekly Clean',
            start_date=date.today(),
            recurrence=Chore.RECURRENCE_WEEKLY,
            active=True,
        )

        # create a non-recurring chore due in two days
        self.chore_once = Chore.objects.create(
            title='One-off',
            due_date=date.today() + timedelta(days=2),
            recurrence=Chore.RECURRENCE_NONE,
            active=True,
        )

    def test_generate_occurrences_for_range(self):
        start = date.today()
        end = date.today() + timedelta(days=21)
        ids = f"{self.chore_weekly.pk},{self.chore_once.pk}"
        url = f"/admin/chores/chore/generate-occurrences/"

        # GET form
        r = self.client.get(url, {'ids': ids})
        self.assertEqual(r.status_code, 200)

        # POST to generate
        r = self.client.post(url, {'ids': ids, 'start_date': start.isoformat(), 'end_date': end.isoformat()})
        self.assertEqual(r.status_code, 302)  # redirect

        # Weekly chore should have occurrences roughly 4 (0,7,14,21)
        occ_weekly = ChoreOccurrence.objects.filter(chore=self.chore_weekly).count()
        self.assertGreaterEqual(occ_weekly, 3)

        # One-off chore should have 1 occurrence
        occ_once = ChoreOccurrence.objects.filter(chore=self.chore_once).count()
        self.assertEqual(occ_once, 1)


# Create your tests here.
