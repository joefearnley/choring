from django.core.management.base import BaseCommand
import re

from choring.chores.models import Chore


class Command(BaseCommand):
    help = "Strip trailing ' (due YYYY-MM-DD)' from chore titles"

    def handle(self, *args, **options):
        pattern = re.compile(r"\s*\(due \d{4}-\d{2}-\d{2}\)$")
        changed = 0
        for c in Chore.objects.all():
            if c.title and pattern.search(c.title):
                new_title = pattern.sub('', c.title)
                self.stdout.write(f"Updating Chore {c.pk}: '{c.title}' -> '{new_title}'")
                c.title = new_title
                c.save(update_fields=['title'])
                changed += 1
        self.stdout.write(self.style.SUCCESS(f"Done. Updated {changed} chore title(s)."))
