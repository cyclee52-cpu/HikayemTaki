import hashlib
import os
import tarfile
import tempfile
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Create, verify and retain production media backups. "
        "A new archive is skipped when media content has not changed."
    )

    RETENTION_DAYS = 28
    HASH_CHUNK_SIZE = 1024 * 1024
    ARCHIVE_PREFIX = "media-"
    ARCHIVE_SUFFIX = ".tar.gz"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show planned operations without creating or deleting files.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        media_root = Path(settings.MEDIA_ROOT).resolve()
        backup_dir = (
            Path(settings.BASE_DIR).parent
            / "production-backups"
            / "hikayemtaki"
            / "media"
        ).resolve()

        self.stdout.write(
            self.style.NOTICE(
                f"Production media backup started. dry_run={dry_run}"
            )
        )
        self.stdout.write(f"Media root: {media_root}")
        self.stdout.write(f"Backup directory: {backup_dir}")

        self._validate_paths(
            media_root=media_root,
            backup_dir=backup_dir,
        )

        current_manifest_hash, file_count, total_size = (
            self._calculate_media_manifest(media_root)
        )

        self.stdout.write(f"Media files: {file_count}")
        self.stdout.write(f"Media bytes: {total_size}")
        self.stdout.write(
            f"Media manifest SHA256: {current_manifest_hash}"
        )

        latest_manifest_hash = self._read_latest_manifest_hash(
            backup_dir=backup_dir,
        )

        if (
            latest_manifest_hash
            and latest_manifest_hash == current_manifest_hash
        ):
            self.stdout.write(
                self.style.WARNING(
                    "SKIP media content has not changed since "
                    "the latest successful backup."
                )
            )

            self._delete_expired_backups(
                backup_dir=backup_dir,
                dry_run=dry_run,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Production media backup completed without "
                    "creating a duplicate archive."
                )
            )
            return

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        archive_name = (
            f"{self.ARCHIVE_PREFIX}{timestamp}{self.ARCHIVE_SUFFIX}"
        )
        archive_path = backup_dir / archive_name
        checksum_path = backup_dir / f"{archive_name}.sha256"
        manifest_path = backup_dir / f"{archive_name}.manifest.sha256"

        self.stdout.write(f"Archive: {archive_path}")
        self.stdout.write(f"Checksum: {checksum_path}")
        self.stdout.write(f"Manifest: {manifest_path}")

        if dry_run:
            self.stdout.write(
                "CREATE media archive and verification files"
            )
            self._delete_expired_backups(
                backup_dir=backup_dir,
                dry_run=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Production media backup dry-run completed."
                )
            )
            return

        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_dir.chmod(0o700)

        temporary_archive_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                prefix=".media-backup-",
                suffix=".tar.gz.tmp",
                dir=backup_dir,
                delete=False,
            ) as temporary_file:
                temporary_archive_path = Path(
                    temporary_file.name
                )

            self._create_archive(
                media_root=media_root,
                archive_path=temporary_archive_path,
            )

            temporary_archive_path.chmod(0o600)

            self._verify_archive(
                archive_path=temporary_archive_path,
                expected_manifest_hash=current_manifest_hash,
                expected_file_count=file_count,
                expected_total_size=total_size,
            )

            os.replace(
                temporary_archive_path,
                archive_path,
            )
            temporary_archive_path = None

            archive_path.chmod(0o600)

            archive_checksum = self._sha256_file(archive_path)

            checksum_path.write_text(
                f"{archive_checksum}  {archive_path.name}\n",
                encoding="utf-8",
            )
            checksum_path.chmod(0o600)

            manifest_path.write_text(
                f"{current_manifest_hash}  media-content\n",
                encoding="utf-8",
            )
            manifest_path.chmod(0o600)

            self._verify_written_checksum(
                archive_path=archive_path,
                checksum_path=checksum_path,
            )

            self._delete_expired_backups(
                backup_dir=backup_dir,
                dry_run=False,
            )

        except Exception:
            if (
                temporary_archive_path is not None
                and temporary_archive_path.exists()
            ):
                temporary_archive_path.unlink()

            for incomplete_path in (
                archive_path,
                checksum_path,
                manifest_path,
            ):
                if incomplete_path.exists():
                    incomplete_path.unlink()

            raise

        self.stdout.write(
            f"Archive SHA256: {archive_checksum}"
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Production media backup completed."
            )
        )

    def _validate_paths(
        self,
        media_root,
        backup_dir,
    ):
        if not media_root.exists():
            raise CommandError(
                f"Media directory not found: {media_root}"
            )

        if not media_root.is_dir():
            raise CommandError(
                f"Media path is not a directory: {media_root}"
            )

        if media_root == backup_dir:
            raise CommandError(
                "Media directory and backup directory cannot be "
                "the same."
            )

        if self._is_relative_to(
            backup_dir,
            media_root,
        ):
            raise CommandError(
                "Backup directory cannot be located inside the "
                "live media directory."
            )

        if self._is_relative_to(
            media_root,
            backup_dir,
        ):
            raise CommandError(
                "Live media directory cannot be located inside "
                "the backup directory."
            )

    def _calculate_media_manifest(
        self,
        media_root,
    ):
        digest = hashlib.sha256()
        file_count = 0
        total_size = 0

        for file_path in self._iter_media_files(media_root):
            relative_path = file_path.relative_to(
                media_root
            ).as_posix()

            file_size = file_path.stat().st_size
            file_hash = self._sha256_file(file_path)

            manifest_line = (
                f"{file_hash}\0{file_size}\0{relative_path}\n"
            )

            digest.update(
                manifest_line.encode(
                    "utf-8",
                    errors="surrogateescape",
                )
            )

            file_count += 1
            total_size += file_size

        return digest.hexdigest(), file_count, total_size

    def _iter_media_files(
        self,
        media_root,
    ):
        files = []

        for path in media_root.rglob("*"):
            if path.is_symlink():
                raise CommandError(
                    f"Symbolic links are not allowed in media: {path}"
                )

            if path.is_file():
                files.append(path)

        return sorted(
            files,
            key=lambda path: path.relative_to(
                media_root
            ).as_posix(),
        )

    def _create_archive(
        self,
        media_root,
        archive_path,
    ):
        with tarfile.open(
            archive_path,
            mode="w:gz",
            format=tarfile.PAX_FORMAT,
        ) as archive:
            for file_path in self._iter_media_files(media_root):
                relative_path = file_path.relative_to(
                    media_root
                )

                archive_name = (
                    PurePosixPath("media")
                    / PurePosixPath(relative_path.as_posix())
                )

                archive.add(
                    file_path,
                    arcname=str(archive_name),
                    recursive=False,
                )

    def _verify_archive(
        self,
        archive_path,
        expected_manifest_hash,
        expected_file_count,
        expected_total_size,
    ):
        digest = hashlib.sha256()
        archive_file_count = 0
        archive_total_size = 0

        try:
            with tarfile.open(
                archive_path,
                mode="r:gz",
            ) as archive:
                members = sorted(
                    archive.getmembers(),
                    key=lambda member: member.name,
                )

                for member in members:
                    self._validate_archive_member(member)

                    if not member.isfile():
                        continue

                    extracted_file = archive.extractfile(member)

                    if extracted_file is None:
                        raise CommandError(
                            f"Archive member could not be read: "
                            f"{member.name}"
                        )

                    file_digest = hashlib.sha256()

                    for chunk in iter(
                        lambda: extracted_file.read(
                            self.HASH_CHUNK_SIZE
                        ),
                        b"",
                    ):
                        file_digest.update(chunk)

                    relative_path = PurePosixPath(
                        member.name
                    ).relative_to("media").as_posix()

                    manifest_line = (
                        f"{file_digest.hexdigest()}"
                        f"\0{member.size}"
                        f"\0{relative_path}\n"
                    )

                    digest.update(
                        manifest_line.encode(
                            "utf-8",
                            errors="surrogateescape",
                        )
                    )

                    archive_file_count += 1
                    archive_total_size += member.size

        except (tarfile.TarError, OSError) as error:
            raise CommandError(
                f"Media archive verification failed: {error}"
            ) from error

        archive_manifest_hash = digest.hexdigest()

        if archive_file_count != expected_file_count:
            raise CommandError(
                "Media archive file count mismatch: "
                f"expected={expected_file_count}, "
                f"actual={archive_file_count}"
            )

        if archive_total_size != expected_total_size:
            raise CommandError(
                "Media archive size mismatch: "
                f"expected={expected_total_size}, "
                f"actual={archive_total_size}"
            )

        if archive_manifest_hash != expected_manifest_hash:
            raise CommandError(
                "Media archive manifest mismatch: "
                f"expected={expected_manifest_hash}, "
                f"actual={archive_manifest_hash}"
            )

        self.stdout.write(
            "Media archive verification: ok"
        )

    def _validate_archive_member(
        self,
        member,
    ):
        member_path = PurePosixPath(member.name)

        if member_path.is_absolute():
            raise CommandError(
                f"Unsafe absolute archive path: {member.name}"
            )

        if ".." in member_path.parts:
            raise CommandError(
                f"Unsafe parent traversal in archive: {member.name}"
            )

        if not member_path.parts:
            raise CommandError(
                "Archive contains an empty path."
            )

        if member_path.parts[0] != "media":
            raise CommandError(
                f"Unexpected archive root: {member.name}"
            )

        if (
            member.issym()
            or member.islnk()
            or member.isdev()
            or member.isfifo()
        ):
            raise CommandError(
                f"Unsafe archive member type: {member.name}"
            )

    def _read_latest_manifest_hash(
        self,
        backup_dir,
    ):
        if not backup_dir.exists():
            return None

        manifest_paths = sorted(
            backup_dir.glob(
                f"{self.ARCHIVE_PREFIX}*"
                f"{self.ARCHIVE_SUFFIX}.manifest.sha256"
            ),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

        for manifest_path in manifest_paths:
            archive_name = manifest_path.name.removesuffix(
                ".manifest.sha256"
            )
            archive_path = backup_dir / archive_name
            checksum_path = backup_dir / f"{archive_name}.sha256"

            if not archive_path.is_file():
                continue

            if not checksum_path.is_file():
                continue

            try:
                manifest_line = manifest_path.read_text(
                    encoding="utf-8"
                ).strip()
            except OSError:
                continue

            if not manifest_line:
                continue

            manifest_hash = manifest_line.split()[0]

            if (
                len(manifest_hash) == 64
                and all(
                    character in "0123456789abcdef"
                    for character in manifest_hash.lower()
                )
            ):
                return manifest_hash.lower()

        return None

    def _verify_written_checksum(
        self,
        archive_path,
        checksum_path,
    ):
        checksum_line = checksum_path.read_text(
            encoding="utf-8"
        ).strip()

        if not checksum_line:
            raise CommandError(
                f"Checksum file is empty: {checksum_path}"
            )

        expected_checksum = checksum_line.split()[0]
        actual_checksum = self._sha256_file(archive_path)

        if expected_checksum != actual_checksum:
            raise CommandError(
                "Written archive checksum verification failed: "
                f"expected={expected_checksum}, "
                f"actual={actual_checksum}"
            )

        self.stdout.write(
            "Media archive SHA256 verification: ok"
        )

    def _sha256_file(
        self,
        file_path,
    ):
        digest = hashlib.sha256()

        with file_path.open("rb") as file_handle:
            for chunk in iter(
                lambda: file_handle.read(
                    self.HASH_CHUNK_SIZE
                ),
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

        for archive_path in sorted(
            backup_dir.glob(
                f"{self.ARCHIVE_PREFIX}*{self.ARCHIVE_SUFFIX}"
            )
        ):
            modified_at = datetime.fromtimestamp(
                archive_path.stat().st_mtime
            )

            if modified_at >= cutoff:
                continue

            related_paths = (
                archive_path,
                backup_dir / f"{archive_path.name}.sha256",
                backup_dir
                / f"{archive_path.name}.manifest.sha256",
            )

            for related_path in related_paths:
                if not related_path.exists():
                    continue

                self.stdout.write(
                    f"DELETE expired media backup file: "
                    f"{related_path}"
                )

                if not dry_run:
                    related_path.unlink()

    def _is_relative_to(
        self,
        child_path,
        parent_path,
    ):
        try:
            child_path.relative_to(parent_path)
            return True
        except ValueError:
            return False
