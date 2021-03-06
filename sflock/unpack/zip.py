# Copyright (C) 2015-2017 Jurriaan Bremer.
# This file is part of SFlock - http://www.sflock.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

import zipfile
import zlib

from sflock.abstracts import File, Unpacker
from sflock.exception import UnpackException

class ZipFile(Unpacker):
    name = "zipfile"
    exts = ".zip"
    magic = "Zip archive data"

    def supported(self):
        return True

    def handles(self):
        if super(ZipFile, self).handles():
            return True
        if self.f.stream.read(2) == "PK":
            return True
        return False

    def decrypt(self, password, archive, entry):
        try:
            archive.setpassword(password)
            return File(
                relapath=entry.filename,
                contents=archive.read(entry),
                password=password
            )
        except (RuntimeError, zipfile.BadZipfile, zlib.error) as e:
            msg = e.message or e.args[0]
            if "Bad password" in msg:
                return
            if "Bad CRC-32" in msg:
                return
            if "password required" in msg:
                return
            if "Truncated file header" in msg:
                return
            if "invalid distance too far back" in msg:
                return

            raise UnpackException("Unknown zipfile error: %s" % e)

    def unpack(self, password=None, duplicates=None):
        try:
            archive = zipfile.ZipFile(self.f.stream)
        except (zipfile.BadZipfile, IOError) as e:
            self.f.mode = "failed"
            self.f.error = e
            return []

        entries = []
        for entry in archive.infolist():
            if entry.filename.endswith("/"):
                continue

            f = self.bruteforce(password, archive, entry)
            entries.append(f or File(
                filename=entry.filename,
                mode="failed",
                description="Error decrypting file"
            ))

        return self.process(entries, duplicates)
