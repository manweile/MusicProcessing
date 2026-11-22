import os
import shutil
import tempfile
import time
import unittest
from unittest.mock import patch

import wx

from tests import (
    TEST_M4A_EAGLES,
    TEST_MP3_ABBA,
    TEST_MP3_GENESIS,
    TEST_MP3_NO_METADATA,
    TEST_WMA_CCR,
)
from src.core.constants import CSV_DIR, CSV_EXT
from src.gui.wx_app import MainFrame
from src.models.audio_info.audio_art import AudioArt
from src.models.audio_info.audio_metadata import AudioMetadata
from src.models.audio_info.audio_playlist import AudioPlaylist
from src.models.audio_info.audio_utilities import AudioUtilities
from src.models.audio_normalize.audio_normalization import AudioNormalization
from src.models.dir_processing.directory_processing import DirectoryProcessing


class TestAddAlbumFoldersGui(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = wx.App(False)
        cls.prepped_src_file_paths = [
            TEST_M4A_EAGLES,
            TEST_MP3_ABBA,
            TEST_MP3_GENESIS,
            TEST_MP3_NO_METADATA,
            TEST_WMA_CCR,
        ]

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory(prefix="musicprocessing-gui-")
        self.addCleanup(temp_dir.cleanup)

        self.prepped = os.path.join(temp_dir.name, "PreppedMusic")
        self.generated = os.path.join(temp_dir.name, "generated")
        os.makedirs(os.path.join(self.generated, CSV_DIR), exist_ok=True)

        generated_path_patcher = patch(
            "src.models.dir_processing.directory_processing.GENERATED_PATH",
            self.generated,
        )
        generated_path_patcher.start()
        self.addCleanup(generated_path_patcher.stop)

        for source in self.prepped_src_file_paths:
            artist = os.path.basename(os.path.dirname(source))
            artist_dir = os.path.join(self.prepped, artist)
            os.makedirs(artist_dir, exist_ok=True)
            shutil.copy2(source, os.path.join(artist_dir, os.path.basename(source)))

        self.frame = MainFrame(
            None,
            art=AudioArt(),
            directory=DirectoryProcessing(),
            metadata=AudioMetadata(),
            normalization=AudioNormalization(),
            utilities=AudioUtilities(),
            playlist=AudioPlaylist(),
        )
        self.frame.Show()
        wx.YieldIfNeeded()
        self.addCleanup(self._destroy_frame)

    def _destroy_frame(self):
        if self.frame:
            self.frame.Destroy()
            wx.YieldIfNeeded()

    def _wait_until(self, predicate, timeout=10):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            wx.YieldIfNeeded()
            if predicate():
                return
            time.sleep(0.01)

        self.fail(f"Condition was not met within {timeout} seconds")

    def test_add_album_folders_happy_path(self):
        path_control = self.frame.FindWindowByName("addAlbumsWalkTld")
        add_button = self.frame.FindWindowByName("addAlbumsWalk")

        self.assertIsNotNone(path_control)
        self.assertIsNotNone(add_button)

        path_control.SetValue(self.prepped)
        wx.PostEvent(
            add_button,
            wx.CommandEvent(wx.EVT_BUTTON.typeId, wx.ID_ANY),
        )

        self._wait_until(
            lambda: "create_album_dirs completed." in self.frame.mainLog.GetValue()
        )

        expected_moves = [
            ("The Eagles", "Desperado", "The Eagles-Desperado.m4a"),
            ("Abba", "Waterloo", "ABBA-Waterloo.mp3"),
            (
                "Creedence Clearwater Revival",
                "Chronicle, Vol. 1",
                "Creedence Clearwater Revival-Fortun ate Son.wma",
            ),
            ("Genesis", "In Too Deep - I'd Rather Be You", "Genesis-In Too Deep.mp3"),
        ]

        for artist, album, filename in expected_moves:
            artist_dir = os.path.join(self.prepped, artist)
            album_file = os.path.join(artist_dir, album, filename)
            original_file = os.path.join(artist_dir, filename)

            self.assertTrue(os.path.isfile(album_file), album_file)
            self.assertFalse(os.path.exists(original_file), original_file)

        no_metadata_dir = os.path.join(self.prepped, "NoMetadata")
        self.assertTrue(
            os.path.isfile(os.path.join(no_metadata_dir, "No_tag_Crush-Live.mp3"))
        )
        self.assertEqual(
            [
                name
                for name in os.listdir(no_metadata_dir)
                if os.path.isdir(os.path.join(no_metadata_dir, name))
            ],
            [],
        )

        report_path = os.path.join(
            self.generated,
            CSV_DIR,
            "create_album_dirs" + CSV_EXT,
        )
        self.assertTrue(os.path.isfile(report_path))


if __name__ == "__main__":
    unittest.main()