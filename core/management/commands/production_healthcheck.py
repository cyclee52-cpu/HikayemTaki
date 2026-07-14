import os
import platform
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Run a read-only production health check."

    DATABASE_BACKUP_MAX_AGE_HOURS = 36
    MEDIA_BACKUP_MAX_AGE_HOURS = 192
    DISK_WARNING_PERCENT = 80
    DISK_CRITICAL_PERCENT = 90

    def handle(self, *args, **options):
        self.results = []

        project_root = Path(settings.BASE_DIR).resolve()
        media_root = Path(settings.MEDIA_ROOT).resolve()
        logs_dir = project_root / "logs"
        backup_root = (
            project_root.parent
            / "production-backups"
            / "hikayemtaki"
        )

        database_path = Path(
            settings.DATABASES["default"]["NAME"]
        ).resolve()

        database_backup_dir = backup_root / "database"
        media_backup_dir = backup_root / "media"

        self.stdout.write("=" * 52)
        self.stdout.write("Hikayem Takı Production Health Check")
        self.stdout.write("=" * 52)

        self._check_environment()
        self._check_django_database()
        self._check_sqlite_integrity(database_path)
        self._check_media(media_root)
        self._check_logs(logs_dir)
        self._check_database_backup(database_backup_dir)
        self._check_media_backup(media_backup_dir)
        self._check_disk(project_root)
        self._check_permissions(
            project_root=project_root,
            media_root=media_root,
            logs_dir=logs_dir,
            database_path=database_path,
            backup_root=backup_root,
        )

        self._print_summary()

    def _record(self, name, status, detail):
        self.results.append(
            {
                "name": name,
                "status": status,
                "detail": detail,
            }
        )

        label = {
            "OK": self.style.SUCCESS("OK"),
            "WARNING": self.style.WARNING("WARNING"),
            "CRITICAL": self.style.ERROR("CRITICAL"),
        }[status]

        self.stdout.write(
            f"{name:<24} {label:<12} {detail}"
        )

    def _check_environment(self):
        if settings.DEBUG:
            self._record(
                "Environment",
                "CRITICAL",
                "DEBUG=True",
            )
            return

        allowed_hosts = set(settings.ALLOWED_HOSTS)

        required_hosts = {
            "hikayemtaki.com",
            "www.hikayemtaki.com",
        }

        missing_hosts = sorted(
            required_hosts - allowed_hosts
        )

        if missing_hosts:
            self._record(
                "Environment",
                "WARNING",
                f"Missing ALLOWED_HOSTS: {missing_hosts}",
            )
            return

        self._record(
            "Environment",
            "OK",
            (
                f"DEBUG=False, Python={platform.python_version()}, "
                f"Django settings loaded"
            ),
        )

    def _check_django_database(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

            if result != (1,):
                self._record(
                    "Database connection",
                    "CRITICAL",
                    f"Unexpected result: {result}",
                )
                return

            self._record(
                "Database connection",
                "OK",
                "Django database query successful",
            )

        except Exception as error:
            self._record(
                "Database connection",
                "CRITICAL",
                str(error),
            )

    def _check_sqlite_integrity(self, database_path):
        if not database_path.is_file():
            self._record(
                "SQLite integrity",
                "CRITICAL",
                f"Database missing: {database_path}",
            )
            return

        try:
            connection_handle = sqlite3.connect(
                f"file:{database_path}?mode=ro",
                uri=True,
            )

            try:
                result = connection_handle.execute(
                    "PRAGMA quick_check;"
                ).fetchone()
            finally:
                connection_handle.close()

            if not result or result[0] != "ok":
                self._record(
                    "SQLite integrity",
                    "CRITICAL",
                    f"quick_check={result}",
                )
                return

            self._record(
                "SQLite integrity",
                "OK",
                (
                    f"quick_check=ok, "
                    f"size={database_path.stat().st_size} bytes"
                ),
            )

        except Exception as error:
            self._record(
                "SQLite integrity",
                "CRITICAL",
                str(error),
            )

    def _check_media(self, media_root):
        if not media_root.is_dir():
            self._record(
                "Media",
                "CRITICAL",
                f"Directory missing: {media_root}",
            )
            return

        file_count = 0
        total_size = 0
        symlink_count = 0

        try:
            for path in media_root.rglob("*"):
                if path.is_symlink():
                    symlink_count += 1
                    continue

                if path.is_file():
                    file_count += 1
                    total_size += path.stat().st_size

        except OSError as error:
            self._record(
                "Media",
                "CRITICAL",
                str(error),
            )
            return

        if symlink_count:
            self._record(
                "Media",
                "WARNING",
                (
                    f"files={file_count}, bytes={total_size}, "
                    f"symlinks={symlink_count}"
                ),
            )
            return

        self._record(
            "Media",
            "OK",
            f"files={file_count}, bytes={total_size}",
        )

    def _check_logs(self, logs_dir):
        required_logs = (
            "django.log",
            "error.log",
            "security.log",
            "maintenance.log",
            "backup.log",
            "media-backup.log",
        )

        missing = []
        insecure = []

        for filename in required_logs:
            log_path = logs_dir / filename

            if not log_path.is_file():
                missing.append(filename)
                continue

            mode = log_path.stat().st_mode & 0o777

            if mode & 0o007:
                insecure.append(
                    f"{filename}:{mode:o}"
                )

        if missing:
            self._record(
                "Logs",
                "WARNING",
                f"Missing: {', '.join(missing)}",
            )
            return

        if insecure:
            self._record(
                "Logs",
                "WARNING",
                (
                    "World permissions detected: "
                    + ", ".join(insecure)
                ),
            )
            return

        self._record(
            "Logs",
            "OK",
            f"{len(required_logs)} required log files present",
        )

    def _check_database_backup(self, backup_dir):
        archive = self._latest_file(
            backup_dir,
            "db-*.sqlite3.gz",
        )

        if archive is None:
            self._record(
                "Database backup",
                "CRITICAL",
                "No database backup found",
            )
            return

        checksum_path = backup_dir / (
            f"{archive.name}.sha256"
        )

        if not checksum_path.is_file():
            self._record(
                "Database backup",
                "CRITICAL",
                f"Checksum missing: {checksum_path.name}",
            )
            return

        age_hours = self._age_hours(archive)

        if age_hours > self.DATABASE_BACKUP_MAX_AGE_HOURS:
            self._record(
                "Database backup",
                "WARNING",
                (
                    f"Latest backup age={age_hours:.1f}h, "
                    f"file={archive.name}"
                ),
            )
            return

        self._record(
            "Database backup",
            "OK",
            (
                f"age={age_hours:.1f}h, "
                f"size={archive.stat().st_size} bytes"
            ),
        )

    def _check_media_backup(self, backup_dir):
        archive = self._latest_file(
            backup_dir,
            "media-*.tar.gz",
        )

        if archive is None:
            self._record(
                "Media backup",
                "CRITICAL",
                "No media backup found",
            )
            return

        checksum_path = backup_dir / (
            f"{archive.name}.sha256"
        )
        manifest_path = backup_dir / (
            f"{archive.name}.manifest.sha256"
        )

        missing = []

        if not checksum_path.is_file():
            missing.append(checksum_path.name)

        if not manifest_path.is_file():
            missing.append(manifest_path.name)

        if missing:
            self._record(
                "Media backup",
                "CRITICAL",
                f"Missing verification files: {missing}",
            )
            return

        age_hours = self._age_hours(archive)

        if age_hours > self.MEDIA_BACKUP_MAX_AGE_HOURS:
            self._record(
                "Media backup",
                "WARNING",
                (
                    f"Latest backup age={age_hours:.1f}h, "
                    f"file={archive.name}"
                ),
            )
            return

        self._record(
            "Media backup",
            "OK",
            (
                f"age={age_hours:.1f}h, "
                f"size={archive.stat().st_size} bytes"
            ),
        )

    def _check_disk(self, project_root):
        usage = shutil.disk_usage(project_root)

        used_percent = (
            usage.used / usage.total
        ) * 100

        detail = (
            f"used={used_percent:.1f}%, "
            f"free={usage.free / (1024 ** 3):.1f} GiB"
        )

        if used_percent >= self.DISK_CRITICAL_PERCENT:
            self._record(
                "Disk",
                "CRITICAL",
                detail,
            )
            return

        if used_percent >= self.DISK_WARNING_PERCENT:
            self._record(
                "Disk",
                "WARNING",
                detail,
            )
            return

        self._record(
            "Disk",
            "OK",
            detail,
        )

    def _check_permissions(
        self,
        project_root,
        media_root,
        logs_dir,
        database_path,
        backup_root,
    ):
        problems = []

        expected_exact = {
            project_root: 0o755,
            database_path: 0o644,
            backup_root / "database": 0o700,
            backup_root / "media": 0o700,
        }

        for path, expected_mode in expected_exact.items():
            if not path.exists():
                problems.append(
                    f"missing:{path}"
                )
                continue

            actual_mode = path.stat().st_mode & 0o777

            if actual_mode != expected_mode:
                problems.append(
                    f"{path.name}:{actual_mode:o}"
                )

        if media_root.is_dir():
            for directory in (
                path
                for path in media_root.rglob("*")
                if path.is_dir()
            ):
                mode = directory.stat().st_mode & 0o777

                if mode != 0o775:
                    problems.append(
                        f"media-dir:{mode:o}:{directory}"
                    )

            root_mode = media_root.stat().st_mode & 0o777

            if root_mode != 0o775:
                problems.append(
                    f"media-root:{root_mode:o}"
                )

            for file_path in (
                path
                for path in media_root.rglob("*")
                if path.is_file()
            ):
                mode = file_path.stat().st_mode & 0o777

                if mode != 0o664:
                    problems.append(
                        f"media-file:{mode:o}:{file_path}"
                    )

        if logs_dir.is_dir():
            for file_path in (
                path
                for path in logs_dir.iterdir()
                if path.is_file()
            ):
                mode = file_path.stat().st_mode & 0o777

                if mode not in (0o600, 0o640):
                    problems.append(
                        f"log:{mode:o}:{file_path.name}"
                    )

        if problems:
            preview = "; ".join(problems[:5])

            if len(problems) > 5:
                preview += (
                    f"; and {len(problems) - 5} more"
                )

            self._record(
                "Permissions",
                "WARNING",
                preview,
            )
            return

        self._record(
            "Permissions",
            "OK",
            "Critical paths match expected modes",
        )

    def _latest_file(self, directory, pattern):
        if not directory.is_dir():
            return None

        files = [
            path
            for path in directory.glob(pattern)
            if path.is_file()
        ]

        if not files:
            return None

        return max(
            files,
            key=lambda path: path.stat().st_mtime,
        )

    def _age_hours(self, file_path):
        now = datetime.now().timestamp()
        modified_at = file_path.stat().st_mtime

        return (now - modified_at) / 3600

    def _print_summary(self):
        critical_count = sum(
            result["status"] == "CRITICAL"
            for result in self.results
        )

        warning_count = sum(
            result["status"] == "WARNING"
            for result in self.results
        )

        ok_count = sum(
            result["status"] == "OK"
            for result in self.results
        )

        self.stdout.write("")
        self.stdout.write("-" * 52)
        self.stdout.write(
            (
                f"OK={ok_count} "
                f"WARNING={warning_count} "
                f"CRITICAL={critical_count}"
            )
        )

        if critical_count:
            self.stdout.write(
                self.style.ERROR(
                    "Overall Status: CRITICAL"
                )
            )
            raise SystemExit(2)

        if warning_count:
            self.stdout.write(
                self.style.WARNING(
                    "Overall Status: WARNING"
                )
            )
            raise SystemExit(1)

        self.stdout.write(
            self.style.SUCCESS(
                "Overall Status: HEALTHY"
            )
        )
