# Copyright (C) 2026 vertexiom
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of Hytale ClearView.
# Hytale ClearView is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See LICENSE for details.
"""Demo-state regression checks; no GTK display or game installation required."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer/linux/gui'))
from model import Demo, NATIVE, FLATPAK

class DemoTests(unittest.TestCase):
    def test_block_install_and_remove_without_target_or_with_running_game(self):
        for scenario in ('missing','multiple','running'):
            for operation in ('install','remove'):
                s=Demo();s.reset(scenario)
                with self.assertRaises(ValueError):s.begin(operation)

    def test_success_requires_all_steps(self):
        for operation,end in [('install','complete'),('remove','removed')]:
            s=Demo();s.reset('normal');token=s.begin(operation)
            for _ in range(2):
                s.advance(token);self.assertEqual(s.screen,'progress')
            s.advance(token);self.assertEqual(s.screen,end)

    def test_failure_phase_and_retry_require_recovery(self):
        for scenario,phase in [('conflict',0),('graphics',1),('copy',2)]:
            s=Demo();s.reset(scenario)
            for attempt in (1,2):
                token=s.begin('install')
                for _ in range(phase+1):s.advance(token)
                self.assertEqual((s.screen,s.stage,s.attempt),('error',phase,attempt))
            s.recover();token=s.begin('install')
            for _ in range(3):s.advance(token)
            self.assertEqual(s.screen,'complete')

    def test_reset_invalidates_inflight_callbacks(self):
        s=Demo();token=s.begin('install');s.reset('normal')
        self.assertFalse(s.advance(token));self.assertEqual(s.screen,'welcome')
        new=s.begin('install');self.assertFalse(s.advance(token))
        self.assertEqual(s.stage,0);self.assertTrue(s.advance(new))

    def test_multiple_selection_and_recovery(self):
        s=Demo();s.reset('multiple');s.path=FLATPAK;self.assertTrue(s.ready)
        s.reset('running');s.recover();self.assertTrue(s.ready)
        s.reset('missing');s.recover();self.assertEqual(s.path,NATIVE)

if __name__=='__main__':unittest.main()
