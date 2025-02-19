from itertools import zip_longest
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import pytest

from zipmanip import rezip


@pytest.fixture(scope="session")
def zip_archive(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("sample") / "sample.zip"
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("file.txt", "content\n" * 234)
    return path


@pytest.fixture(scope="session")
def stored_archive(zip_archive: Path, tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("stored") / "stored.zip"
    rezip(zip_archive, path, compression=ZIP_STORED)
    return path


def test_stored_archive_larger(zip_archive: Path, stored_archive: Path) -> None:
    # sanity check
    assert zip_archive.stat().st_size < stored_archive.stat().st_size


@pytest.mark.parametrize(
    "attr",
    [
        "CRC",
        "create_system",
        "create_version",
        "date_time",
        "external_attr",
        "extra",
        "extract_version",
        "file_size",
        "filename",
        "internal_attr",
    ],
)
def test_stored_archive_equivalent(
    zip_archive: Path, stored_archive: Path, attr: str
) -> None:
    with ZipFile(zip_archive) as orig_zf, ZipFile(stored_archive) as stored_zf:
        for orig, stored in zip_longest(orig_zf.infolist(), stored_zf.infolist()):
            assert getattr(orig, attr) == getattr(stored, attr)
