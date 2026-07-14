import gzip
import hashlib
import shutil
import sqlite3
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create and retain production SQLite backups."

    RETENTION_DAYS = 14

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned operations without changing files.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        database_path = Path(
            settings.DATABASES["default"]["NAME"]
        ).resolve()

        backup_dir = (
            Path(settings.BASE_DIR).parent
            / "production-backups"
            / "hikayemtaki"
            / "database"
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Production database backup started. dry_run={dry_run}"
            )
        )

        if not database_path.exists():
            raise CommandError(
                f"Database file not found: {database_path}"
            )

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_name = f"db-{timestamp}.sqlite3.gz"
        backup_path = backup_dir / backup_name
        checksum_path = backup_dir / f"{backup_name}.sha256"

        self.stdout.write(
            f"Database: {database_path}"
        )
        self.stdout.write(
            f"Backup: {backup_path}"
        )

        if dry_run:
            self._delete_expired_backups(
                backup_dir=backup_dir,
                dry_run=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Production database backup dry-run completed."
                )
            )
            return

        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.chmod(0o700)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_database = Path(temp_dir) / "db.sqlite3"

            self._create_sqlite_backup(
                source_path=database_path,
                destination_path=temp_database,
            )

            self._verify_sqlite_backup(
                database_path=temp_database,
            )

            self._compress_backup(
                source_path=temp_database,
                destination_path=backup_path,
            )

        backup_path.chmod(0o600)

        checksum = self._sha256(backup_path)
        checksum_path.write_text(
            f"{checksum}  {backup_path.name}\n",
            encoding="utf-8",
        )
        checksum_path.chmod(0o600)

        self._delete_expired_backups(
            backup_dir=backup_dir,
            dry_run=False,
        )

        self.stdout.write(
            f"SHA256: {checksum}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Production database backup completed."
            )
        )

    def _create_sqlite_backup(
        self,
        source_path,
        destination_path,
    ):
        source = sqlite3.connect(
            f"file:{source_path}?mode=ro",
            uri=True,
        )
        destination = sqlite3.connect(destination_path)

        try:
            source.backup(destination)
        finally:
            destination.close()
            source.close()

    def _verify_sqlite_backup(
        self,
        database_path,
    ):
        connection = sqlite3.connect(
            f"file:{database_path}?mode=ro",
            uri=True,
        )

        try:
            result = connection.execute(
                "PRAGMA integrity_check;"
            ).fetchone()
        finally:
            connection.close()

        if not result or result[0] != "ok":
            raise CommandError(
                f"SQLite backup integrity check failed: {result}"
            )

        self.stdout.write(
            "SQLite backup integrity_check: ok"
        )

    def _compress_backup(
        self,
        source_path,
        destination_path,
    ):
        with source_path.open("rb") as source:
            with gzip.open(destination_path, "wb") as target:
                shutil.copyfileobj(source, target)

    def _sha256(self, file_path):
        digest = hashlib.sha256()

        with file_path.open("rb") as file_handle:
            for chunk in iter(
                lambda: file_handle.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    def _delete_expired_backups(
        self,
        backup_dir,
        dry_run,
    ):
        if not backup_dir.exists():
            self.stdout.write(
                f"SKIP backup directory missing: {backup_dir}"
            )
            return

        cutoff = datetime.now() - timedelta(
            days=self.RETENTION_DAYS
        )

        for backup_path in backup_dir.glob(
            "db-*.sqlite3.gz"
        ):
            modified_at = datetime.fromtimestamp(
                backup_path.stat().st_mtime
            )

            if modified_at >= cutoff:
                continue

            checksum_path = backup_dir / (
                f"{backup_path.name}.sha256"
            )

            self.stdout.write(
                f"DELETE expired backup: {backup_path}"
            )

            if dry_run:
                continue

            backup_path.unlink()

            if checksum_path.exists():
                checksum_path.unlink()
