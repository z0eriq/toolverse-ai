from django.core.management.base import BaseCommand

from apps.common.tasks import run_database_backup


class Command(BaseCommand):
    help = "Create a database backup (pg_dump or sqlite copy) when BACKUP_ENABLED=true"

    def handle(self, *args, **options):
        result = run_database_backup()
        status = result.get("status")
        if status == "ok":
            self.stdout.write(self.style.SUCCESS(f"Backup written: {result.get('path')}"))
        elif status == "skipped":
            self.stdout.write(self.style.WARNING(f"Skipped: {result.get('reason')}"))
        else:
            self.stderr.write(self.style.ERROR(str(result)))
