#!/usr/bin/env python3
"""Integration tests: Python + Pillow + ffmpeg/ffprobe, no Apple frameworks."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from pair_live_photo import pair, verify_pair
from package_live_photo import package


class PortableLivePhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.video = cls.root / 'motion.mp4'
        cls.photo = cls.root / 'cover.jpg'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=160x120:rate=30:duration=2', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.video)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(cls.video), '-frames:v', '1', str(cls.photo)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_frame_positions_and_package_without_photokit(self):
        for i, time in enumerate((0, 1, 59/30)):
            with self.subTest(time=time):
                output = self.root / f'pair-{i}'
                manifest = pair(self.photo, self.video, output, time, 30)
                self.assertEqual(manifest['localPHLivePhotoLoad'], 'not_available')
                self.assertAlmostEqual(verify_pair(output, manifest).still_time, time, places=4)
                receipt = package(output, self.root/f'item-{i}.pvt')
                self.assertTrue(receipt['resourcesUnchanged'])
                self.assertTrue(package(output, self.root/f'item-{i}.pvt')['reused'])

    def test_invalid_times_and_fps(self):
        for time, fps in ((-1, 30), (2, 30), (float('nan'), 30), (0.01, 30), (1, 24), (1, 0)):
            with self.subTest(time=time, fps=fps), self.assertRaises(ValueError):
                pair(self.photo, self.video, self.root/'invalid', time, fps)
        self.assertFalse((self.root/'invalid').exists())

    def test_tampering_and_failed_load_block_package(self):
        output = self.root / 'tamper'
        manifest = pair(self.photo, self.video, output, 1, 30)
        manifest['localPHLivePhotoLoad'] = 'failed'
        (output/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            package(output, self.root/'failed.pvt')
        manifest['localPHLivePhotoLoad'] = 'not_available'
        (output/'manifest.json').write_text(json.dumps(manifest))
        with (output/'live.mov').open('ab') as f:
            f.write(b'corruption')
        with self.assertRaises(ValueError):
            package(output, self.root/'corrupt.pvt')

    def test_input_and_output_protection(self):
        existing = self.root/'existing'
        existing.mkdir()
        sentinel = existing/'keep.txt'
        sentinel.write_text('keep')
        with self.assertRaises(ValueError):
            pair(self.photo, self.video, existing, 1, 30)
        self.assertEqual(sentinel.read_text(), 'keep')
        audio = self.root/'audio.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(self.video), '-f', 'lavfi', '-i', 'sine=duration=2', '-c:v', 'copy', '-c:a', 'aac', '-shortest', str(audio)], check=True)
        with self.assertRaisesRegex(ValueError, 'audio'):
            pair(self.photo, audio, self.root/'audio-pair', 1, 30)


if __name__ == '__main__':
    unittest.main()
