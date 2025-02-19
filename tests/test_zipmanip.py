# ruff: noqa: TRY003, EM101

import io
from pathlib import Path

import pytest

from zipmanip import _atomic_write, _buffer_input, _buffer_output, is_seekable


class _NonseekableBytesIO(io.BytesIO):
    def seek(self, offset: int, whence: int = 0, /) -> int:  # noqa: ARG002
        raise OSError("Not seekable")

    def seekable(self) -> bool:
        return False

    def tell(self) -> int:
        raise OSError("Not seekable")


def test_is_seekable_true() -> None:
    assert is_seekable(io.BytesIO())


def test_is_seekable_false() -> None:
    assert not is_seekable(_NonseekableBytesIO())


def test_buffer_input() -> None:
    fp = _NonseekableBytesIO(b"test text")
    with _buffer_input(fp) as sfp:
        assert sfp.read() == b"test text"
        sfp.seek(5)
        assert sfp.read() == b"text"


def test_buffer_output() -> None:
    fp = _NonseekableBytesIO()
    with _buffer_output(fp) as sfp:
        sfp.write(b"one")
        sfp.seek(0)
        sfp.write(b"two")
    assert fp.getvalue() == b"two"


def test_atomic_write(tmp_path: Path) -> None:
    target = tmp_path / "test.txt"
    target.write_bytes(b"content")
    with open(target, "rb") as ifp, _atomic_write(target) as ofp:
        ofp.write(b"X")
        ofp.write(ifp.read())
        ofp.write(b"Y")
    assert target.read_bytes() == b"XcontentY"

def test_atomic_write_exc(tmp_path: Path) -> None:
    target = tmp_path / "test.txt"
    target.write_bytes(b"content")
    with pytest.raises(RuntimeError):
        with open(target, "rb") as ifp, _atomic_write(target) as ofp:
            ofp.write(b"X")
            ofp.write(ifp.read())
            ofp.write(b"Y")
            raise RuntimeError
    assert target.read_bytes() == b"content"
