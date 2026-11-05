# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Failure and integrity checks using temporary clients only."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'installer/linux'))
import install as b

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.client=Path(self.tmp.name)
        (self.client/'HytaleClient').write_bytes(b'fixture')
        (self.client/'libSDL3.so').write_bytes(b'original SDL fixture')
        self.payload=b.ROOT/'build/libSDL3.so'
    def snapshot(self):
        return {str(p.relative_to(self.client)):p.read_bytes() for p in self.client.rglob('*') if p.is_file()}
    def test_update_restore_and_settings(self):
        b.perform(self.client,self.payload)
        settings=self.client/'.clearview/settings';settings.write_text('0.21 0.34 0.55\n')
        self.assertEqual(b.perform(self.client,self.payload)['operation'],'update')
        self.assertEqual(settings.read_text(),'0.21 0.34 0.55\n')
        b.perform(self.client,uninstall=True)
        self.assertEqual((self.client/'libSDL3.so').read_bytes(),b'original SDL fixture')
        self.assertEqual(settings.read_text(),'0.21 0.34 0.55\n')
    def test_rollback_after_replacement(self):
        before=self.snapshot(); original=b.atomic_write; failed=False
        def fail_once(path,data,permissions=0o644):
            nonlocal failed
            original(path,data,permissions)
            if path.name=='libSDL3.so' and not failed:
                failed=True;raise OSError('injected write failure')
        with patch.object(b,'atomic_write',fail_once):
            with self.assertRaisesRegex(b.InstallError,'restaurados'):b.perform(self.client,self.payload)
        self.assertEqual(self.snapshot(),before)
    def test_tampered_backup_refused(self):
        b.perform(self.client,self.payload)
        (self.client/'libSDL3.clearview-original.so').write_bytes(b'bad')
        before=self.snapshot()
        with self.assertRaises(b.InstallError):b.perform(self.client,uninstall=True)
        self.assertEqual(self.snapshot(),before)
    def test_lock(self):
        with b.locked(self.client):
            with self.assertRaisesRegex(b.InstallError,'Outra operação'):b.perform(self.client,self.payload)
    def test_symlink_refused(self):
        (self.client/'.clearview').symlink_to(self.client,target_is_directory=True)
        with self.assertRaises(b.InstallError):b.perform(self.client,self.payload)
    def test_running_refused(self):
        before=self.snapshot()
        with patch.object(b,'stopped',side_effect=b.InstallError('running')):
            with self.assertRaises(b.InstallError):b.perform(self.client,self.payload)
        self.assertEqual(self.snapshot(),before)
    def test_package_refused(self):
        bad=self.client/'bad.so';bad.write_bytes(b'bad')
        before=self.snapshot()
        with self.assertRaises(b.InstallError):b.perform(self.client,bad)
        self.assertEqual(self.snapshot(),before)

if __name__=='__main__':unittest.main()
