import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Production log rotation and maintenance tasks."

    LOG_FILES = (
        "django.log",
        "error.log",
        "security.log",
        "stderr.log",
    )

    ROTATE_SIZE_BYTES = 1 * 1024 * 1024
    RETENTION_DAYS = 30

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned operations without changing files.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        project_root = Path(settings.BASE_DIR)
        logs_dir = project_root / "logs"
        archive_dir = (
            project_root.parent
            / "production-backups"
            / "hikayemtaki"
            / "logs"
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Production maintenance started. dry_run={dry_run}"
            )
        )

        if not logs_dir.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Log directory not found: {logs_dir}"
                )
            )
            return

        if not dry_run:
            archive_dir.mkdir(parents=True, exist_ok=True)
            archive_dir.chmod(0o700)

        self._rotate_logs(
            project_root=project_root,
            logs_dir=logs_dir,
            archive_dir=archive_dir,
            dry_run=dry_run,
        )

        self._delete_expired_archives(
            archive_dir=archive_dir,
            dry_run=dry_run,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Production maintenance completed."
            )
        )

    def _rotate_logs(
        self,
        project_root,
        logs_dir,
        archive_dir,
        dry_run,
    ):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        for filename in self.LOG_FILES:
            if filename == "stderr.log":
                log_path = project_root / filename
            else:
                log_path = logs_dir / filename

            if not log_path.exists():
                self.stdout.write(
                    f"SKIP missing: {log_path}"
                )
                continue

            size = log_path.stat().st_size

            if size < self.ROTATE_SIZE_BYTES:
                self.stdout.write(
                    f"SKIP size={size} bytes: {log_path}"
                )
                continue

            archive_name = (
                f"{log_path.stem}-{timestamp}{log_path.suffix}.gz"
            )
            archive_path = archive_dir / archive_name

            self.stdout.write(
                f"ROTATE {log_path} -> {archive_path}"
            )

            if dry_run:
                continue

            with log_path.open("rb") as source:
                with gzip.open(archive_path, "wb") as target:
                    shutil.copyfileobj(source, target)

            archive_path.chmod(0o600)

            with log_path.open("w", encoding="utf-8"):
                pass

            log_path.chmod(0o640)

    def _delete_expired_archives(
        self,
        archive_dir,
        dry_run,
    ):
        if not archive_dir.exists():
            self.stdout.write(
                f"SKIP archive directory missing: {archive_dir}"
            )
            return

        cutoff = datetime.now() - timedelta(
            days=self.RETENTION_DAYS
        )

        for archive_path in archive_dir.glob("*.gz"):
            modified_at = datetime.fromtimestamp(
                archive_path.stat().st_mtime
            )

            if modified_at >= cutoff:
                continue

            self.stdout.write(
                f"DELETE expired archive: {archive_path}"
            )

            if not dry_run:
                archive_path.unlink()
