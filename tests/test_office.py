# Copyright (C) 2017 Jurriaan Bremer.
# This file is part of SFlock - http://www.sflock.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import pytest

from sflock.abstracts import File
from sflock.main import unpack
from sflock.unpack import OfficeFile

def f(filename):
    return File.from_path("tests/files/%s" % filename)

@pytest.mark.skipif("sys.platform != 'linux2'")
class TestOfficeFile(object):
    def test_office_plain(self):
        z = OfficeFile(f("maldoc.xls"))
        assert z.handles() is True
        assert not z.unpack()
        # Don't test z.f.selected / z.f.preview here as that logic isn't
        # performed by OfficeFile(), but rather the SFlock core.

    def test_office_plain2(self):
        f = unpack("tests/files/maldoc.xls")
        assert f.selected is True
        assert f.preview is False

    @pytest.mark.xfail
    def test_office_pw_failure(self):
        z = OfficeFile(f("encrypted1.docx"))
        assert z.handles() is True
        assert not z.unpack()
        # TODO Failure to decrypt should also unselect the file.
        assert z.f.selected is False
        assert z.f.preview is False

    def test_office_pw_success(self):
        z = OfficeFile(f("encrypted1.docx"))
        assert z.handles() is True
        d, = z.unpack("Password1234_")
        assert z.f.selected is False
        assert z.f.preview is True
        assert d.magic == "Microsoft Word 2007+"

@pytest.mark.skipif("sys.platform == 'linux2'")
def test_no_pycrypto():
    z = OfficeFile(f("encrypted1.docx"))
    assert z.handles() is True
    z.unpack("Password1234_")
    assert z.f.mode == "failed"
    assert "To decrypt" in z.f.error
